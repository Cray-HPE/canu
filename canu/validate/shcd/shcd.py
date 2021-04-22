"""CANU commands that validate the shcd."""
import logging
import os
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from openpyxl import load_workbook


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

names_mapper = {}

names_mapper["network_v2"] = [
    ("mn", "ncn-m", "river_ncn_node_2_port"),
    ("wn", "ncn-w", "river_ncn_node_2_port"),
    ("sn", "ncn-s", "river_ncn_node_4_port"),
    ("uan", "uan", "river_ncn_node_4_port"),
    ("Ln", "ln", "river_ncn_node_4_port"),
    ("sw-cdu", "sw-cdu", "mountain_compute_leaf"),
    ("sw-smn", "sw-leaf-bmc", "river_bmc_leaf"),
    ("sw-25g", "sw-leaf", "river_ncn_leaf"),
    ("sw-100g", "sw-spine", "spine"),
    ("sw-edge", "sw-edge", "customer_edge_router"),
]
names_mapper["network_v2_tds"] = [
    ("mn", "ncn-m", "river_ncn_node_2_port"),
    ("wn", "ncn-w", "river_ncn_node_2_port"),
    ("sn", "ncn-s", "river_ncn_node_4_port"),
    ("uan", "uan", "river_ncn_node_4_port"),
    ("sw-cdu", "sw-cdu", "mountain_compute_leaf"),
    ("sw-smn", "sw-leaf-bmc", "river_bmc_leaf"),
    ("sw-25g", "sw-spine", "spine"),
    ("sw-100g", "sw-edge", "customer_edge_router"),
]


log = logging.getLogger("validate_shcd")


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["network_v1", "network_v2", "network_v2_tds", "small"]),
    help="Shasta architecture",
    required=True,
)
@click.option(
    "--shcd",
    help="SHCD file",
    type=click.File("rb"),
    required=True,
)
@click.option(
    "--tabs",
    help="The tabs on the SHCD file to check.",
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
    """Report the firmware of an Aruba switch (API v10.04) on the network."""
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

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
        for i in range(len(tabs.split(","))):
            # 0 -> 0,1
            # 1 -> 2,3
            # 2 -> 4,5

            sheets.append(
                (
                    tabs.split(",")[i],
                    corners.split(",")[i * 2],
                    corners.split(",")[i * 2 + 1],
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
    factory = NetworkNodeFactory.get_factory(
        hardware_schema=hardware_schema_file,
        hardware_data=hardware_spec_file,
        architecture_schema=architecture_schema_file,
        architecture_data=architecture_spec_file,
        architecture_version=architecture,
    )

    node_list = node_model_from_shcd(
        factory=factory, spreadsheet=shcd, sheets=sheets, architecture=architecture
    )

    print_node_list(node_list)


def get_node_common_name(name, mapper):
    """Map SHCD device names to hostname.

    :param name: A string from SHCD representing the device name
    :param mapper: An array of tuples (SHCD name, hostname, device type)

    :param out: A string of the hostname
    """
    common_name = None
    for node in mapper:
        if re.match("^{}".format(node[0].strip()), name):
            # One naming convention for switches, another for else.
            tmp_name = None
            if node[1].find("sw-") != -1:
                tmp_name = node[1] + "-"
            else:
                tmp_name = node[1]
            tmp_id = re.sub("^({})0*([1-9]*)".format(node[0]), r"\2", name)
            common_name = "{}{:0>3}".format(tmp_name, tmp_id)
            break
    return common_name


def get_node_type(name, mapper):
    """Map SHCD device name to device type.

    :param name: A string from SHCD representing the device name
    :param mapper: An array of tuples (SHCD name, hostname, device type)

    :param out: A string with the device type
    """
    node_type = None
    for node in mapper:
        if re.match("^{}".format(node[0].strip()), name):
            node_type = node[2]
    return node_type


def node_model_from_shcd(factory, spreadsheet, sheets, architecture):
    """Create a list of nodes from SHCD.

    :param factory: Node factory object
    :param spreadsheet: The SHCD spreadsheet
    :param sheets: An array of tabs and their corners on the spreadsheet
    :param architecture: The architecture version of the system

    :param out: A list of created nodes
    """
    # Generated nodes
    node_list = []
    node_name_list = []

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
            # if len(row) != expected_columns:
            #     log.error("")
            #     click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
            #     click.secho(f"{range_start}:{range_end}\n", fg="red")
            #     click.secho(
            #         f"Ensure the range entered contains the {expected_columns} header columns from 'Source' to 'Port'.",
            #         fg="red",
            #     )
            #     sys.exit(1)

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

                continue  # Skip this row - prevent from further processing

            #
            # Cable source
            #
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
            node_name = get_node_common_name(src_name, names_mapper[architecture])
            log.debug(f"Source Name Lookup:  {node_name}")
            node_type = get_node_type(src_name, names_mapper[architecture])
            log.debug(f"Source Node Type Lookup:  {node_type}")

            #
            # Created src node if possible and required
            #
            src_node = None
            src_index = None
            if node_type and node_name:
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
                log.warning(
                    f"Node type for {src_name} cannot be determined by node type ({node_type}) or node name ({node_name})"
                )

            #
            # Cable destination
            #
            dst_name = row[6].value.strip()
            # dst_xname = row[7].value + row[8].value
            dst_port = row[10].value

            log.debug(f"Destination Data:  {dst_name} {dst_port}")
            node_name = get_node_common_name(dst_name, names_mapper[architecture])
            log.debug(f"Destination Name Lookup:  {node_name}")
            node_type = get_node_type(dst_name, names_mapper[architecture])
            log.debug(f"Destination Node Type Lookup:  {node_type}")

            #
            # Created destination node if possible and required
            #
            dst_node = None
            dst_index = None
            if node_type and node_name:
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
                log.warning(
                    f"Node type for {dst_name} cannot be determined by node type ({node_type}) or node name ({node_name})"
                )

            #
            # Connect the nodes if possible
            #
            # use the lists
            if src_index and dst_index:
                connected = node_list[src_index].connect(node_list[dst_index])
                if connected:
                    log.info(
                        f"Connected {node_list[src_index].common_name()} to {node_list[dst_index].common_name()} bi-directionally"
                    )
                else:
                    log.error("")
                    click.secho(
                        f"Failed to connect {node_list[src_index].common_name()}"
                        + " to {node_list[dst_index].common_name()} bi-directionally",
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
    return node_list


def print_node_list(node_list):
    """Print the nodes found in the SHCD.

    :param node_list: A list of nodes
    """
    print("\n")
    for node in node_list:
        print(
            f"{node.id()}: {node.common_name()} connects to {len(node.edges())} nodes: {node.edges()}"
        )
