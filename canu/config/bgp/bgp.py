"""CANU commands that configure BGP."""
import ipaddress
import json
import os

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import requests


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option("--csi-folder", help="Directory containing the CSI json file")
@click.option(
    "--auth-token",
    envvar="SLS_TOKEN",
    help="Token for SLS authentication",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@optgroup.group(
    "Network cabling IPv4 input sources",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--ips",
    help="Comma separated list of IPv4 addresses of switches",
    type=Ipv4AddressListParamType(),
)
@optgroup.option(
    "--ips-file",
    help="File with one IPv4 address per line",
    type=click.File("r"),
)
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--asn",
    help="ASN",
    default="65533",
    show_default=True,
)
@click.option("--verbose", is_flag=True, help="Verbose mode")
@click.pass_context
def bgp(
    ctx,
    csi_folder,
    auth_token,
    sls_address,
    ips,
    ips_file,
    username,
    password,
    asn,
    verbose,
):
    """Configure BGP for a pair of switches.

    This script updates the BGP neighbors on the management switches to match the IPs of what CSI generated.
       - It Queries SLS for network and NCN data.


    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        csi_folder: Directory containing the CSI json file
        auth_token: Token for SLS authentication
        sls_address: The address of SLS
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        asn: Switch ASN
        verbose: Bool indicating verbose output
    """
    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    errors = []
    ips_length = len(ips)

    # Get SLS config
    token = os.environ.get("SLS_TOKEN")

    # Token file takes precedence over the environmental variable
    if auth_token != token:
        try:
            with open(auth_token) as f:
                data = json.load(f)
                token = data["access_token"]

        except Exception:
            click.secho(
                "Invalid token file, generate another token or try again.",
                fg="white",
                bg="red",
            )
            return

    # SLS
    url = "https://" + sls_address + "/apis/sls/v1/networks"
    try:
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            verify=False,
        )
        response.raise_for_status()

        sls_json = response.json()

    except requests.exceptions.ConnectionError:
        return click.secho(
            f"Error connecting to SLS {sls_address}, check the address or pass in a new address using --sls-address.",
            fg="white",
            bg="red",
        )
    except requests.exceptions.HTTPError:
        bad_token_reason = (
            "environmental variable 'SLS_TOKEN' is correct."
            if auth_token == token
            else "token is valid, or generate a new one."
        )
        return click.secho(
            f"Error connecting SLS {sls_address}, check that the {bad_token_reason}",
            fg="white",
            bg="red",
        )

    # Parse SLS
    prefix, ncn = parse_sls(sls_json)

    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                ip = str(ip)
                session = requests.Session()
                # Login
                try:
                    login = session.post(
                        f"https://{ip}/rest/v10.04/login",
                        data=credentials,
                        verify=False,
                    )
                    login.raise_for_status()

                except requests.exceptions.HTTPError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, check that this IP is an Aruba switch, or check the "
                            + "username or password.",
                        ]
                    )

                except requests.exceptions.ConnectionError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, check the IP address and try again.",
                        ]
                    )

                except requests.exceptions.RequestException:  # pragma: no cover
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}.",
                        ]
                    )

                # Remove: BGP, Prefix Lists, Route Maps
                remove_config(ip, session, asn)

                # Add Prefix Lists
                add_prefix_list(ip, session, prefix)

                # Create Route Maps
                create_route_maps(ip, session, ncn)

                # Add BGP and Router ID
                add_bgp_asn_router_id(ip, session, asn)

                # Update BGP Neighbors
                update_bgp_neighbors(ip, ips, session, asn, ncn)

                # Write Memory
                session.put(
                    f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
                    verify=False,
                )

                # Logout
                session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    dash = "-" * 50

    click.echo("\n")
    click.secho("BGP Updated", fg="bright_white")
    click.echo(dash)
    for ip in ips:
        click.echo(ip)

    if len(errors) > 0:
        click.echo("\n")
        click.secho("Errors", fg="red")
        click.echo(dash)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]))
    return


def parse_sls(sls_json):
    """Parse the JSON from SLS `/networks` API.

    Args:
        sls_json: JSON from the SLS `/networks` API

    Returns:
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
    """
    ncn_names = []
    ncn_nmn_ips = []
    ncn_can_ips = []
    ncn_hmn_ips = []

    for sls_network in sls_json:
        for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
            full_name = subnets["FullName"]

            # get CAN prefix
            if "CAN Bootstrap DHCP Subnet" in full_name:
                CAN_prefix = subnets["CIDR"]

                # CAN NCN IPs
                ncn_can_ips = [
                    ip.get("IPAddress", None)
                    for ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ip.get("Name", "")
                ]

            # get HMN prefix
            if "HMN MetalLB" in full_name:
                HMN_prefix = subnets["CIDR"]

            # get NMN prefix
            if "NMN MetalLB" in full_name:
                NMN_prefix = subnets["CIDR"]

                # get TFTP prefix
                for ip in subnets["IPReservations"]:
                    if "cray-tftp" in ip["Name"]:
                        TFTP_prefix = ip["IPAddress"] + "/32"

            # NCN Names
            if "NMN Bootstrap DHCP Subnet" in full_name:
                ncn_names = [
                    ip.get("Name", None)
                    for ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ip.get("Name", "")
                ]

                # NCN NMN IPs
                ncn_nmn_ips = [
                    ip.get("IPAddress", None)
                    for ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ip.get("Name", "")
                ]

            # NMN NCN IPs
            if "HMN Bootstrap DHCP Subnet" in full_name:
                ncn_hmn_ips = [
                    ip.get("IPAddress", None)
                    for ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ip.get("Name", "")
                ]

    prefix = {
        "can": CAN_prefix,
        "hmn": HMN_prefix,
        "nmn": NMN_prefix,
        "tftp": TFTP_prefix,
    }
    ncn = {
        "names": ncn_names,
        "can": ncn_can_ips,
        "nmn": ncn_nmn_ips,
        "hmn": ncn_hmn_ips,
    }

    return prefix, ncn


def remove_config(ip, session, asn):
    """Remove config for BGP, prefix lists, and route maps.

    Args:
        ip: Switch IP
        session: Switch login session
        asn: Switch ASN
    """
    # remove bgp config
    session.delete(f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}")

    # remove prefix lists
    session.delete(f"https://{ip}/rest/v10.04/system/prefix_lists/*")

    # remove route maps
    session.delete(f"https://{ip}/rest/v10.04/system/route_maps/*")


def add_prefix_list(ip, session, prefix):
    """Add prefix lists to a switch.

    Args:
        ip: Switch IP
        session: Switch login session
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
    """
    CAN_prefix = prefix["can"]
    HMN_prefix = prefix["hmn"]
    NMN_prefix = prefix["nmn"]
    TFTP_prefix = prefix["tftp"]

    prefix_list_template = {
        "action": "permit",
        "ge": 24,
        "le": 0,
        "preference": 10,
        "prefix": "",
    }

    # "pl-can"
    prefix_list_pl_can = {"address_family": "ipv4", "name": "pl-can"}
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists",
        json=prefix_list_pl_can,
        verify=False,
    )
    prefix_list_template["prefix"] = CAN_prefix
    prefix_list_template["preference"] = 10
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists/pl-can/prefix_list_entries",
        json=prefix_list_template,
        verify=False,
    )

    # "pl-hmn"
    prefix_list_pl_hmn = {"address_family": "ipv4", "name": "pl-hmn"}
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists",
        json=prefix_list_pl_hmn,
        verify=False,
    )
    prefix_list_template["prefix"] = HMN_prefix
    prefix_list_template["preference"] = 20
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists/pl-hmn/prefix_list_entries",
        json=prefix_list_template,
        verify=False,
    )

    # "pl-nmn"
    prefix_list_pl_nmn = {"address_family": "ipv4", "name": "pl-nmn"}
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists",
        json=prefix_list_pl_nmn,
        verify=False,
    )
    prefix_list_template["prefix"] = NMN_prefix
    prefix_list_template["preference"] = 30
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists/pl-nmn/prefix_list_entries",
        json=prefix_list_template,
        verify=False,
    )

    # "tftp"
    prefix_list_tftp = {"address_family": "ipv4", "name": "tftp"}
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists",
        json=prefix_list_tftp,
        verify=False,
    )
    prefix_list_template["prefix"] = TFTP_prefix
    prefix_list_template["ge"] = 32
    prefix_list_template["le"] = 32
    prefix_list_template["preference"] = 10
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists/tftp/prefix_list_entries",
        json=prefix_list_template,
        verify=False,
    )


def create_route_maps(ip, session, ncn):
    """Create route maps for a switch.

    Args:
        ip: Switch IP
        session: Switch login session
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
    """
    ncn_names = ncn["names"]
    ncn_can_ips = ncn["can"]
    ncn_nmn_ips = ncn["nmn"]
    ncn_hmn_ips = ncn["hmn"]

    # tftp
    route_map_entry_tftp = {
        "action": "permit",
        "match_ipv4_prefix_list": {"tftp": "/rest/v10.04/system/prefix_lists/tftp"},
        "preference": 10,
        "set": {"local_preference": ""},
        "match": {"ipv4_next_hop_address": ""},
    }

    for name in ncn_names:
        route_map = {"name": name}
        session.post(
            f"https://{ip}/rest/v10.04/system/route_maps", json=route_map, verify=False
        )

        route_map_entry_tftp["preference"] = 10
        route_map_entry_tftp["set"]["local_preference"] = 1000

        for nmn_ip in ncn_nmn_ips[:3]:
            route_map_entry_tftp["match"]["ipv4_next_hop_address"] = nmn_ip
            session.post(
                f"https://{ip}/rest/v10.04/system/route_maps/{name}/route_map_entries",
                json=route_map_entry_tftp,
                verify=False,
            )
            route_map_entry_tftp["preference"] += 10
            route_map_entry_tftp["set"]["local_preference"] += 100

    # pl-can
    route_map_entry_can = {
        "action": "permit",
        "match_ipv4_prefix_list": {"pl-can": "/rest/v10.04/system/prefix_lists/pl-can"},
        "preference": 40,
        "set": {"ipv4_next_hop_address": ""},
    }
    add_route_entry(ip, session, ncn_can_ips, ncn_names, route_map_entry_can)

    # pl-hmn
    route_map_entry_hmn = {
        "action": "permit",
        "match_ipv4_prefix_list": {"pl-hmn": "/rest/v10.04/system/prefix_lists/pl-hmn"},
        "preference": 30,
        "set": {"ipv4_next_hop_address": ""},
    }
    add_route_entry(ip, session, ncn_hmn_ips, ncn_names, route_map_entry_hmn)

    # pl-nmn
    route_map_entry_nmn = {
        "action": "permit",
        "match_ipv4_prefix_list": {"pl-can": "/rest/v10.04/system/prefix_lists/pl-nmn"},
        "preference": 20,
        "set": {"ipv4_next_hop_address": ""},
    }
    add_route_entry(ip, session, ncn_nmn_ips, ncn_names, route_map_entry_nmn)

    return


def add_route_entry(ip, session, ips, ncn_names, route_map_entry):
    """Add route entries to a switch.

    Args:
        ip: Switch IP
        session: Switch login session
        ips: IPs of the switches
        ncn_names: NCN Names
        route_map_entry: Route map to be added
    """
    w001_response = session.get(
        f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
        verify=False,
    )
    route_map1 = w001_response.json()
    pref = int(sorted(route_map1.keys())[-1])

    for ncn, name in zip(ips, ncn_names):
        route_map_entry["set"]["ipv4_next_hop_address"] = ncn
        route_map_entry["preference"] = pref + 10
        session.post(
            f"https://{ip}/rest/v10.04/system/route_maps/{name}/route_map_entries",
            json=route_map_entry,
            verify=False,
        )


def add_bgp_asn_router_id(ip, session, asn):
    """Add BGP ASN and router id.

    Args:
        ip: Switch IP
        session: Switch login session
        asn: Switch ASN
    """
    bgp_data = {"asn": int(asn), "router_id": ip, "maximum_paths": 8, "ibgp_distance": 70}
    session.post(
        f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers",
        json=bgp_data,
        verify=False,
    )


def update_bgp_neighbors(ip, ips, session, asn, ncn):
    """Update BGP neighbors for a switch.

    Args:
        ip: Switch IP
        ips: IPs of the switches
        session: Switch login session
        asn: Switch ASN
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
    """
    ncn_names = ncn["names"]
    ncn_nmn_ips = ncn["nmn"]

    bgp_neighbor = {
        "ip_or_ifname_or_group_name": "",
        "remote_as": int(asn),
        "passive": True,
        "route_maps": {"ipv4-unicast": {"in": ""}},
        "shutdown": False,
        "activate": {"ipv4-unicast": True},
    }

    for ncn_ip, name in zip(ncn_nmn_ips, ncn_names):
        bgp_neighbor["ip_or_ifname_or_group_name"] = ncn_ip
        bgp_neighbor["route_maps"]["ipv4-unicast"]["in"] = (
            "/rest/v10.04/system/route_maps/" + name
        )
        session.post(
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
            json=bgp_neighbor,
            verify=False,
        )

    for x in ips:
        x = str(x)
        if x != ip:
            vsx_neighbor = dict(bgp_neighbor)
            vsx_neighbor["ip_or_ifname_or_group_name"] = x
            del vsx_neighbor["route_maps"]
            del vsx_neighbor["passive"]
            session.post(
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
                json=vsx_neighbor,
                verify=False,
            )
