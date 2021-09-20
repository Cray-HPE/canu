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
"""CANU commands that validate the network cabling."""
from collections import defaultdict
import ipaddress
import logging
from os import path
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from network_modeling.NetworkPort import NetworkPort
import requests
import ruamel.yaml

from canu.cache import cache_directory
from canu.report.switch.cabling.cabling import get_lldp
from canu.validate.shcd.shcd import node_list_warnings, print_node_list

yaml = ruamel.yaml.YAML()


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

# Schema and Data files
hardware_schema_file = path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-hardware-schema.yaml",
)
hardware_spec_file = path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-hardware.yaml",
)
architecture_schema_file = path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-architecture-schema.yaml",
)
architecture_spec_file = path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-architecture.yaml",
)

canu_cache_file = path.join(cache_directory(), "canu_cache.yaml")

log = logging.getLogger("validate_shcd")


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "v1"], case_sensitive=False),
    help="Shasta architecture",
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
@click.pass_context
def cabling(ctx, architecture, ips, ips_file, username, password, log_):
    """Validate the network.

    This command will use LLDP to determine the neighbors of the IP addresses passed in to validate that the network
    is properly connected architecturally. The validation will ensure that spine switches, leaf switches,
    edge switches, and nodes all are connected properly.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        architecture: Shasta architecture
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        log_: Level of logging.
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

    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    # Get LLDP info (stored in cache)
                    get_lldp(str(ip), credentials, return_error=True)

                except requests.exceptions.HTTPError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, "
                            + "check that this IP is an Aruba switch, or check the username or password.",
                        ],
                    )
                except requests.exceptions.ConnectionError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip},"
                            + " check the IP address and try again.",
                        ],
                    )
                except requests.exceptions.RequestException:  # pragma: no cover
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}.",
                        ],
                    )

    # Create Node factory
    factory = NetworkNodeFactory(
        hardware_schema=hardware_schema_file,
        hardware_data=hardware_spec_file,
        architecture_schema=architecture_schema_file,
        architecture_data=architecture_spec_file,
        architecture_version=architecture,
    )

    # Open the updated cache to model nodes
    with open(canu_cache_file, "r+") as file:
        canu_cache = yaml.load(file)

    node_list, warnings = node_model_from_canu(factory, canu_cache, ips)

    print_node_list(node_list, "Cabling")

    node_list_warnings(node_list, warnings)

    dash = "-" * 100
    if len(errors) > 0:
        click.echo("\n")
        click.secho("Errors", fg="red")
        click.echo(dash)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]))


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


def node_model_from_canu(factory, canu_cache, ips):
    """Create a list of nodes from CANU cache.

    Args:
        factory: Node factory object
        canu_cache: CANU cache file
        ips: List of ips to check

    Returns:
        node_list: A list of created nodes
        warnings: A list of warnings
    """
    # Generated nodes
    node_list = []
    node_name_list = []
    warnings = defaultdict(list)

    for switch in canu_cache["switches"]:
        if ipaddress.ip_address(switch["ip_address"]) in ips:
            src_name = switch["hostname"]

            for port in switch["cabling"]:

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

                # Cable destination
                dst_lldp = switch["cabling"][port][0]

                # If starts with 'sw-' then add an extra '-' before the number, and convert to 3 digit
                dst_name = dst_lldp["neighbor"]
                dst_slot = validate_cabling_slot_data(
                    dst_lldp,
                    warnings,
                    vendor=switch["vendor"],
                )
                dst_port = validate_cabling_port_data(dst_lldp, warnings)

                if dst_name.startswith("sw-"):
                    dst_start = "sw-"
                    dst_middle = re.findall(r"(?:sw-)([a-z-]+)", dst_name)[0]
                    dst_digits = re.findall(r"(\d+)", dst_name)[0]
                    dst_name = (
                        f"{dst_start}{dst_middle.rstrip('-')}-{int(dst_digits) :03d}"
                    )

                log.debug(f"Destination Data: {dst_name} {dst_slot} {dst_port}")
                dst_node_name = dst_name
                log.debug(f"Destination Name Lookup:  {dst_node_name}")
                node_type, dst_rename = get_node_type_yaml(
                    dst_name,
                    factory.lookup_mapper(),
                )
                log.debug(f"Destination Node Type Lookup:  {node_type}")

                if (
                    dst_name != dst_lldp["neighbor"] or dst_rename is not None
                ) and dst_name is not None:
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

                # Connect src_node and dst_node if possible
                if src_index is not None and dst_index is not None:
                    src_node = node_list[src_index]
                    dst_node = node_list[dst_index]
                    try:
                        connected = src_node.connect(
                            dst_node,
                            src_port=src_node_port,
                            dst_port=dst_node_port,
                        )
                    except Exception:
                        log.fatal(
                            click.secho(
                                f"Failed to connect {src_node.common_name()} "
                                + f"to {dst_node.common_name()} bi-directionally ",
                                fg="red",
                            ),
                        )
                        exit(1)
                    if connected:
                        log.info(
                            f"Connected {src_node.common_name()} to"
                            + f" {dst_node.common_name()} bi-directionally",
                        )
                    else:
                        log.error("")
                        click.secho(
                            f"Failed to connect {src_node.common_name()}"
                            + f" to {dst_node.common_name()} bi-directionally",
                            fg="red",
                        )
                        for node in node_list:
                            click.secho(
                                f"Node {node.id()} named {node.common_name()} connects "
                                + f"to {len(node.edges())} ports on nodes: {node.edges()}",
                            )
                        log.fatal(
                            f"Failed to connect {src_node.common_name()} "
                            + f"to {dst_node.common_name()} bi-directionally",
                        )
                        sys.exit(1)  # TODO: this should probably be an exception
    return node_list, warnings
