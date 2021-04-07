"""CANU commands that report the firmware of an individual switch."""
from collections import defaultdict, OrderedDict
import datetime
import re
from urllib.parse import unquote

import click
from click_help_colors import HelpColorsCommand
import natsort
import requests
import urllib3

from canu.cache import cache_switch

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option("--ip", required=True, help="The IP address of the switch")
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--out", help="Output results to a file", type=click.File("w"), default="-"
)
@click.pass_context
def cabling(ctx, username, ip, password, out):
    """Report the cabling of an Aruba switch (API v10.04) on the network by using LLDP.

    If the neighbor name is not in LLDP, the IP and vlan information are displayed
    by looking up the MAC address in the ARP table.

    If there is a duplicate port, the duplicates will be highlighted in bright white.

    Ports highlighted in blue contain the string "ncn" in the hostname.

    Ports are highlighted in green when the port name is set with the interface name.
    """
    credentials = {"username": username, "password": password}
    switch_info, switch_dict, arp = get_lldp(ip, credentials)

    cache_lldp(switch_info, switch_dict, arp)
    print_lldp(switch_info, switch_dict, arp, out)


def get_lldp(ip, credentials):
    """Get lldp of an Aruba switch using v10.04 API.

    :param ip: IPv4 address of the switch
    :param credentials: Dictionary with username and password of the switch

    :return switch_info: Dictionary with switch platform_name, hostname and IP address
    :return lldp_dict: Dictionary with LLDP information
    :return arp: ARP dictionary
    """
    session = requests.Session()
    # try:
    # Login
    session.post(f"https://{ip}/rest/v10.04/login", data=credentials, verify=False)
    # login.raise_for_status()

    # try:

    # GET switch info
    switch_info_response = session.get(
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        verify=False,
    )
    # switch_info_response.raise_for_status()
    switch_info = switch_info_response.json()
    switch_info["ip"] = ip

    # GET LLDP neighbors
    neighbors = session.get(
        f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
        verify=False,
    )
    # neighbors.raise_for_status()
    neighbors_dict = neighbors.json()

    arp_response = session.get(
        f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
        verify=False,
    )
    # arp_response.raise_for_status()
    arp = arp_response.json()

    # interfaces = []
    lldp_dict = defaultdict(list)
    for port in neighbors_dict:
        interface = unquote(port)

        for x in neighbors_dict[port]:
            neighbor = {
                "chassis_id": neighbors_dict[port][x]["chassis_id"],
                "mac_addr": neighbors_dict[port][x]["mac_addr"],
                "chassis_description": neighbors_dict[port][x]["neighbor_info"][
                    "chassis_description"
                ],
                "chassis_name": neighbors_dict[port][x]["neighbor_info"][
                    "chassis_name"
                ],
                "port_description": neighbors_dict[port][x]["neighbor_info"][
                    "port_description"
                ],
                "port_id_subtype": neighbors_dict[port][x]["neighbor_info"][
                    "port_id_subtype"
                ],
                "port_id": neighbors_dict[port][x]["port_id"],
            }

            lldp_dict[interface].append(neighbor)

    # Logout
    session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    # Order the ports in natural order
    lldp_dict = OrderedDict(natsort.natsorted(lldp_dict.items()))

    return switch_info, lldp_dict, arp


def cache_lldp(switch_info, lldp_dict, arp):
    """Format LLDP info and cache it."""
    switch = {
        "ip_address": switch_info["ip"],
        "cabling": defaultdict(list),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    for port in lldp_dict:
        for entry in range(len(lldp_dict[port])):
            arp_list = []
            if lldp_dict[port][entry]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == lldp_dict[port][entry]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)

            port_info = {
                "neighbor": lldp_dict[port][entry]["chassis_name"],
                "neighbor_description": lldp_dict[port][entry]["chassis_description"][
                    :54
                ]
                + str(arp_list),
                "neighbor_port": lldp_dict[port][entry]["port_id"],
                "neighbor_port_description": re.sub(
                    r"(Interface\s+[0-9]+ as )",
                    "",
                    lldp_dict[port][entry]["port_description"],
                ),
            }

            switch["cabling"][port].append(port_info)
    switch["cabling"] = dict(switch["cabling"])
    cache_switch(switch)


def print_lldp(switch_info, lldp_dict, arp, out="-"):
    """Print summary of the switch LLDP data.

    :param switch_info: Dictionary with switch platform_name, hostname and IP address
    :param lldp_dict: Dictionary with LLDP information
    :param arp: ARP dictionary
    :param out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 150
    heading = [
        "PORT",
        "",
        "NEIGHBOR",
        "NEIGHBOR PORT",
        "PORT DESCRIPTION",
        "DESCRIPTION",
    ]

    table = []
    for port in lldp_dict:
        for entry in range(len(lldp_dict[port])):
            # If the device cannot be discovered by lldp, look it up in the ARP.
            arp_list = []
            if lldp_dict[port][entry]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == lldp_dict[port][entry]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)

            if (
                lldp_dict[port][entry]["port_description"]
                == lldp_dict[port][entry]["port_id"]
            ):
                neighbor_port = lldp_dict[port][entry]["port_id"]
                neighbor_description = ""
            else:
                neighbor_port = lldp_dict[port][entry]["port_id"]
                neighbor_description = re.sub(
                    r"(Interface\s+[0-9]+ as )",
                    "",
                    lldp_dict[port][entry]["port_description"],
                )
            if len(arp_list) > 0 and neighbor_description == "":
                neighbor_description = "No LLDP data, check ARP vlan info."
            duplicate = False
            if len(lldp_dict[port]) > 1:
                duplicate = True

            table.append(
                [
                    port,
                    lldp_dict[port][entry]["chassis_name"],
                    neighbor_port,
                    neighbor_description,
                    lldp_dict[port][entry]["chassis_description"][:54] + str(arp_list),
                    lldp_dict[port][entry]["port_id_subtype"],
                    duplicate,
                ]
            )

    click.secho(
        f"Switch: {switch_info['hostname']} ({switch_info['ip']})",
        fg="bright_white",
        file=out,
    )
    click.secho(f"Aruba {switch_info['platform_name']}", fg="bright_white", file=out)

    click.echo(dash, file=out)
    click.echo(
        "{:<7s}{:^5s}{:<15s}{:<19s}{:<54s}{}".format(
            heading[0],
            heading[1],
            heading[2],
            heading[3],
            heading[4],
            heading[5],
        ),
        file=out,
    )
    click.echo(dash, file=out)

    for i in range(len(table)):
        text_color = ""
        if table[i][5] == "if_name":
            text_color = "green"
        elif "ncn" in table[i][1]:
            text_color = "blue"
        if table[i][6] is True:
            text_color = "bright_white"

        click.secho(
            "{:<7s}{:^5s}{:<15s}{:<19s}{:<54s}{}".format(
                table[i][0],
                "==>",
                table[i][1],
                table[i][2],
                table[i][3],
                table[i][4],
            ),
            fg=text_color,
            file=out,
        )
