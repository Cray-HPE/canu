# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""CANU commands that configure BGP."""
import ipaddress
import json
from os import environ

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import requests

from canu.utils.vendor import switch_vendor


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
)
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
    sls_file,
    auth_token,
    sls_address,
    ips,
    ips_file,
    username,
    password,
    asn,
    verbose,
):  # noqa:WPS211
    """Configure BGP for a pair of switches.

    This command will remove previous configuration (BGP, Prefix Lists, Route Maps), then add prefix lists, create
    route maps, and update BGP neighbors, then write it all to the switch memory.

    The network and NCN data can be read from one of two sources, the SLS API, or using CSI.

    To access SLS, a token must be passed in using the `--auth-token` flag.
    Tokens are typically stored in ~./config/cray/tokens/
    Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

    To initialize using any SLS data, pass in the file containing SLS JSON data (sometimes sls_input_file.json) the --sls-file flag

    If used, CSI-generated sls_file.json file is generally stored in one of two places
    depending on how far the system is in the install process.


        - Early in the install process, when running off of the LiveCD the
        sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

        - Later in the install process, the sls_input_file.json file is
        generally in `/mnt/pitdata/prep/SYSTEMNAME/`

    To print extra details (prefixes, NCN names, IPs), add the `--verbose` flag

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        sls_file: Directory containing the CSI json file
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
    if ips_length != 2:
        click.secho(
            "Incorrect number of IP addresses entered, there should be exactly 2 IPs.",
            fg="white",
            bg="red",
        )
        return

    # Parse SLS input file.
    if sls_file:
        try:
            input_json = json.load(sls_file)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho(
                f"The file {sls_file.name} is not valid JSON.",
                fg="red",
            )
            return

        # Format the input to be like the SLS JSON
        sls_json = [
            network[x] for network in [input_json.get("Networks", {})] for x in network
        ]

    else:
        # Get SLS config
        token = environ.get("SLS_TOKEN")

        # Token file takes precedence over the environmental variable
        if auth_token != token:
            try:
                with open(auth_token) as auth_f:
                    auth_data = json.load(auth_f)
                    token = auth_data["access_token"]

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
                try:
                    config_bgp(ip, credentials, prefix, ncn, asn, ips)

                except requests.exceptions.HTTPError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, check the IP, username, or password.",
                        ],
                    )
                    continue

                except requests.exceptions.ConnectionError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, check the IP address and try again.",
                        ],
                    )
                    continue

                except requests.exceptions.RequestException:  # pragma: no cover
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}.",
                        ],
                    )
                    continue

    dash = "-" * 50

    click.secho("\nBGP Updated", fg="bright_white")
    click.echo(dash)
    for bgp_ip in ips:
        click.echo(bgp_ip)

    if verbose:
        click.secho("\nDetails", fg="bright_white")
        click.echo(dash)
        click.echo(f"CAN Prefix: {prefix['can']}")
        click.echo(f"HMN Prefix: {prefix['hmn']}")
        click.echo(f"NMN Prefix: {prefix['nmn']}")
        click.echo(f"TFTP Prefix: {prefix['tftp']}")
        click.echo(f"NCN Names: {ncn['names']}")
        click.echo(f"NCN CAN IPs: {ncn['can']}")
        click.echo(f"NCN NMN IPs: {ncn['nmn']}")
        click.echo(f"NCN HMN IPs: {ncn['hmn']}")

    if len(errors) > 0:
        click.secho("\nErrors", fg="red")
        click.echo(dash)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]))


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
                can_prefix = subnets["CIDR"]

                # CAN NCN IPs
                ncn_can_ips = [
                    ip.get("IPAddress", None)
                    for ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ip.get("Name", "")
                ]

            # get HMN prefix
            if "HMN MetalLB" in full_name:
                hmn_prefix = subnets["CIDR"]

            # get NMN prefix
            if "NMN MetalLB" in full_name:
                nmn_prefix = subnets["CIDR"]

                # get TFTP prefix
                for ip in subnets["IPReservations"]:
                    if "cray-tftp" in ip["Name"]:
                        tftp_prefix = ip["IPAddress"] + "/32"

            # NCN Names
            if "NMN Bootstrap DHCP Subnet" in full_name:
                ncn_names = [
                    ncn_name_ip.get("Name", None)
                    for ncn_name_ip in subnets.get("IPReservations", {})
                    if "ncn-w" in ncn_name_ip.get("Name", "")
                ]

                # NCN NMN IPs
                ncn_nmn_ips = [
                    nmn_ip.get("IPAddress", None)
                    for nmn_ip in subnets.get("IPReservations", {})
                    if "ncn-w" in nmn_ip.get("Name", "")
                ]

            # NMN NCN IPs
            if "HMN Bootstrap DHCP Subnet" in full_name:
                ncn_hmn_ips = [
                    hmn_ip.get("IPAddress", None)
                    for hmn_ip in subnets.get("IPReservations", {})
                    if "ncn-w" in hmn_ip.get("Name", "")
                ]

    prefix = {
        "can": can_prefix,
        "hmn": hmn_prefix,
        "nmn": nmn_prefix,
        "tftp": tftp_prefix,
    }
    ncn = {
        "names": ncn_names,
        "can": ncn_can_ips,
        "nmn": ncn_nmn_ips,
        "hmn": ncn_hmn_ips,
    }

    return prefix, ncn


def config_bgp(ip, credentials, prefix, ncn, asn, ips):
    """Configure BGP for Shasta switches.

    Args:
        ip: Switch IP
        credentials: Dictionary with username and password of the switch
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
        asn: Switch ASN
        ips: List of switch IPs
    """
    try:
        vendor = switch_vendor(ip, credentials, return_error=True)

        if vendor is None:
            click.secho(
                "Could not determine the vendor of the switch",
                fg="white",
                bg="red",
            )

        elif vendor == "aruba":
            config_bgp_aruba(
                ip,
                credentials,
                prefix,
                ncn,
                asn,
                ips,
            )
        elif vendor == "dell":
            click.secho(
                "BGP peering against Dell switch not allowed by CSM architecture.",
                fg="white",
                bg="red",
            )

        elif vendor == "mellanox":
            config_bgp_mellanox(
                ip,
                credentials,
                prefix,
                ncn,
                asn,
            )

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
    ) as error:
        raise error


def config_bgp_aruba(ip, credentials, prefix, ncn, asn, ips):
    """Configure BGP for an Aruba switch.

    Args:
        ip: Switch IP
        credentials: Dictionary with username and password of the switch
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
        asn: Switch ASN
        ips: List of switch IPs
    """
    session = requests.Session()
    # Login
    try:
        login = session.post(
            f"https://{ip}/rest/v10.04/login",
            data=credentials,
            verify=False,
        )
        login.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as error:
        raise error

    # Remove: BGP, Prefix Lists, Route Maps
    remove_config_aruba(ip, session, asn)

    # Add Prefix Lists
    add_prefix_list_aruba(ip, session, prefix)

    # Create Route Maps
    create_route_maps_aruba(ip, session, ncn)

    # Add BGP and Router ID
    add_bgp_asn_router_id_aruba(ip, session, asn)

    # Update BGP Neighbors
    update_bgp_neighbors_aruba(ip, ips, session, asn, ncn)

    # Write Memory
    session.put(
        f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
        verify=False,
    )

    # Logout
    session.post(f"https://{ip}/rest/v10.04/logout", verify=False)


def remove_config_aruba(ip, session, asn):
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


def add_prefix_list_aruba(ip, session, prefix):
    """Add prefix lists to a switch.

    Args:
        ip: Switch IP
        session: Switch login session
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
    """
    can_prefix = prefix["can"]
    hmn_prefix = prefix["hmn"]
    nmn_prefix = prefix["nmn"]
    tftp_prefix = prefix["tftp"]

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
    prefix_list_template["prefix"] = can_prefix
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
    prefix_list_template["prefix"] = hmn_prefix
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
    prefix_list_template["prefix"] = nmn_prefix
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
    prefix_list_template["prefix"] = tftp_prefix
    prefix_list_template["ge"] = 32
    prefix_list_template["le"] = 32
    prefix_list_template["preference"] = 10
    session.post(
        f"https://{ip}/rest/v10.04/system/prefix_lists/tftp/prefix_list_entries",
        json=prefix_list_template,
        verify=False,
    )


def create_route_maps_aruba(ip, session, ncn):
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
            f"https://{ip}/rest/v10.04/system/route_maps",
            json=route_map,
            verify=False,
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


def add_bgp_asn_router_id_aruba(ip, session, asn):
    """Add BGP ASN and router id.

    Args:
        ip: Switch IP
        session: Switch login session
        asn: Switch ASN
    """
    bgp_data = {
        "asn": int(asn),
        "router_id": ip,
        "maximum_paths": 8,
        "ibgp_distance": 70,
    }
    session.post(
        f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers",
        json=bgp_data,
        verify=False,
    )


def update_bgp_neighbors_aruba(ip, ips, session, asn, ncn):
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
            vsx_neighbor.pop("route_maps")
            vsx_neighbor.pop("passive")
            session.post(
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
                json=vsx_neighbor,
                verify=False,
            )


def config_bgp_mellanox(ip, credentials, prefix, ncn, asn):
    """Configure BGP for a Mellanox switch.

    Args:
        ip: Switch IP
        credentials: Dictionary with username and password of the switch
        prefix: Dict containing prefix for ("can", "hmn", "nmn", "tftp")
        ncn: Dict containing (NCN Names, NCN CAN IPs, NCN NMN IPs, NCN HMN IPs)
        asn: Switch ASN
    """
    can_prefix = prefix["can"]
    hmn_prefix = prefix["hmn"]
    nmn_prefix = prefix["nmn"]

    ncn_names = ncn["names"]
    ncn_can_ips = ncn["can"]
    ncn_hmn_ips = ncn["hmn"]
    ncn_nmn_ips = ncn["nmn"]

    login_url = (
        f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login"
    )

    # default url to post commands
    command_url = (
        login_url + "/admin/launch?script=rh&template=json-request&action=json-login"
    )

    session = requests.Session()
    # Login
    try:
        login = session.post(
            login_url,
            json=credentials,
            verify=False,
        )
        login.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as error:
        raise error

    # get route-map configuration
    route_map_response = session.post(
        url=command_url,
        json={"cmd": "show route-map"},
        verify=False,
    )

    # create command to delete previous route-map configuration.
    route_map_response_json = json.loads(route_map_response.text)
    cmd_no_route_map_list = [f"no router bgp {asn}"]

    for route in route_map_response_json["data"]:
        for key in route:
            new_route = f"no {key.split(',')[0]}"
            if new_route not in cmd_no_route_map_list:
                cmd_no_route_map_list.append(new_route)

    # posts NO route maps to the switch
    session.post(
        url=command_url,
        json={"commands": cmd_no_route_map_list},
        verify=False,
    )

    # create command to delete previous prefix list configuration.
    # these are hard coded, the API does not return prefix lists when called...
    # delete prefix lists
    get_prefix_list = [
        "no ip prefix-list pl-can",
        "no ip prefix-list pl-hmn",
        "no ip prefix-list pl-nmn",
    ]
    session.post(
        url=command_url,
        json={"commands": get_prefix_list},
        verify=False,
    )

    # define the switch prefix list commands
    cmd_list = [
        f"ip prefix-list pl-nmn seq 10 permit {nmn_prefix[:-3]} /24 ge 24",
        f"ip prefix-list pl-hmn seq 20 permit {hmn_prefix[:-3]} /24 ge 24",
        f"ip prefix-list pl-can seq 30 permit {can_prefix[:-3]} /24 ge 24",
    ]

    # create route_map commands
    for nmn_name, nmn_ip in zip(ncn_names, ncn_nmn_ips):
        cmd_list.append(f"route-map {nmn_name} permit 10 match ip address pl-nmn")
        cmd_list.append(f"route-map {nmn_name} permit 10 set ip next-hop {nmn_ip}")

    for hmn_name, hmn_ip in zip(ncn_names, ncn_hmn_ips):
        cmd_list.append(f"route-map {hmn_name} permit 20 match ip address pl-hmn")
        cmd_list.append(f"route-map {hmn_name} permit 20 set ip next-hop {hmn_ip}")

    for can_name, can_ip in zip(ncn_names, ncn_can_ips):
        cmd_list.append(f"route-map {can_name} permit 30 match ip address pl-can")
        cmd_list.append(f"route-map {can_name} permit 30 set ip next-hop {can_ip}")

    # BGP commands
    cmd_list.append(f"router bgp {asn} vrf default")
    cmd_list.append(f"router-id {ip} force")

    for ncn_ip, name in zip(ncn_nmn_ips, ncn_names):
        cmd_list.append(f"neighbor {ncn_ip} remote-as 65533")
        cmd_list.append(f"neighbor {ncn_ip} route-map {name}")
        cmd_list.append(f"neighbor {ncn_ip} transport connection-mode passive")

    cmd_list.append("maximum-paths ibgp 32")

    # post all the bgp configuration commands
    session.post(
        url=command_url,
        json={"commands": cmd_list},
        verify=False,
    )

    session.post(
        url=command_url,
        json={"cmd": "write memory"},
        verify=False,
    )
