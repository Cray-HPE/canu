"""CANU commands that validate the shcd."""
import ipaddress

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import natsort
import requests


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
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
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
    help="Shasta architecture",
    required=True,
    prompt="Architecture type",
)
@click.option("--verbose", is_flag=True, help="Verbose mode")
@click.pass_context
def bgp(ctx, ips, ips_file, username, password, asn, architecture, verbose):
    """Validate BGP neighbors..

    This command will check the BGP neighbors for the switch IP addresses entered. All of the neighbors of a switch
    must be 'Established', or the verification will fail.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        asn: Switch ASN
        architecture: Shasta architecture
        verbose: Bool indicating verbose output
    """
    if architecture.lower() == "full":
        architecture = "full"
    elif architecture.lower() == "tds":
        architecture = "tds"
    elif architecture.lower() == "v1":
        architecture = "network_v1"

    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    data = {}
    errors = []
    ips_length = len(ips)

    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )

                bgp_neighbors, switch_info = get_bgp_neighbors(ip, credentials, asn)
                if switch_info is None:
                    errors.append(
                        [
                            str(ip),
                            "Connection Error",
                        ]
                    )
                else:
                    data[ip] = {
                        "neighbors": bgp_neighbors,
                        "hostname": switch_info["hostname"],
                    }

    dash = "-" * 50

    for switch in data:
        bgp_neighbors = data[switch]["neighbors"]
        ip = switch
        hostname = data[switch]["hostname"]

        if verbose:
            click.echo(dash)
            click.secho(f"{hostname}", fg="bright_white")
            click.echo(dash)

        if len(bgp_neighbors) == 0:
            data[switch]["status"] = "SKIP"
            continue
        else:
            data[switch]["status"] = "PASS"
        for neighbor in bgp_neighbors:
            neighbor_status = bgp_neighbors[neighbor]["status"]["bgp_peer_state"]

            if neighbor_status != "Established":
                data[switch]["status"] = "FAIL"
                if verbose:
                    click.secho(
                        f"{hostname} ===> {neighbor}: {neighbor_status}",
                        fg="red",
                    )
            else:
                if verbose:
                    click.secho(f"{hostname} ===> {neighbor}: {neighbor_status}")

            if architecture == "tds":
                if "spine" not in str(hostname):
                    errors.append(
                        [
                            str(ip),
                            f"{hostname} not a spine switch, with TDS architecture BGP config only allowed with spine switches",
                        ]
                    )
            if architecture == "full":
                if "agg" not in str(hostname) and "leaf" not in str(hostname):
                    errors.append(
                        [
                            str(ip),
                            f"{hostname} not an agg or leaf switch, with Full architecture BGP config only allowed"
                            + "with agg and leaf switches",
                        ]
                    )

    click.echo("\n")
    click.secho("BGP Neighbors Established", fg="bright_white")
    click.echo(dash)

    for switch in data:

        bgp_neighbors = data[switch]["neighbors"]
        ip = switch
        hostname = data[switch]["hostname"]
        status = data[switch]["status"]

        color = ""
        if status == "PASS":
            color = "green"
        if status == "FAIL":
            color = "red"

        click.secho(
            f"{status} - IP: {ip} Hostname: {hostname}",
            fg=color,
        )

    if len(errors) > 0:
        errors = set(tuple(x) for x in errors)
        errors = natsort.natsorted(errors)
        click.echo("\n")
        click.secho("Errors", fg="red")
        click.echo(dash)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]))
    return


def get_bgp_neighbors(ip, credentials, asn):
    """Get BGP neighbors for a switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        asn: Switch ASN

    Returns:
        bgp_neighbors: A dict with switch neighbors
        switch_info: A dict with switch info
    """
    session = requests.Session()
    try:
        # Login
        login = session.post(
            f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
        )
        login.raise_for_status()

    except requests.exceptions.HTTPError:
        click.secho(
            f"Error connecting to switch {ip}, check that this IP is an Aruba switch, or check the username or password",
            fg="white",
            bg="red",
        )
        return None, None
    except requests.exceptions.ConnectionError:
        click.secho(
            f"Error connecting to switch {ip}, check the IP address and try again",
            fg="white",
            bg="red",
        )
        return None, None
    except requests.exceptions.RequestException:  # pragma: no cover
        click.secho(
            f"Error connecting to switch  {ip}.",
            fg="white",
            bg="red",
        )
        return None, None

    # Get neighbors
    try:
        bgp_neighbors_response = session.get(
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            verify=False,
        )
        bgp_neighbors_response.raise_for_status()

        bgp_neighbors = bgp_neighbors_response.json()

        switch_info_response = session.get(
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            verify=False,
        )
        switch_info_response.raise_for_status()

        switch_info = switch_info_response.json()

        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    except requests.exceptions.RequestException:  # pragma: no cover
        click.secho(
            f"Error getting BGP neighbors from switch {ip}",
            fg="white",
            bg="red",
        )
        return "FAIL", None

    return bgp_neighbors, switch_info
