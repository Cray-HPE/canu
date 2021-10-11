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
"""CANU commands that validate the network bgp."""
from collections import defaultdict
import ipaddress

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import natsort
from netmiko import ssh_exception
import requests

from canu.utils.vendor import switch_vendor


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

                bgp_neighbors, switch_info = get_bgp_neighbors(
                    str(ip),
                    credentials,
                    asn,
                )
                if switch_info is None:
                    errors.append(
                        [
                            str(ip),
                            "Connection Error",
                        ],
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
            click.secho(
                f"Switch: {switch_info['hostname']} ({switch_info['ip']})                       ",
                fg="bright_white",
            )
            click.secho(
                f"{switch_info['vendor'].capitalize()} {switch_info['platform_name']}",
                fg="bright_white",
            )
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
                        ],
                    )
            if architecture == "full":
                if "agg" not in str(hostname) and "leaf" not in str(hostname):
                    errors.append(
                        [
                            str(ip),
                            f"{hostname} not an agg or leaf switch, with Full architecture BGP config only allowed"
                            + "with agg and leaf switches",
                        ],
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
        errors = {tuple(x) for x in errors}
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
    return_error = True
    try:
        vendor = switch_vendor(ip, credentials, return_error)

        if vendor is None:
            return None, None
        elif vendor == "aruba":
            bgp_neighbors, switch_info = get_bgp_neighbors_aruba(ip, credentials, asn)
        elif vendor == "dell":
            # This function returns: {}, switch_info
            # There won't be any Dell switches with BGP neighbors
            bgp_neighbors, switch_info = get_bgp_neighbors_dell(ip, credentials)
        elif vendor == "mellanox":
            bgp_neighbors, switch_info = get_bgp_neighbors_mellanox(ip, credentials)

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
        ssh_exception.NetmikoTimeoutException,
        ssh_exception.NetmikoAuthenticationException,
    ) as error:
        exception_type = type(error).__name__
        click.secho(
            f"Error connecting to switch {ip}, {exception_type}.",
            fg="white",
            bg="red",
        )
        return None, None

    return bgp_neighbors, switch_info


def get_bgp_neighbors_aruba(ip, credentials, asn):
    """Get BGP neighbors for an Aruba switch.

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
            f"https://{ip}/rest/v10.04/login",
            data=credentials,
            verify=False,
        )
        login.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as err:
        exception_type = type(err).__name__

        if exception_type == "HTTPError":
            error_message = (
                f"Error connecting to switch {ip}, check the username or password"
            )
        elif exception_type == "ConnectionError":
            error_message = (
                f"Error connecting to switch {ip}, check the IP address and try again."
            )
        else:
            error_message = f"Error connecting to switch {ip}."

        click.secho(
            str(error_message),
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

        bgp_neighbors_aruba = bgp_neighbors_response.json()

        switch_info_response = session.get(
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            verify=False,
        )
        switch_info_response.raise_for_status()

        switch_info = switch_info_response.json()
        switch_info["ip"] = ip
        switch_info["vendor"] = "aruba"

        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    except requests.exceptions.RequestException:  # pragma: no cover
        click.secho(
            f"Error getting BGP neighbors from switch {ip}",
            fg="white",
            bg="red",
        )
        return "FAIL", None

    return bgp_neighbors_aruba, switch_info


def get_bgp_neighbors_dell(ip, credentials):
    """Get Dell switch info. Dell switches won't ever have BGP, so return 0 neighbors.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch

    Returns:
        bgp_neighbors: An empty dict
        switch_info: A dict with switch info

    Raises:
        Exception: Exception
    """
    session = requests.Session()
    try:
        auth = (credentials["username"], credentials["password"])
        url = f"https://{ip}/restconf/data/system-sw-state/sw-version"

        response = session.get(url, auth=auth, verify=False)
        response.raise_for_status()
        switch_info = response.json()
        platform_name = switch_info["dell-system-software:sw-version"]["sw-platform"]

        # GET hostname
        hostname_url = f"https://{ip}/restconf/data/dell-system:system/hostname"

        get_hostname = session.get(hostname_url, auth=auth, verify=False)
        get_hostname.raise_for_status()
        hostname = get_hostname.json()
        switch_info = {
            "ip_address": ip,
            "ip": ip,
            "hostname": hostname["dell-system:hostname"],
            "platform_name": platform_name,
            "vendor": "dell",
        }

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
    ) as connection_err:
        raise connection_err

    except Exception as error:  # pragma: no cover
        raise error

    return {}, switch_info


def get_bgp_neighbors_mellanox(ip, credentials):
    """Get BGP neighbors for a Mellanox switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch

    Returns:
        bgp_neighbors: A dict with switch neighbors
        switch_info: A dict with switch info

    Raises:
        ConnectionError: Connection error exception
        HTTPError: Authentication exception
    """
    session = requests.Session()

    # Login
    login = session.post(
        f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
        json=credentials,
        verify=False,
    )

    if login.status_code == 404:
        raise requests.exceptions.ConnectionError
    if login.json()["status"] != "OK":
        raise requests.exceptions.HTTPError

    try:
        bgp_status = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show ip bgp summary"},
            verify=False,
        )
        bgp_status = bgp_status.json()

        bgp_neighbors_mellanox = defaultdict(list)
        for x in bgp_status["data"]:
            if "VRF name" in x.keys():
                continue
            for entry in x:
                neighbor_ip = entry
                neighbor_status = x[entry][0]["State/PfxRcd"].split("/")[0]

                bgp_neighbor = {
                    "status": {"bgp_peer_state": neighbor_status.capitalize()},
                }
                bgp_neighbors_mellanox[neighbor_ip] = bgp_neighbor

        # Switch Hostname
        switch_hostname = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show hosts | include Hostname"},
            verify=False,
        )
        switch_hostname.raise_for_status()

        hostname = switch_hostname.json()["data"][0]["Hostname"]

        # Switch Model
        system_type = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show system type"},
            verify=False,
        )
        system_type.raise_for_status()

        platform_name = system_type.json()["data"]["value"]

        switch_info = {
            "platform_name": platform_name[0],
            "hostname": hostname,
        }

        # Cache switch values
        switch_json = {
            "ip_address": ip,
            "ip": ip,
            "hostname": switch_info["hostname"],
            "platform_name": switch_info["platform_name"],
            "vendor": "mellanox",
        }

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
        Exception,
    ) as error:
        exception_type = type(error).__name__
        click.secho(
            f"Error connecting to switch {ip}, {exception_type}.",
            fg="white",
            bg="red",
        )
        return None, None

    return bgp_neighbors_mellanox, switch_json
