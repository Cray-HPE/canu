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
"""CANU commands that report the cabling of the entire Shasta network."""
from collections import defaultdict
import ipaddress
import json
import logging
import re
import sys

import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
import requests

from canu.report.switch.cabling.cabling import (
    add_heuristic_metadata_to_lldp,
    add_kea_metadata_to_lldp,
    add_sls_metadata_to_lldp,
    add_smd_metadata_to_lldp,
    get_lldp,
    print_lldp,
)
from canu.style import Style

log = logging.getLogger("report_cabling")


@click.command(
    cls=Style.CanuHelpColorsCommand,
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
    "--view",
    type=click.Choice(["switch", "equipment"]),
    help="View of the cabling results.",
    default="switch",
    show_default=True,
)
@click.option(
    "--kea-lease-file",
    help="Kea leases in JSON format from API call used for MAC-to-hostname lookups.",
    type=click.File("r"),
    required=False,
)
@click.option(
    "--sls-file",
    help="SLS file in JSON format from API call used for MAC-to-hostname lookups.",
    type=click.File("r"),
    required=False,
)
@click.option(
    "--smd-file",
    help="SMD ethernetInterfaces in JSON format from API call used for MAC-to-hostname lookups.",
    type=click.File("r"),
    required=False,
)
@click.option(
    "--heuristic-lookups",
    help="Make educated guesses and hints about what device is based on MAC.",
    is_flag=True,
    default=False,
)
@click.option(
    "--log",
    "log_",
    help="Level of logging.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="ERROR",
)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.pass_context
def cabling(
    ctx,
    ips,
    ips_file,
    username,
    password,
    view,
    kea_lease_file,
    sls_file,
    smd_file,
    heuristic_lookups,
    log_,
    out,
):
    """Report the cabling of all switches (Aruba, Dell, or Mellanox) on the network by using LLDP.

    Pass in either a comma separated list of IP addresses using the --ips option

    OR

    Pass in a file of IP addresses with one address per line.

    There are three different connection types that will be shown in the results.

    1. '===>' Outbound connections

    2. '<===' Inbound connections

    3. '<==>' Bi-directional connections


    There are two different '--view' options, 'switch' and 'equipment'.

    1. The '--view switch' option displays a table for every switch IP address passed in showing connections.

    2. The '--view equipment' option displays a table for each mac address connection. This means that servers
    and switches will both display incoming and outgoing connections.

    If the neighbor name is not in LLDP, the IP and vlan information are displayed
    by looking up the MAC address in the ARP table and mac address table.

    If there is a duplicate port, the duplicates will be highlighted in 'bright white'.

    Ports highlighted in 'blue' contain the string "ncn" in the hostname.

    Ports are highlighted in 'green' when the port name is set with the interface name.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        view: View of the cabling results.
        kea_lease_file: Name of the JSON file containing Kea leases
        sls_file: Name of the JSON file containing SLS system data
        smd_file: Name of the JSON file containing SMD ethernetInterfaces
        heuristic_lookups: Turn off annotations to LLDP data based on common device use
        log_: Level of logging.
        out: Name of the output file
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

    try:
        kea_json = None
        if kea_lease_file is not None:
            kea_json = json.load(kea_lease_file)
    except json.JSONDecodeError:
        click.secho(
            f"The Kea lease file {kea_lease_file.name} is not valid JSON.  LLDP data will not be annotated.",
            fg="white",
            bg="red",
        )

    try:
        sls_json = None
        if sls_file is not None:
            sls_json = json.load(sls_file)
    except json.JSONDecodeError:
        click.secho(
            f"The SLS  file {sls_file.name} is not valid JSON.  LLDP data will not be annotated.",
            fg="white",
            bg="red",
        )

    try:
        smd_json = None
        if smd_file is not None:
            smd_json = json.load(smd_file)
    except json.JSONDecodeError:
        click.secho(
            f"The SMD  file {smd_file.name} is not valid JSON.  LLDP data will not be annotated.",
            fg="white",
            bg="red",
        )

    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}
    switch_data = []
    errors = []
    ips_length = len(ips)
    if ips:
        with click_spinner.spinner(
            beep=False,
            disable=False,
            force=False,
            stream=sys.stdout,
        ):
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    switch_info, switch_dict, arp = get_lldp(
                        str(ip),
                        credentials,
                        return_error=True,
                    )

                    # Annotate LLDP data with Kea lease data via MAC lookup.
                    if kea_json is not None:
                        add_kea_metadata_to_lldp(switch_dict, kea_json)
                    # Annotate LLDP data with SLS file data via MAC lookup.
                    if sls_json is not None:
                        add_sls_metadata_to_lldp(switch_dict, sls_json)
                    # Annotate LLDP data with SMD ethernetInterfaces data
                    if smd_json is not None:
                        add_smd_metadata_to_lldp(switch_dict, smd_json)
                    # Annotate LLDP data with heuristics
                    if heuristic_lookups:
                        add_heuristic_metadata_to_lldp(switch_info, switch_dict)

                    switch_data.append(
                        [
                            switch_info,
                            switch_dict,
                            arp,
                        ],
                    )
                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    NetmikoTimeoutException,
                    NetmikoAuthenticationException,
                ) as err:
                    exception_type = type(err).__name__
                    error_message = "Unchecked"
                    if exception_type == "HTTPError":
                        error_message = f"Error connecting to switch {ip}, check the entered username, IP address and password."
                    if exception_type == "ConnectionError":
                        error_message = f"Error connecting to switch {ip}, check the entered username, IP address and password."
                    if exception_type == "RequestException":
                        error_message = f"Error connecting to switch {ip}."
                    if exception_type == "NetmikoTimeoutException":
                        error_message = f"Timeout error connecting to switch {ip}, check the entered username, IP address and password."  # noqa: B950
                    if exception_type == "NetmikoAuthenticationException":
                        error_message = f"Auth error connecting to switch {ip}, check the entered username, IP address and password."  # noqa: B950

                    errors.append(
                        [
                            str(ip),
                            error_message,
                        ],
                    )

        if view == "switch":
            switch_table(switch_data, heuristic_lookups, out)
        elif view == "equipment":
            equipment_json = equipment_table(switch_data)
            print_equipment(equipment_json, out)

        dash = "-" * 100
        if len(errors) > 0:
            click.secho("\nErrors", fg="red", file=out)
            click.echo(dash, file=out)
            for error in errors:
                click.echo("{:<15s} - {}".format(error[0], error[1]), file=out)


def equipment_table(switch_data):
    """Generate a dictionary of MAC addresses and what each address is connected to.

    Args:
        switch_data: A dictionary containing data for each equipment.
            switch_data[i][0] -> Dictionary with switch platform_name, hostname and IP address
            switch_data[i][1] -> Dictionary with LLDP information
            switch_data[i][2] -> ARP dictionary

    Returns:
        equipment_json: Dictionary with mac addresses as keys.
    """
    equipment_json = defaultdict(lambda: defaultdict(dict))

    # Go through equipment and make the "TO" connections
    for i in range(len(switch_data)):
        # Add the mac address to equipment_json
        equipment_json[switch_data[i][0]["system_mac"]].update(
            {"hostname": switch_data[i][0]["hostname"]},
        )

        for port in switch_data[i][1]:
            port_entries = []
            for entry in range(len(switch_data[i][1][port])):
                switch_entry = switch_data[i][1][port][entry]

                connection = {
                    "neighbor": switch_entry["chassis_name"],
                    "neighbor_description": switch_entry["chassis_description"],
                    "neighbor_port": switch_entry["port_id"],
                    "neighbor_port_description": switch_entry["port_description"],
                    "neighbor_port_mac": switch_entry["mac_addr"],
                    "neighbor_chassis_mac": switch_entry["chassis_id"],
                }
                port_entries.append(connection)

            equipment_json[switch_data[i][0]["system_mac"]]["connections_to"][
                port
            ] = port_entries

    # Go through a second time and make the "FROM" connections
    for equipment in equipment_json.copy():
        for port in equipment_json[equipment]["connections_to"]:
            for entry in range(len(equipment_json[equipment]["connections_to"][port])):
                equipment_entry = equipment_json[equipment]["connections_to"][port][
                    entry
                ]

                neighbor_mac = equipment_entry["neighbor_chassis_mac"]
                neighbor_port = equipment_entry["neighbor_port"]

                equipment_json[neighbor_mac]["hostname"] = equipment_entry["neighbor"]
                equipment_json[neighbor_mac]["description"] = equipment_entry[
                    "neighbor_description"
                ]

                connection_dict = {
                    "hostname": equipment_json[equipment]["hostname"],
                    "description": equipment_json[equipment]["description"],
                    "port": port,
                    "port_description": equipment_entry["neighbor_port_description"],
                }

                equipment_json[neighbor_mac]["connections_from"].update(
                    {neighbor_port: connection_dict},
                )

    # Go through a third time to add all ARP info to equipment_json
    for i in range(len(switch_data)):
        for mac in switch_data[i][2]:
            arp_mac = switch_data[i][2][mac]
            if arp_mac["mac"] in equipment_json.keys():
                arp_list = f"{arp_mac['ip_address']}:{list(arp_mac['port'])[0]}"

                if len(equipment_json[arp_mac["mac"]]["arp"]) == 0:
                    equipment_json[arp_mac["mac"]]["arp"] = [arp_list]
                else:
                    equipment_json[arp_mac["mac"]]["arp"].append(arp_list)

    return equipment_json


def print_equipment(equipment_json, out="-"):
    """Print a table for each mac address.

    Args:
        equipment_json: A dictionary containing data for each equipment.
        out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 100

    for equipment in equipment_json:
        click.secho(
            f'{equipment_json[equipment]["hostname"]} {equipment_json[equipment]["description"]}                     ',
            fg="bright_white",
            file=out,
        )
        click.secho(f"{equipment}", fg="bright_white", file=out)
        # Remove duplicates from ARP
        arp = set(equipment_json[equipment]["arp"])
        if arp:
            click.secho(", ".join(arp), fg="bright_white", file=out)

        click.echo(dash, file=out)

        for port in equipment_json[equipment]["connections_to"]:
            for entry in range(len(equipment_json[equipment]["connections_to"][port])):
                neighbor_port = equipment_json[equipment]["connections_to"][port][
                    entry
                ]["neighbor_port"]
                neighbor_port_description = re.sub(
                    r"(Interface\s+\d+ as )",
                    "",
                    equipment_json[equipment]["connections_to"][port][entry][
                        "neighbor_port_description"
                    ],
                )

                if neighbor_port_description == neighbor_port:
                    neighbor_port_description = ""
                text_color = ""
                if (
                    "ncn"
                    in equipment_json[equipment]["connections_to"][port][entry][
                        "neighbor"
                    ]
                ):
                    text_color = "blue"
                elif (
                    "sw-"
                    in equipment_json[equipment]["connections_to"][port][entry][
                        "neighbor"
                    ]
                ):
                    text_color = "green"

                if port not in equipment_json[equipment]["connections_from"]:
                    arrow = "===>"
                elif port in equipment_json[equipment]["connections_from"]:
                    arrow = "<==>"
                else:  # pragma: no cover
                    arrow = "<==="

                click.secho(
                    "{:<25s}{:^6s}{:<15s} {} {} {}".format(
                        port,
                        arrow,
                        equipment_json[equipment]["connections_to"][port][entry][
                            "neighbor"
                        ],
                        neighbor_port,
                        neighbor_port_description,
                        equipment_json[equipment]["connections_to"][port][entry][
                            "neighbor_description"
                        ][:54],
                    ),
                    fg=text_color,
                    file=out,
                )

        for port in equipment_json[equipment]["connections_from"]:
            if port not in equipment_json[equipment]["connections_to"]:
                description = equipment_json[equipment]["connections_from"][port][
                    "description"
                ]
                port_description = re.sub(
                    r"(Interface\s+\d+ as )",
                    "",
                    equipment_json[equipment]["connections_from"][port][
                        "port_description"
                    ],
                )
                if port_description == port:
                    port_description = ""
                text_color = ""
                if "ncn" in str(
                    equipment_json[equipment]["connections_from"][port]["hostname"],
                ):  # pragma: no cover
                    text_color = "blue"
                if "sw-" in str(
                    equipment_json[equipment]["connections_from"][port]["hostname"],
                ):
                    text_color = "green"

                if len(description) == 0:
                    description = ""
                arrow = "<==="
                click.secho(
                    "{:<25s}{:^6s}{:<15s} {} {}".format(
                        port + " " + port_description,
                        arrow,
                        str(
                            equipment_json[equipment]["connections_from"][port][
                                "hostname"
                            ],
                        ),
                        equipment_json[equipment]["connections_from"][port]["port"],
                        description,
                    ),
                    fg=text_color,
                    file=out,
                )
        click.echo("\n", file=out)


def switch_table(switch_data, heuristic_lookups, out="-"):
    """Print a table for each switch.

    Args:
        switch_data: A list containing data for each switch.
            switch_data[i][0] -> Dictionary with switch platform_name, hostname and IP address
            switch_data[i][1] -> Dictionary with LLDP information
            switch_data[i][2] -> ARP dictionary
        heuristic_lookups: Table of educated guesses about normal configurations
        out: Defaults to stdout, but will print to the file name passed in
    """
    for i in range(len(switch_data)):
        print_lldp(switch_data[i][0], switch_data[i][1], switch_data[i][2], heuristic_lookups, out)
