"""CANU commands that validate the shcd."""
from collections import defaultdict
import logging
import os
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
import natsort
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from openpyxl import load_workbook


# Get project root directory
prog = __file__
project_root = Path(__file__).resolve().parent.parent.parent.parent

# Schema and Data files
hardware_schema_file = os.path.join(
    project_root, "network_modeling", "schema", "cray-network-hardware-schema.yaml"
)
hardware_spec_file = os.path.join(
    project_root, "network_modeling", "models", "cray-network-hardware.yaml"
)
architecture_schema_file = os.path.join(
    project_root, "network_modeling", "schema", "cray-network-architecture-schema.yaml"
)
architecture_spec_file = os.path.join(
    project_root, "network_modeling", "models", "cray-network-architecture.yaml"
)

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
@click.option(
    "--shcd",
    help="SHCD file",
    type=click.File("rb"),
    required=True,
)
@click.option(
    "--tabs",
    help="The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.",
    required=True,
)
@click.option(
    "--corners",
    help="The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.",
    # required=True,
)
@click.option(
    "--log",
    "log_",
    help="Level of logging.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    # required=True,
    default="ERROR",
)
@click.pass_context
def shcd(ctx, architecture, shcd, tabs, corners, log_):
    """Validate a SHCD file.

    Pass in a SHCD file to validate that it works architecturally. The validation will ensure that spine switches,
    leaf switches, edge switches, and nodes all are connected properly.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        architecture: Shasta architecture
        shcd: SHCD file
        tabs: The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.
        corners: The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.
        log_: Level of logging.
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

    if architecture.lower() == "full":
        architecture = "network_v2"
    elif architecture.lower() == "tds":
        architecture = "network_v2_tds"

    sheets = []

    if corners:
        if len(tabs.split(",")) * 2 != len(corners.split(",")):
            log.error("")
            click.secho("Not enough corners.\n", fg="red")
            click.secho(
                f"Make sure each tab: {tabs.split(',')} has 2 corners.\n", fg="red"
            )
            click.secho(
                f"There were {len(corners.split(','))} corners entered, but there should be {len(tabs.split(',')) * 2}.",
                fg="red",
            )
            click.secho(
                f"{corners}\n",
                fg="red",
            )
            return

        # Each tab should have 2 corners entered in comma separated
        for i in range(len(tabs.split(","))):
            # 0 -> 0,1
            # 1 -> 2,3
            # 2 -> 4,5

            sheets.append(
                (
                    tabs.split(",")[i],
                    corners.split(",")[i * 2].strip(),
                    corners.split(",")[i * 2 + 1].strip(),
                )
            )
    else:
        for tab in tabs.split(","):
            click.secho(f"\nFor the Sheet {tab}", fg="green")
            range_start = click.prompt(
                "Enter the cell of the upper left corner (Labeled 'Source')",
                type=str,
            )
            range_end = click.prompt(
                "Enter the cell of the lower right corner", type=str
            )
            sheets.append((tab, range_start, range_end))

    # Create Node factory
    factory = NetworkNodeFactory(
        hardware_schema=hardware_schema_file,
        hardware_data=hardware_spec_file,
        architecture_schema=architecture_schema_file,
        architecture_data=architecture_spec_file,
        architecture_version=architecture,
    )

    node_list, warnings = node_model_from_shcd(
        factory=factory, spreadsheet=shcd, sheets=sheets
    )

    print_node_list(node_list, "SHCD")

    node_list_warnings(node_list, warnings)


def get_node_common_name(name, mapper):
    """Map SHCD device names to hostname.

    Args:
        name: A string from SHCD representing the device name
        mapper: An array of tuples (SHCD name, hostname, device type)

    Returns:
        common_name: A string of the hostname
    """
    common_name = None
    for node in mapper:
        for lookup_name in node[0]:
            if re.match("^{}".format(lookup_name.strip()), name):
                # One naming convention for switches, another for else.
                tmp_name = None
                if node[1].find("sw-") != -1:
                    tmp_name = node[1] + "-"
                else:
                    tmp_name = node[1]
                tmp_id = re.sub("^({})0*([1-9]*)".format(lookup_name), r"\2", name)
                common_name = "{}{:0>3}".format(tmp_name, tmp_id)
                return common_name
    return common_name


def get_node_type(name, mapper):
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


def node_model_from_shcd(factory, spreadsheet, sheets):
    """Create a list of nodes from SHCD.

    Args:
        factory: Node factory object
        spreadsheet: The SHCD spreadsheet
        sheets: An array of tabs and their corners on the spreadsheet

    Returns:
        node_list: A list of created nodes
        warnings: A list of warnings
    """
    # Generated nodes
    node_list = []
    node_name_list = []
    warnings = defaultdict(list)

    wb = load_workbook(spreadsheet, read_only=True)

    for tab in sheets:

        sheet = tab[0]
        range_start = tab[1]
        range_end = tab[2]

        log.info("----------------------------------------")
        log.info(f"Working on tab/worksheet {sheet}")
        log.info("----------------------------------------")
        log.info("")

        if sheet not in wb.sheetnames:
            log.error("")
            click.secho(f"Tab {sheet} not found in {spreadsheet.name}\n", fg="red")
            click.secho(f"Available tabs: {wb.sheetnames}", fg="red")
            sys.exit(1)

        ws = wb[sheet]
        try:
            block = ws[range_start:range_end]
        except ValueError:
            log.error("")
            click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
            click.secho(f"{range_start}:{range_end}\n", fg="red")
            click.secho(
                "Ensure that the upper left corner (Labeled 'Source'), and the lower right corner of the table is entered.",
                fg="red",
            )
            sys.exit(1)

        required_header = [
            "Source",
            "Rack",
            "Location",
            "Slot",
            None,
            "Port",
            "Destination",
            "Rack",
            "Location",
            None,
            "Port",
        ]
        expected_columns = len(required_header)

        for row in block:
            if len(row) == 0 or len(row) < expected_columns:
                log.error("")
                click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
                click.secho(f"{range_start}:{range_end}\n", fg="red")
                click.secho(
                    "Ensure that the upper left corner (Labeled 'Source'), and the lower right corner of the table is entered.",
                    fg="red",
                )
                sys.exit(1)

            if row[0].value == required_header[0]:
                log.debug(f"Expecting header with {expected_columns} columns")
                log.debug(f"Header found with {len(row)} columns")
                error = False
                for i in range(expected_columns):
                    if row[i].value != required_header[i]:
                        log.error("")
                        click.secho(
                            f"On tab {sheet}, header column {required_header[i]} not found",
                            fg="red",
                        )
                        error = True
                    else:
                        log.debug(f"Header column {required_header[i]} found")

                if error:
                    log.error("")
                    click.secho(
                        f"On tab {sheet}, the header is formatted incorrectly.\n",
                        fg="red",
                    )
                    click.secho("The columns should be labeled:", fg="red")
                    click.secho(
                        "Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port",
                        fg="red",
                    )
                    sys.exit(1)
                continue

            # Cable source
            try:
                src_name = row[0].value.strip()
            except AttributeError:
                log.error("")
                click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
                click.secho(f"{range_start}:{range_end}\n", fg="red")
                click.secho(
                    "Ensure the range entered does not contain a row of empty cells.",
                    fg="red",
                )
                sys.exit(1)
            # src_xname = row[1].value + row[2].value
            src_slot = row[3].value
            src_port = row[5].value
            log.debug(f"Source Data:  {src_name} {src_slot} {src_port}")
            node_name = get_node_common_name(src_name, factory.lookup_mapper())
            log.debug(f"Source Name Lookup:  {node_name}")
            node_type = get_node_type(src_name, factory.lookup_mapper())
            log.debug(f"Source Node Type Lookup:  {node_type}")

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
            dst_name = row[6].value.strip()
            # dst_xname = row[7].value + row[8].value
            dst_port = row[10].value

            log.debug(f"Destination Data:  {dst_name} {dst_port}")
            node_name = get_node_common_name(dst_name, factory.lookup_mapper())
            log.debug(f"Destination Name Lookup:  {node_name}")
            node_type = get_node_type(dst_name, factory.lookup_mapper())
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
                        f"Connected {node_list[src_index].common_name()} to {node_list[dst_index].common_name()} bi-directionally"
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


def node_list_warnings(node_list, warnings):
    """Print the warnings found while validating the SHCD.

    Args:
        node_list: A list of nodes
        warnings: A dictionary of warnings
    """
    dash = "-" * 60
    # Generate warnings
    # Additional warnings about the data will be entered here
    for node in node_list:
        if len(node.edges()) == 0:
            warnings["zero_connections"].append(node.common_name())

    # Print Warnings
    if warnings:
        click.secho("\nWarnings", fg="red")
        if warnings["node_type"]:
            click.secho(
                "\nNode type could not be determined for the following",
                fg="red",
            )
            click.secho(dash)
            nodes = set(warnings["node_type"])
            nodes = natsort.natsorted(nodes)
            for node in nodes:
                click.secho(node, fg="bright_white")
            click.secho(
                "Nodes that show up as MAC addresses might need to have LLDP enabled."
            )
        if warnings["zero_connections"]:
            click.secho(
                "\nThe following nodes have zero connections",
                fg="red",
            )
            click.secho(dash)
            nodes = set(warnings["zero_connections"])
            nodes = natsort.natsorted(nodes)
            for node in nodes:
                click.secho(node, fg="bright_white")
        if warnings["rename"]:
            click.secho(
                "\nThe following nodes should be renamed",
                fg="red",
            )
            click.secho(dash)
            nodes = set()
            for x in warnings["rename"]:
                new_name = x[1]
                if new_name == "":
                    new_name = "(could not identify node)"
                nodes.add((x[0], new_name))
            nodes = natsort.natsorted(nodes)
            for node in nodes:
                click.secho(f"{node[0]} should be renamed {node[1]}", fg="bright_white")


def print_node_list(node_list, title):
    """Print the nodes found in the SHCD.

    Args:
        node_list: A list of nodes
        title: Title to be printed
    """
    dash = "-" * 60
    click.echo("\n")
    click.secho(f"{title} Node Connections", fg="bright_white")
    click.echo(dash)

    for node in node_list:
        click.echo(
            f"{node.id()}: {node.common_name()} connects to {len(node.edges())} nodes: {node.edges()}"
        )
