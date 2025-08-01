# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""CANU commands that validate the network cabling."""
import datetime
import ipaddress
import logging
import re
import sys
from collections import defaultdict

import click
import click_spinner
import requests
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from ruamel.yaml import YAML

from canu.report.switch.cabling.cabling import get_lldp
from canu.style import Style
from canu.validate.shcd.shcd import node_list_warnings, print_node_list
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from network_modeling.NetworkPort import NetworkPort

yaml = YAML()

log = logging.getLogger("validate_cabling")


def create_cache_structure_from_lldp(switch_info, lldp_dict, arp):
    """Create a cache structure from LLDP data that matches the expected format.

    Args:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary

    Returns:
        Dictionary representing switch in cache format
    """
    switch = {
        "ip_address": switch_info["ip"],
        "cabling": defaultdict(list),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": switch_info["hostname"],
        "platform_name": switch_info["platform_name"],
        "vendor": switch_info["vendor"],
    }

    for port_number, port in lldp_dict.items():
        for index, _entry in enumerate(port):
            arp_list = []
            if port[index]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == port[index]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)
            neighbor_description = f"{port[index]['chassis_description'][:54]} {str(arp_list)}"
            port_info = {
                "neighbor": port[index]["chassis_name"],
                "neighbor_description": neighbor_description,
                "neighbor_port": port[index]["port_id"],
                "neighbor_port_description": re.sub(
                    r"(Interface\s+\d+ as )",
                    "",
                    port[index]["port_description"],
                ),
                "neighbor_chassis_id": port[index]["chassis_id"],
            }

            switch["cabling"][port_number].append(port_info)

    switch["cabling"] = dict(switch["cabling"])
    return switch


@click.command(
    cls=Style.CanuHelpColorsCommand,
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "v1"], case_sensitive=False),
    help="CSM architecture",
    required=True,
    prompt="Architecture type",
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
def cabling(ctx, architecture, ips, ips_file, username, password, log_, out):
    """Validate network cabling.

    CANU can be used to validate that network cabling passes basic validation checks.

    This command will use LLDP to determine if the network is properly connected architecturally.

    The validation will ensure that spine switches, leaf switches, edge switches, and nodes all are connected properly.

    --------
    \f
    # noqa: D301, B950

    Args:
        ctx: CANU context settings
        architecture: CSM architecture
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        log_: Level of logging.
        out: Name of the output file
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

    if architecture.lower() == "full":
        architecture = "network_v2"
    elif architecture.lower() == "tds":
        architecture = "network_v2_tds"
    elif architecture.lower() == "v1":
        architecture = "network_v1"

    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    errors = []
    ips_length = len(ips)

    # Create in-memory cache structure from live LLDP data
    switches_list = []

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
                    # Get LLDP info directly (without caching to file)
                    switch_info, lldp_dict, arp = get_lldp(str(ip), credentials, return_error=True)

                    if switch_info and lldp_dict:
                        # Create cache structure from live LLDP data
                        switch_cache_entry = create_cache_structure_from_lldp(switch_info, lldp_dict, arp)
                        switches_list.append(switch_cache_entry)

                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    NetmikoTimeoutException,
                    NetmikoAuthenticationException,
                ) as err:
                    exception_type = type(err).__name__

                    if exception_type == "HTTPError":
                        error_message = f"Error connecting to switch {ip}, check the IP, username, or password."
                    elif exception_type == "ConnectionError":
                        error_message = (
                            f"Error connecting to switch {ip}, check the entered username, IP address and password."
                        )
                    elif exception_type == "NetmikoTimeoutException":
                        error_message = f"Timeout error connecting to {ip}. Check the IP address and try again."
                    elif exception_type == "NetmikoAuthenticationException":
                        error_message = (
                            f"Auth error connecting to {ip}. Check the credentials or IP address and try again"
                        )
                    else:
                        error_message = f"Error connecting to switch {ip}."

                    errors.append([str(ip), error_message])

    # Create in-memory network data structure that matches expected format
    network_data = {
        "version": "1.0",  # Using a default version
        "switches": switches_list,
    }

    # Create cabling Node factory and model from network data
    log.debug("Creating model from network data")
    cabling_factory = NetworkNodeFactory(architecture_version=architecture)
    cabling_node_list, cabling_warnings = node_model_from_canu(
        cabling_factory,
        network_data,
        ips,
    )

    # Use the generated node list and warnings
    node_list = cabling_node_list
    warnings = cabling_warnings

    print_node_list(node_list, "Cabling", out)

    node_list_warnings(node_list, warnings, out)

    dash = "-" * 100
    if len(errors) > 0:
        click.echo("\n", file=out)
        click.secho("Errors", fg="red", file=out)
        click.echo(dash, file=out)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]), file=out)


def get_node_type_yaml(name, mapper):
    """Map SHCD device name to device type.

    Args:
        name: A string from SHCD representing the device name
        mapper: An array of tuples (SHCD name, hostname, device type)

    Returns:
        node_type: A string with the device type
        rename: The name the node needs to be renamed
    """
    node_type = None
    rename = None
    for node in mapper:
        for lookup_name in node[0]:
            if re.match("^{}".format(lookup_name.strip()), name):
                node_type = node[2]
                if lookup_name is not node[1]:
                    rename = node[1]
                return node_type, rename
    return node_type, None


def validate_cabling_slot_data(lldp_info, warnings, vendor="aruba"):
    """Ensure LLDP data is parsed properly into a slot.

    Args:
        lldp_info: String representing port and slot info from LLDP.
        warnings: Existing list of warnings to post to.
        vendor: Switch vendor

    Returns:
        slot: A cleaned up string value from initial LLDP data.
    """
    # TODO:  Integrate with cabling standards and remove this hack.
    # NCN slot case
    port_result = re.search(
        r"([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}",
        lldp_info["neighbor_port"],
    )
    port_description_result = re.search(
        r"mgmt(\d)",
        lldp_info["neighbor_port_description"],
    )
    if port_result is not None and port_description_result is not None:
        port_number = int(port_description_result.group(1))
        if vendor == "aruba":
            if port_number in [0, 1]:
                return "ocp"
            elif port_number in [2, 3]:
                return "pcie-slot1"
        else:
            return "pcie-slot1"

    return None


def validate_cabling_port_data(lldp_info, warnings):
    """Ensure LLDP data is parsed properly into a port.

    Args:
        lldp_info: String representing port and slot info from LLDP.
        warnings: Existing list of warnings to post to

    Returns:
        port: A cleaned up string value from initial LLDP data
    """
    # TODO:  Integrate with cabling standards and remove this hack.

    # Arista edge port case
    port_result = re.search(r"Ethernet1/(\d+)$", lldp_info["neighbor_port"])
    if port_result is not None:
        return int(port_result.group(1))

    # Switch port case
    port_result = re.search(r"1/1/(\d+)$", lldp_info["neighbor_port"])
    if port_result is not None:
        return int(port_result.group(1))

    # NCN port case
    port_result = re.search(
        r"([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}",
        lldp_info["neighbor_port"],
    )
    port_description_result = re.search(
        r"mgmt(\d)",
        lldp_info["neighbor_port_description"],
    )
    if port_result is not None and port_description_result is not None:
        port_number = int(port_description_result.group(1))
        if port_number in [0, 1]:
            # OCP slot, keep ports same but convert to one's based
            return int(port_number) + 1
        elif port_number in [2, 3]:
            # PCIE-Slot1 slot, levelset ports to 1, 2 one's based
            return int(port_number) - 1

    return None


class FormatSwitchDestinationNameError(Exception):
    """Exception raised when the switch destination name cannot be formatted."""

    def __init__(
        self,
        message="Unable to parse and format switch destination name. Should follow the format: 'sw-NAME-NNN'",
    ):
        # noqa: DAR101
        """Initialize the exception."""
        self.message = message
        super().__init__(self.message)


def format_switch_dst_name(dst_name):
    # noqa: DAR101, DAR201, DAR401
    """
    Format the destination name.

    Parameters:
    - dst_name (str): The destination name to format.

    Raises:
    - FormatSwitchDestinationNameError (Exception): If the destination name cannot be formatted according to the expected pattern.

      Returns:
    - formatted_dst_name (str): The formatted destination name.
    """
    # TODO: the naming requirement is fairly arbitrary and should be documented or improved
    # regex match for the following patterns:
    #   1. a prefix ending with a letter (excluding g/G) followed by digits
    #   2. a prefix that may include 'g' or 'G' as part of the middle section followed by digits
    pattern = re.compile(r"(sw-)((?:.*[^gG\d]|.*[gG])?)(\d+)")
    match = pattern.match(dst_name)
    # if the name is close to what we need, try to format it
    if match:
        prefix = match.group(1).rstrip("-")
        middle = match.group(2).rstrip("-").replace("-", "")
        # some other commands like 'report switch firmware|cabling' and even
        # certain variants of 'validate network cabling', where this code gets
        # called there is some weird interdependencies here that are in the
        # existing integration tests.  since I broke this out into its own
        # function in an effort to start a better testing pattern, it has some
        # unintended consequences.  that said, this could potentially go away
        # once the other monolithinc functions are decomposed and the tests in
        # general are more robust
        if middle == "leafbmc":
            middle = "leaf-bmc"
        number = match.group(3)
        # format the number to have three digits, padding with zeros if necessary
        formatted_number = f"{int(number):03d}"
        # combine the parts into the desired format
        return f"{prefix}-{middle}-{formatted_number}"
    # otherwise, return an error
    else:
        raise FormatSwitchDestinationNameError


def node_model_from_canu(factory, network_data, ips):
    """Create a list of nodes from network data.

    Args:
        factory: Node factory object
        network_data: Network data structure with switch information
        ips: List of ips to check

    Returns:
        node_list: A list of created nodes
        warnings: A list of warnings
    """
    # Generated nodes
    node_list = []
    node_name_list = []
    warnings = defaultdict(list)

    # Handle case where network data is empty
    if "switches" not in network_data:
        return node_list, warnings

    for switch in network_data["switches"]:
        if ipaddress.ip_address(switch["ip_address"]) in ips:
            src_name = switch["hostname"]

            for port in switch["cabling"]:
                #
                # Source is always a switch
                #
                src_slot = None  # Always local switch
                src_lldp = {"neighbor_port": port, "neighbor_port_description": None}
                src_port = validate_cabling_port_data(src_lldp, warnings)
                log.debug(f"Source Data:  {src_name} {src_slot} {src_port}")
                # If starts with 'sw-' then add an extra '-' before the number, and convert to 3 digit.
                # Needs to work for these combinations:
                # sw-spine01
                # sw-spine-002
                # sw-leaf-bmc99
                # sw-leaf-bmc-098
                node_name = src_name
                if str(node_name).startswith("sw-"):
                    start = "sw-"
                    middle = re.findall(r"(?:sw-)([a-z-]+)", node_name)[0]
                    digits = re.findall(r"(\d+)", node_name)[0]
                    node_name = f"{start}{middle.rstrip('-')}-{int(digits) :03d}"

                log.debug(f"Source Name Lookup: {node_name}")
                node_type, rename = get_node_type_yaml(
                    str(src_name),
                    factory.lookup_mapper(),
                )
                log.debug(f"Source Node Type Lookup: {node_type}")

                # If the hostname is not the Shasta name, it needs to be renamed
                if src_name != node_name or rename is not None:
                    renamed = node_name

                    if rename is not None:
                        digits = re.findall(r"(\d+)", node_name)[0]
                        renamed = f"{rename}-{int(digits) :03d}"

                    # If type can't be determined, we do not know what to rename the switch
                    if node_type is None:
                        renamed = ""
                    warnings["rename"].append([src_name, renamed])
                    log.warning(f"Node {src_name} should be renamed to {node_name}")
                # Create src_node if it does not exist
                src_node = None
                src_index = None
                if node_type is not None and node_name is not None:
                    if node_name not in node_name_list:
                        log.info(f"Creating new node {node_name} of type {node_type}")
                        try:
                            src_node = factory.generate_node(node_type)
                        except Exception as e:
                            print(e)
                            sys.exit(1)

                        src_node.common_name(node_name)

                        node_list.append(src_node)
                        node_name_list.append(node_name)
                    else:
                        log.debug(
                            f"Node {node_name} already exists, skipping node creation.",
                        )

                    src_index = node_name_list.index(node_name)
                else:
                    warnings["node_type"].append(node_name)
                    log.warning(
                        f"Node type for {node_name} cannot be determined by node type ({node_type}) or node name ({node_name})",
                    )

                # Create the source port for the node
                src_node_port = NetworkPort(number=src_port, slot=src_slot)

                #
                # Destinations could be a switch or a server
                #
                # Cable destination
                dst_lldp = switch["cabling"][port][0]

                dst_name = dst_lldp["neighbor"]
                dst_slot = validate_cabling_slot_data(
                    dst_lldp,
                    warnings,
                    vendor=switch["vendor"],
                )
                dst_port = validate_cabling_port_data(dst_lldp, warnings)

                # If starts with 'sw-' then add an extra '-' before the number, and convert to 3 digit
                if dst_name.startswith("sw-"):
                    dst_name = format_switch_dst_name(dst_name)

                log.debug(f"Destination Data: {dst_name} {dst_slot} {dst_port}")
                dst_node_name = dst_name
                log.debug(f"Destination Name Lookup:  {dst_node_name}")
                node_type, dst_rename = get_node_type_yaml(
                    dst_name,
                    factory.lookup_mapper(),
                )
                log.debug(f"Destination Node Type Lookup:  {node_type}")

                if (dst_name != dst_lldp["neighbor"] or dst_rename is not None) and dst_name is not None:
                    dst_renamed = dst_name

                    if dst_rename is not None:
                        dst_digits = re.findall(r"(\d+)", dst_name)[0]
                        dst_renamed = f"{dst_rename}-{int(dst_digits) :03d}"

                    # If type can't be determined, we do not know what to rename the switch
                    if node_type is None:
                        dst_renamed = ""
                    warnings["rename"].append([dst_lldp["neighbor"], dst_renamed])
                    log.warning(
                        f"Node {dst_lldp['neighbor']} should be renamed {dst_renamed}",
                    )
                # Create dst_node if it does not exist
                dst_node = None
                dst_index = None
                if node_type is not None and dst_node_name is not None:
                    if dst_node_name not in node_name_list:
                        log.info(
                            f"Creating new node {dst_node_name} of type {node_type}",
                        )
                        try:
                            dst_node = factory.generate_node(node_type)
                        except Exception as e:
                            print(e)
                            sys.exit(1)

                        dst_node.common_name(dst_node_name)

                        node_list.append(dst_node)
                        node_name_list.append(dst_node_name)
                    else:
                        log.debug(
                            f"Node {dst_node_name} already exists, skipping node creation.",
                        )

                    dst_index = node_name_list.index(dst_node_name)

                else:
                    warn_name = dst_name
                    warn_descrip = switch["cabling"][port][0]["neighbor_description"]
                    warn_port = switch["cabling"][port][0]["neighbor_port"]
                    dst_name_warning = f"{str(node_name) : <16} {port : <9} ===> {warn_port} {warn_name} {warn_descrip}"

                    warnings["node_type"].append(dst_name_warning)

                    log.warning(
                        f"Node type for {dst_name} cannot be determined by node type ({node_type}) or node name ({node_name})",
                    )

                # Create the destination
                dst_node_port = NetworkPort(number=dst_port, slot=dst_slot)

                # The destination node has been created, but the port number cannot be determined so skip connecting
                if dst_port is None:
                    log.warning(
                        f"Physical port number for {dst_name} cannot be determined from LLDP data "
                        f'"{dst_lldp["neighbor_port"]}" or "{dst_lldp["neighbor_port_description"]}"',
                    )
                    continue

                # Connect src_node and dst_node if possible
                if src_index is not None and dst_index is not None:
                    src_node = node_list[src_index]
                    dst_node = node_list[dst_index]
                    try:
                        connected = src_node.connect(
                            dst_node,
                            src_port=src_node_port,
                            dst_port=dst_node_port,
                            strict=False,
                        )
                    except Exception:
                        err_connect = f"Failed to connect {src_node.common_name()} to {dst_node.common_name()}"
                        log.fatal(err_connect)
                        click.secho(
                            err_connect,
                            fg="red",
                        )
                        sys.exit(1)
                    if connected:
                        log.info(
                            f"Connected {src_node.common_name()} to" + f" {dst_node.common_name()}",
                        )
                    else:
                        log.error("")
                        click.secho(
                            f"Failed to connect {src_node.common_name()}" + f" to {dst_node.common_name()}",
                            fg="red",
                        )
                        for node in node_list:
                            click.secho(
                                f"Node {node.id()} named {node.common_name()} connects "
                                + f"to {len(node.edges())} ports on nodes: {node.edges()}",
                            )
                        log.fatal(
                            f"Failed to connect {src_node.common_name()} " + f"to {dst_node.common_name()}",
                        )
                        sys.exit(1)  # TODO: this should probably be an exception
    return node_list, warnings
