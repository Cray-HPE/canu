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
from network_modeling.NetworkPort import NetworkPort
from openpyxl import load_workbook


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
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
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
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
    elif architecture.lower() == "v1":
        architecture = "network_v1"

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
                if tmp_name == "sw-cdu-" and not name.startswith("sw-cdu"):
                    # cdu0sw1 --> sw-cdu-001
                    # cdu0sw2 --> sw-cdu-002
                    # cdu1sw1 --> sw-cdu-003
                    # cdu1sw2 --> sw-cdu-004
                    # cdu2sw1 --> sw-cdu-005
                    # cdu2sw2 --> sw-cdu-006
                    digits = re.findall(r"\d+", name)
                    tmp_id = int(digits[0]) * 2 + int(digits[1])
                else:
                    tmp_id = re.sub(
                        "^({})0*([1-9]*)".format(lookup_name), r"\2", name
                    ).strip("-")
                common_name = f"{tmp_name}{tmp_id:0>3}"
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


def validate_shcd_slot_data(cell, sheet, warnings, is_src_slot=False):
    """Ensure that a slot from the SHCD is a proper string.

    Args:
        cell: Cell object of a port from the SHCD spreadsheet
        sheet: SHCD spreadsheet sheet/tab name
        warnings: Existing list of warnings to post to
        is_src_slot: Boolean hack to work around SHCD inconsistencies.

    Returns:
        slot: A cleaned up string value from the cell
    """
    valid_slot_names = ["ocp", "pcie-slot1", "bmc", "mgmt", "onboard", "s", "pci", None]
    location = None
    if cell.value is not None:
        location = cell.coordinate
    slot = cell.value
    if isinstance(slot, str):
        slot = slot.strip()
        if slot and slot[0] == "s":
            warnings["shcd_slot_data"].append(sheet + ":" + location)
            log.warning(
                'Prepending the character "s" to a slot will not be allowed in the future. '
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot} and prefer pcie-slot1."
            )
            slot = "pcie-slot" + slot[1:]
        if slot and slot == "pci":
            warnings["shcd_slot_data"].append(sheet + ":" + location)
            log.warning(
                "The name pcie alone as a slot will not be allowed in the future"
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot} and prefer pcie-slot1."
            )
            slot = "pcie-slot1"
        if slot not in valid_slot_names:
            warnings["shcd_slot_data"].append(sheet + ":" + location)
            log.error(
                f"Slots must be named from the following list {valid_slot_names}."
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot}."
            )
        if not slot:
            slot = None
    # Awful hack around the convention that src slot can be blank and a bmc
    # is noted by port 3 when there is physically one port.
    # NOTE: This is required for the port to get fixed.
    if is_src_slot:
        if sheet == "HMN" and slot is None:
            warnings["shcd_slot_data"].append(f"{sheet}:{location}")
            log.warning(
                'A source slot of type "bmc" for servers or "mgmt" for switches must be specified in the HMN tab. '
                f"Please correct the SHCD for {sheet}:{location} with an empty value."
            )
            slot = "bmc"

    return slot


def validate_shcd_port_data(cell, sheet, warnings, is_src_port=False):
    """Ensure that a port from the SHCD is a proper integer.

    Args:
        cell: Cell object of a port from the SHCD spreadsheet
        sheet: SHCD spreadsheet sheet/tab name
        warnings: Existing list of warnings to post to
        is_src_port: (optional) Boolean triggers a hack to work around SHCD inconsistencies

    Returns:
        port: A cleaned up integer value from the cell
    """
    location = None
    if cell.value is not None:
        location = cell.coordinate
    port = cell.value
    if isinstance(port, str):
        port = port.strip()
        if not port:
            log.fatal(
                "A port number must be specified. "
                f"Please correct the SHCD for {sheet}:{location} with an empty value"
            )
            exit(1)
        if port[0] == "j":
            warnings["shcd_port_data"].append(f"{sheet}:{location}")
            log.warning(
                'Prepending the character "j" to a port will not be allowed in the future. '
                f"Please correct cell {sheet}:{location} in the SHCD with value {port}"
            )
            port = port[1:]
        if re.search(r"\D", port) is not None:
            log.fatal(
                "Port numbers must be integers. "
                f'Please correct in the SHCD for cell {sheet}:{location} with value "{port}"'
            )
            sys.exit(1)
        if is_src_port:
            # Awful hack around the convention that src slot can be blank and a bmc
            # is noted by port 3 when there is physically one port.
            # NOTE: This assumes that the slot has already been corrected to "bmc"
            if sheet == "HMN" and int(port) == 3:
                warnings["shcd_port_conventions"].append(f"{sheet}:{location}")
                log.warning(
                    f'Bad slot/port convention for port "j{port}" in location {sheet}:{location}.'
                    f'This should be slot "bmc" for servers and "mgmt" for switches, and port "1".'
                )
                port = 1

    if port is None:
        log.fatal(
            "A port number must be specified. "
            f"Please correct the SHCD for {sheet}:{location} with an empty value"
        )
        exit(1)

    return int(port)


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
            log.fatal("")
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
                log.fatal("")
                click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
                click.secho(f"{range_start}:{range_end}\n", fg="red")
                click.secho(
                    "Not enough columns selected. Expecting columns labeled:\n"
                    + "Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port\n"
                    + "Ensure that the upper left corner (Labeled 'Source'), and the lower right corner of the table is entered.",
                    fg="red",
                )
                sys.exit(1)

            if row[0].value == required_header[0]:
                log.debug(f"Expecting header with {expected_columns} columns")
                log.debug(f"Found header with {len(row)} columns")
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
                    log.fatal("")
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
                current_row = row[0].row
                log.debug(f"---- Working in sheet {sheet} on row {current_row} ----")
            except AttributeError:
                log.fatal("")
                click.secho(f"Bad range of cells entered for tab {sheet}.", fg="red")
                click.secho(f"{range_start}:{range_end}\n", fg="red")
                click.secho(
                    "Ensure the range entered does not contain a row of empty cells.",
                    fg="red",
                )
                sys.exit(1)

            tmp_slot = row[3]
            tmp_port = row[5]
            src_slot = validate_shcd_slot_data(
                tmp_slot, sheet, warnings, is_src_slot=True
            )
            src_port = validate_shcd_port_data(
                tmp_port, sheet, warnings, is_src_port=True
            )
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

            # src_xname = row[1].value + row[2].value
            # Create the source port for the node
            src_node_port = NetworkPort(number=src_port, slot=src_slot)
            # src_node_port = None

            # Cable destination
            dst_name = row[6].value.strip()
            # dst_xname = row[7].value + row[8].value
            # Create the destination slot and port for the node
            dst_slot = None  # There is no spreadsheet data and dst is always a switch
            dst_port = validate_shcd_port_data(row[10], sheet, warnings)
            log.debug(f"Destination Data:  {dst_name} {dst_slot} {dst_port}")
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

            # Create the destination port
            dst_node_port = NetworkPort(number=dst_port, slot=dst_slot)
            # dst_node_port = None

            # Connect src_node and dst_node if possible
            if src_index is not None and dst_index is not None:
                src_node = node_list[src_index]
                dst_node = node_list[dst_index]
                try:
                    connected = src_node.connect(
                        dst_node,
                        src_port=src_node_port,
                        dst_port=dst_node_port,
                        strict=True,
                    )
                except Exception as err:
                    log.fatal(err)
                    log.fatal(
                        click.secho(
                            f"Failed to connect {src_node.common_name()} "
                            f"to {dst_node.common_name()} bi-directionally "
                            f"while working on sheet {sheet}, row {current_row}.",
                            fg="red",
                        )
                    )
                    exit(1)

                if connected:
                    log.info(
                        f"Connected {src_node.common_name()} to {dst_node.common_name()} bi-directionally"
                    )
                else:
                    log.error(
                        click.secho(
                            f"Failed to connect {src_node.common_name()}"
                            f" to {dst_node.common_name()} bi-directionally",
                            fg="red",
                        )
                    )
                    for node in node_list:
                        click.secho(
                            f"Node {node.id()} named {node.common_name()} connects "
                            f"to {len(node.edges())} ports on nodes: {node.edges()}"
                        )
                    log.fatal(
                        f"Failed to connect {src_node.common_name()} "
                        f"to {dst_node.common_name()} bi-directionally"
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
                "\nNode type could not be determined for the following."
                "\nThese nodes are not currently included in the model."
                "\n(This may be a missing architectural definition/lookup or a spelling error)",
                fg="red",
            )
            click.secho(dash)
            nodes = set(warnings["node_type"])
            nodes = natsort.natsorted(nodes)
            has_mac = False
            for node in nodes:
                # If the string has a mac address in it, set to True
                if bool(re.search(r"(?:[0-9a-fA-F]:?){12}", str(node))):
                    has_mac = True
                click.secho(node, fg="bright_white")
            if has_mac is True:
                click.secho(
                    "Nodes that show up as MAC addresses might need to have LLDP enabled."
                )
        if warnings["zero_connections"]:
            click.secho(
                "\nThe following nodes have zero connections"
                "\n(The node type may not have been found or no connections are present)",
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
                if new_name == "":  # pragma: no cover
                    new_name = "(could not identify node)"
                nodes.add((x[0], new_name))
            nodes = natsort.natsorted(nodes)
            for node in nodes:
                click.secho(f"{node[0]} should be renamed {node[1]}", fg="bright_white")
        if warnings["shcd_port_data"]:
            click.secho(
                '\nSHCD port definitions are using a deprecated "j" prefix'
                '\n(Remove the prepended "j" in each cell to correct)',
                fg="red",
            )
            click.secho(dash)
            port_warnings = {}
            for x in warnings["shcd_port_data"]:
                sheet = x.split(":")[0]
                cell = x.split(":")[1]
                if sheet not in port_warnings:
                    port_warnings[sheet] = []
                port_warnings[sheet].append(cell)
            for entry in port_warnings:
                click.secho(f"{entry}:{port_warnings[entry]}", fg="bright_white")
                click.secho("")
        if warnings["shcd_port_conventions"]:
            click.secho(
                "\nSHCD port convention in the HMN tab is to use port 3 to represent BMCs."
                '\n(Correct the values in the following cells to use a Slot of "bmc" and a port of "1" for servers)'
                '\n(Correct the values in the following cells to use a Slot of "mgmt" and a port of "1" for switches)',
                fg="red",
            )
            click.secho(dash)
            slot_warnings = {}
            for x in warnings["shcd_port_conventions"]:
                sheet = x.split(":")[0]
                cell = x.split(":")[1]
                if sheet not in slot_warnings:
                    slot_warnings[sheet] = []
                slot_warnings[sheet].append(cell)
            for entry in slot_warnings:
                click.secho(f"{entry}:{slot_warnings[entry]}", fg="bright_white")
                click.secho("")
        if warnings["shcd_slot_data"]:
            click.secho(
                "\nSHCD slot definitions used are either deprecated, missing or incorrect."
                '\n(Correct values in the following cells to be appropriate values of ["bmc", "ocp", "pcie-slot1, "mgmt", None]',
                fg="red",
            )
            click.secho(dash)
            slot_warnings = {}
            for x in warnings["shcd_slot_data"]:
                sheet = x.split(":")[0]
                cell = x.split(":")[1]
                if sheet not in slot_warnings:
                    slot_warnings[sheet] = []
                slot_warnings[sheet].append(cell)
            for entry in slot_warnings:
                click.secho(f"{entry}:{slot_warnings[entry]}", fg="bright_white")
                click.secho("")


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
