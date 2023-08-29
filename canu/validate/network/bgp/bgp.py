# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
import sys

import click
import click_spinner
import natsort
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
import requests

from canu.style import Style
from canu.utils.sls import pull_sls_networks
from canu.utils.vendor import switch_vendor


@click.command(
    cls=Style.CanuHelpColorsCommand,
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
    "--network",
    default="ALL",
    show_default=True,
    type=click.Choice(["ALL", "NMN", "CMN"], case_sensitive=False),
    help="The network that BGP neighbors are checked.",
)
@click.option("--verbose", is_flag=True, help="Verbose mode")
@click.pass_context
def bgp(ctx, username, password, verbose, network):
    """Validate BGP neighbors.

    This command will check the BGP neighbors for the switch IP addresses entered. All of the neighbors of a switch
    must be 'Established', or the verification will fail.

    If a switch that is not a spine switch is tested, it will show in the results table as 'SKIP'.

    - Enter a comma separated list of IP addresses with the '---ips' flag.

    - Or read the IP addresses from a file, one IP address per line, using '--ips-file FILENAME' flag.

    If you want to see the individual status of all the neighbors of a switch, use the '--verbose' flag.

    --------
    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        username: Switch username
        password: Switch password
        verbose: Bool indicating verbose output
        network: The network that BGP neighbors are checked
    """
    credentials = {"username": username, "password": password}
    data = {}
    errors = []
    sls_cache = pull_sls_networks()
    if sls_cache["SWITCH_ASN"]:
        asn = sls_cache["SWITCH_ASN"]
    else:
        # default asn if ASN isn't in SLS
        asn = "65533"
    spine_switches = [
        sls_cache["HMN_IPs"]["sw-spine-001"],
        sls_cache["HMN_IPs"]["sw-spine-002"],
    ]
    with click_spinner.spinner(
        beep=False,
        disable=False,
        force=False,
        stream=sys.stdout,
    ):
        for ip in spine_switches:
            print(
                "  Connecting",
                end="\r",
            )

            bgp_neighbors, switch_info = get_bgp_neighbors(
                str(ip),
                credentials,
                asn,
                network,
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
                f"Switch: {hostname} ({ip})                       ",
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
                errors.append(
                    [
                        neighbor,
                        neighbor_status,
                    ],
                )
                if verbose:
                    click.secho(
                        f"{hostname} ===> {neighbor}: {neighbor_status}",
                        fg="red",
                    )
            else:
                if verbose:
                    click.secho(f"{hostname} ===> {neighbor}: {neighbor_status}")

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
        sys.exit(1)


def get_bgp_neighbors(ip, credentials, asn, network):
    """Get BGP neighbors for a switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        asn: Switch ASN
        network: The network that BGP neighbors are checked

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
            bgp_neighbors, switch_info = get_bgp_neighbors_aruba(
                ip,
                credentials,
                asn,
                network,
            )
        elif vendor == "dell":
            # This function returns: {}, switch_info
            # There won't be any Dell switches with BGP neighbors
            bgp_neighbors, switch_info = get_bgp_neighbors_dell(
                ip,
                credentials,
            )
        elif vendor == "mellanox":
            bgp_neighbors, switch_info = get_bgp_neighbors_mellanox(
                ip,
                credentials,
                network,
            )

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
    ) as error:
        exception_type = type(error).__name__
        click.secho(
            f"Error connecting to switch {ip}, {exception_type}.",
            fg="white",
            bg="red",
        )
        return None, None

    return bgp_neighbors, switch_info


def get_bgp_neighbors_aruba(ip, credentials, asn, network):
    """Get BGP neighbors for an Aruba switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        asn: Switch ASN
        network: The network that BGP neighbors are checked

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
            error_message = f"Error connecting to switch {ip}, check the entered username, IP address and password."
        else:
            error_message = f"Error connecting to switch {ip}."

        click.secho(
            str(error_message),
            fg="white",
            bg="red",
        )
        return None, None
    # Get neighbors
    bgp_neighbors_aruba = {}
    network_list = {"CMN": "Customer", "NMN": "default"}
    if network == "NMN":
        del network_list["CMN"]
    elif network == "CMN":
        del network_list["NMN"]

    try:
        for net_vrf in network_list.values():
            bgp_neighbors_response = session.get(
                f"https://{ip}/rest/v10.04/system/vrfs/{net_vrf}/bgp_routers/{asn}/bgp_neighbors?depth=2",
                verify=False,
            )
            bgp_neighbors_response.raise_for_status()
            bgp_neighbors_aruba.update(bgp_neighbors_response.json())
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


def get_bgp_neighbors_mellanox(ip, credentials, network):
    """Get BGP neighbors for a Mellanox switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        network: The network that BGP neighbors are checked

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

    if network == "NMN":
        net_vrf = "default"
    elif network == "CMN":
        net_vrf = "Customer"
    else:
        net_vrf = "all"
    try:
        bgp_status = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": f"show ip bgp vrf {net_vrf} summary"},
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
