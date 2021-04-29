"""CANU commands that validate the shcd."""
from collections import defaultdict
import ipaddress
import logging
import os
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import requests
import ruamel.yaml

from canu.switch.cabling.cabling import get_lldp
from canu.validate.shcd.shcd import node_list_warnings, print_node_list

yaml = ruamel.yaml.YAML()


# Get project root directory
prog = __file__
project_root = Path(__file__).resolve().parent.parent.parent.parent

# Schema and Data files
hardware_schema_file = os.path.join(
    project_root, "schema", "cray-network-hardware-schema.yaml"
)
hardware_spec_file = os.path.join(
    project_root, "network_models", "cray-network-hardware.yaml"
)
architecture_schema_file = os.path.join(
    project_root, "schema", "cray-network-architecture-schema.yaml"
)
architecture_spec_file = os.path.join(
    project_root, "network_models", "cray-network-architecture.yaml"
)

canu_cache_file = os.path.join(project_root, "canu_cache.yaml")


log = logging.getLogger("validate_shcd")


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS"], case_sensitive=False),
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
                    get_lldp(str(ip), credentials, True)

                except requests.exceptions.HTTPError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}, "
                            + "check that this IP is an Aruba switch, or check the username or password.",
                        ]
                    )
                except requests.exceptions.ConnectionError:
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip},"
                            + " check the IP address and try again.",
                        ]
                    )
                except requests.exceptions.RequestException:  # pragma: no cover
                    errors.append(
                        [
                            str(ip),
                            f"Error connecting to switch {ip}.",
                        ]
                    )

    # Create Node factory
    factory = NetworkNodeFactory.get_factory(
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
    """
    node_type = None
    for node in mapper:
        for lookup_name in node[0]:
            if re.match("^{}".format(lookup_name.strip()), name):
                node_type = node[2]
                return node_type
    return node_type


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

                # src_port = port
                log.debug(f"Source Data: {src_name}")
                # If starts with 'sw-' then add an extra '-' before the number, and convert to 3 digit
                node_name = src_name
                if node_name.startswith("sw-"):
                    split_name = re.findall(r"(\w+?)(\d+)", node_name)[0]
                    node_name = "sw-{}-{:03d}".format(split_name[0], int(split_name[1]))

                log.debug(f"Source Name Lookup: {node_name}")
                node_type = get_node_type_yaml(src_name, factory.lookup_mapper())
                log.debug(f"Source Node Type Lookup: {node_type}")

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
                        log.debug(f"Node {node_name} already exists, skipping...")

                    src_index = node_name_list.index(node_name)
                else:
                    warnings["node_type"].append(src_name)
                    log.warning(
                        f"Node type for {src_name} cannot be determined by node type ({node_type}) or node name ({node_name})"
                    )

                # Cable destination
                dst = switch["cabling"][port][0]

                # If starts with 'sw-' then add an extra '-' before the number, and convert to 3 digit
                dst_name = dst["neighbor"]
                if dst_name.startswith("sw-"):
                    split_name = re.findall(r"(\w+?)(\d+)", dst_name)[0]
                    dst_name = "sw-{}-{:03d}".format(split_name[0], int(split_name[1]))
                # dst_port = dst["neighbor_port"]

                log.debug(f"Destination Data: {dst_name}")
                node_name = dst_name
                log.debug(f"Destination Name Lookup:  {node_name}")
                node_type = get_node_type_yaml(dst_name, factory.lookup_mapper())
                log.debug(f"Destination Node Type Lookup:  {node_type}")

                # Create dst_node if it does not exist
                dst_node = None
                dst_index = None
                if node_type is not None and node_name is not None:
                    if node_name not in node_name_list:
                        log.info(f"Creating new node {node_name} of type {node_type}")
                        try:
                            dst_node = factory.generate_node(node_type)
                        except Exception as e:
                            print(e)
                            sys.exit(1)

                        dst_node.common_name(node_name)

                        node_list.append(dst_node)
                        node_name_list.append(node_name)
                    else:
                        log.debug(f"Node {node_name} already exists, skipping...")

                    dst_index = node_name_list.index(node_name)

                else:
                    warnings["node_type"].append(dst_name)

                    log.warning(
                        f"Node type for {dst_name} cannot be determined by node type ({node_type}) or node name ({node_name})"
                    )

                # Connect src_node and dst_node if possible
                if src_index is not None and dst_index is not None:
                    connected = node_list[src_index].connect(node_list[dst_index])
                    if connected:
                        log.info(
                            f"Connected {node_list[src_index].common_name()} to"
                            + f" {node_list[dst_index].common_name()} bi-directionally"
                        )
                    else:
                        log.error("")
                        click.secho(
                            f"Failed to connect {node_list[src_index].common_name()}"
                            + f" to {node_list[dst_index].common_name()} bi-directionally",
                            fg="red",
                        )
                        for node in node_list:
                            click.secho(
                                f"Node {node.id()} named {node.common_name()} connects "
                                + f"to {len(node.edges())} ports on nodes: {node.edges()}"
                            )
                        log.fatal(
                            f"Failed to connect {node_list[src_index].common_name()} "
                            + f"to {node_list[dst_index].common_name()} bi-directionally"
                        )
                        sys.exit(1)  # TODO: this should probably be an exception
    return node_list, warnings
