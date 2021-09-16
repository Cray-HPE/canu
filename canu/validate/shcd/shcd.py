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
"""CANU commands that validate the shcd."""
from collections import defaultdict
import json
import logging
import os
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
import jsonschema
import natsort
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from network_modeling.NetworkPort import NetworkPort
from network_modeling.NodeLocation import NodeLocation
from openpyxl import load_workbook


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent

# Schema and Data files
json_schema_file = os.path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-system-topology-schema.json",
)
hardware_schema_file = os.path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-hardware-schema.yaml",
)
hardware_spec_file = os.path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-hardware.yaml",
)
architecture_schema_file = os.path.join(
    project_root,
    "network_modeling",
    "schema",
    "cray-network-architecture-schema.yaml",
)
architecture_spec_file = os.path.join(
    project_root,
    "network_modeling",
    "models",
    "cray-network-architecture.yaml",
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
)
@click.option(
    "--corners",
    help="The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.",
)
@click.option("--out", help="Output JSON model to a file", type=click.File("w"))
@click.option(
    "--log",
    "log_",
    help="Level of logging.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="ERROR",
)
@click.pass_context
def shcd(ctx, architecture, shcd, tabs, corners, out, log_):
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
        out: Filename for the JSON Topology if requested.
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

    if not tabs:
        wb = load_workbook(shcd, read_only=True)
        click.secho("What tabs would you like to check in the SHCD?")
        tab_options = wb.sheetnames
        for x in tab_options:
            click.secho(f"{x}", fg="green")

        tabs = click.prompt(
            "Please enter the tabs to check separated by a comma, e.g. 10G_25G_40G_100G,NMN,HMN.",
            type=str,
        )

    if corners:
        if len(tabs.split(",")) * 2 != len(corners.split(",")):
            log.error("")
            click.secho("Not enough corners.\n", fg="red")
            click.secho(
                f"Make sure each tab: {tabs.split(',')} has 2 corners.\n",
                fg="red",
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
                ),
            )
    else:
        for tab in tabs.split(","):
            click.secho(f"\nFor the Sheet {tab}", fg="green")
            range_start = click.prompt(
                "Enter the cell of the upper left corner (Labeled 'Source')",
                type=str,
            )
            range_end = click.prompt(
                "Enter the cell of the lower right corner",
                type=str,
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
        factory=factory,
        spreadsheet=shcd,
        sheets=sheets,
    )

    print_node_list(node_list, "SHCD")

    node_list_warnings(node_list, warnings)

    if out:
        json_output(node_list, out, json_schema_file)


def get_node_common_name(name, rack_number, rack_elevation, mapper):
    """Map SHCD device names to hostname.

    Args:
        name: A string from SHCD representing the device name
        rack_number: A string for rack the device is in (e.g. x1001)
        rack_elevation: A string for the position of the device in the rack (e.g. u19)
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
                elif node[1].find("cmm") != -1:
                    tmp_name = node[1] + "-" + rack_number + "-"
                elif node[1].find("cec") != -1:
                    tmp_name = node[1] + "-" + rack_number + "-"
                elif node[1].find("pdu") != -1:
                    tmp_name = node[1] + "-" + rack_number + "-"
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
                        "^({})0*([1-9]*)".format(lookup_name),
                        r"\2",
                        name,
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
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot} and prefer pcie-slot1.",
            )
            slot = "pcie-slot" + slot[1:]
        if slot and slot == "pci":
            warnings["shcd_slot_data"].append(sheet + ":" + location)
            log.warning(
                "The name pcie alone as a slot will not be allowed in the future"
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot} and prefer pcie-slot1.",
            )
            slot = "pcie-slot1"
        if slot not in valid_slot_names:
            warnings["shcd_slot_data"].append(sheet + ":" + location)
            log.warning(
                f"Slots must be named from the following list {valid_slot_names}."
                f"Please correct cell {sheet}:{location} in the SHCD with value {slot}.",
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
                f"Please correct the SHCD for {sheet}:{location} with an empty value.",
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
                f"Please correct the SHCD for {sheet}:{location} with an empty value",
            )
            exit(1)
        if port[0] == "j":
            warnings["shcd_port_data"].append(f"{sheet}:{location}")
            log.warning(
                'Prepending the character "j" to a port will not be allowed in the future. '
                f"Please correct cell {sheet}:{location} in the SHCD with value {port}",
            )
            port = port[1:]
        if re.search(r"\D", port) is not None:
            log.fatal(
                "Port numbers must be integers. "
                f'Please correct in the SHCD for cell {sheet}:{location} with value "{port}"',
            )
            sys.exit(1)
        if int(port) < 1:
            log.fatal(
                "Ports numbers must be greater than 1. Port numbering must begin at 1. "
                f'Please correct in the SHCD for cell {sheet}:{location} with value "{port}"',
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
                    f'This should be slot "bmc" for servers and "mgmt" for switches, and port "1".',
                )
                port = 1

    if port is None:
        log.fatal(
            "A port number must be specified. "
            f"Please correct the SHCD for {sheet}:{location} with an empty value",
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

        log.info("---------------------------------------------")
        log.info(f"Working on tab/worksheet {sheet}")
        log.info("---------------------------------------------")
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

        #
        # Process Headers
        #
        required_header = [
            "Source",
            "Rack",
            "Location",
            "Slot",
            "Port",
            "Destination",
            "Rack",
            "Location",
            "Port",
        ]

        header = block[0]
        if len(header) == 0 or len(header) < len(required_header):
            log.fatal("")
            click.secho(
                f"Bad range of cells entered for tab {sheet}:{range_start}:{range_end}.",
                fg="red",
            )
            click.secho(
                "Not enough columns exist.\n"
                "Columns must exist in the following order, but may have other columns in between:\n"
                f"{required_header}\n"
                "Ensure that the upper left corner (Labeled 'Source'), and the lower right corner of the table is entered.",
                fg="red",
            )
            sys.exit(1)

        log.info(
            f"Expecting header with {len(required_header):>2} columns: {required_header}",
        )
        log.info(
            f"Found header with     {len(header):>2} columns: {[x.value for x in header]}",
        )
        log.info("Mapping required columns to actual.")

        start_index = 0
        for required_index in range(len(required_header)):
            found = None
            for current_index in range(start_index, len(header)):
                if header[current_index].value == required_header[required_index]:
                    found = current_index
                    break
                else:
                    found = None
                    continue
            if found is not None:
                log.info(
                    f"Required header column {required_header[required_index]} "
                    f"found in spreadsheet cell {header[current_index].coordinate}",
                )
                required_header[required_index] = found
                start_index = current_index + 1
                found = None
                continue
            else:
                log.error("")
                click.secho(
                    f"On tab {sheet}, header column {required_header[required_index]} not found.",
                    fg="red",
                )
                log.fatal("")
                click.secho(
                    f"On tab {sheet}, the header is formatted incorrectly.\n"
                    "Columns must exist in the following order, but may have other columns in between:\n"
                    f"{required_header}",
                    fg="red",
                )
                sys.exit(1)

        #
        # Process Data
        #
        block = block[1:]
        for row in block:
            # Cable source
            try:
                current_row = row[required_header[0]].row
                log.debug(f"---- Working in sheet {sheet} on row {current_row} ----")
                src_name = row[required_header[0]].value.strip()
                tmp_slot = row[required_header[3]]
                tmp_port = row[required_header[4]]
                src_rack = None
                if row[required_header[1]].value:
                    src_rack = row[required_header[1]].value.strip()
                src_elevation = None
                if row[required_header[2]].value:
                    src_elevation = row[required_header[2]].value.strip()
                src_location = NodeLocation(src_rack, src_elevation)
            except AttributeError:
                log.fatal("")
                click.secho(
                    f"Bad cell data or range of cells entered for sheet {sheet} in row {current_row} for source data.",
                    fg="red",
                )
                click.secho(
                    "Ensure the range entered does not contain empty cells.",
                    fg="red",
                )
                sys.exit(1)

            src_slot = validate_shcd_slot_data(
                tmp_slot,
                sheet,
                warnings,
                is_src_slot=True,
            )
            src_port = validate_shcd_port_data(
                tmp_port,
                sheet,
                warnings,
                is_src_port=True,
            )
            log.debug(f"Source Data:  {src_name} {src_slot} {src_port}")
            node_name = get_node_common_name(
                src_name,
                src_rack,
                src_elevation,
                factory.lookup_mapper(),
            )
            log.debug(f"Source Name Lookup:  {node_name}")
            log.debug(f"Source rack {src_rack} in location {src_elevation}")
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
                    src_node.location(src_location)

                    node_list.append(src_node)
                    node_name_list.append(node_name)
                else:
                    log.debug(
                        f"Node {node_name} already exists, skipping node creation.",
                    )

                src_index = node_name_list.index(node_name)
            else:
                warnings["node_type"].append(src_name)
                log.warning(
                    f"Node type for {src_name} cannot be determined by node type ({node_type}) or node name ({node_name})",
                )

            # Create the source port for the node
            src_node_port = NetworkPort(number=src_port, slot=src_slot)

            # Cable destination
            try:
                dst_name = row[required_header[5]].value.strip()
                dst_slot = None  # dst is always a switch
                dst_port = validate_shcd_port_data(
                    row[required_header[8]],
                    sheet,
                    warnings,
                )
                dst_rack = None
                if row[required_header[6]].value:
                    dst_rack = row[required_header[6]].value.strip()
                dst_elevation = None
                if row[required_header[7]].value:
                    dst_elevation = row[required_header[7]].value.strip()
                dst_location = NodeLocation(dst_rack, dst_elevation)
            except AttributeError:
                log.fatal("")
                click.secho(
                    f"Bad cell data or range of cells entered for sheet {sheet} in row {current_row} for destination data.",
                    fg="red",
                )
                click.secho(
                    "Ensure the range entered does not contain empty cells.",
                    fg="red",
                )
                sys.exit(1)

            log.debug(f"Destination Data:  {dst_name} {dst_slot} {dst_port}")
            node_name = get_node_common_name(
                dst_name,
                dst_rack,
                dst_elevation,
                factory.lookup_mapper(),
            )
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
                    dst_node.location(dst_location)

                    node_list.append(dst_node)
                    node_name_list.append(node_name)
                else:
                    log.debug(
                        f"Node {node_name} already exists, skipping node creation",
                    )

                dst_index = node_name_list.index(node_name)

            else:
                warnings["node_type"].append(dst_name)

                log.warning(
                    f"Node type for {dst_name} cannot be determined by node type ({node_type}) or node name ({node_name})",
                )

            # Create the destination port
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
                        ),
                    )
                    exit(1)

                if connected:
                    log.info(
                        f"Connected {src_node.common_name()} to {dst_node.common_name()} bi-directionally",
                    )
                else:
                    log.error(
                        click.secho(
                            f"Failed to connect {src_node.common_name()}"
                            f" to {dst_node.common_name()} bi-directionally",
                            fg="red",
                        ),
                    )
                    for node in node_list:
                        click.secho(
                            f"Node {node.id()} named {node.common_name()} connects "
                            f"to {len(node.edges())} ports on nodes: {node.edges()}",
                        )
                    log.fatal(
                        f"Failed to connect {src_node.common_name()} "
                        f"to {dst_node.common_name()} bi-directionally",
                    )
                    sys.exit(1)  # TODO: this should probably be an exception
    wb.close()

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
                    "Nodes that show up as MAC addresses might need to have LLDP enabled.",
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
            f"{node.id()}: {node.common_name()} connects to {len(node.edges())} nodes: {node.edges()}",
        )

    dash = "-" * 60
    click.echo("\n")
    click.secho(f"{title} Port Usage", fg="bright_white")
    click.echo(dash)

    for node in node_list:
        click.echo(f"{node.id()}: {node.common_name()} has the following port usage:")

        unused_block = []
        logical_index = 1
        for port in node.ports():
            if port is None:
                unused_block.append(logical_index)
                logical_index += 1
                continue
            if unused_block:
                if len(unused_block) == 1:
                    port_string = f"{unused_block[0]:02}==>UNUSED"
                else:
                    port_string = f"{unused_block[0]:02}-{unused_block[len(unused_block)-1]:02}==>UNUSED"
                unused_block = []  # reset
                click.secho(f"        {port_string}", fg="green")
            destination_node_name = [
                x.common_name()
                for x in node_list
                if x.id() == port["destination_node_id"]
            ]
            destination_node_name = destination_node_name[0]
            destination_port_slot = None
            if port["destination_slot"] is None:
                destination_port_slot = f'{port["destination_port"]}'
            else:
                destination_port_slot = (
                    f'{port["destination_slot"]}:{port["destination_port"]}'
                )
            if port["slot"] is None:
                port_string = f'{port["port"]:>02}==>{destination_node_name}:{destination_port_slot}'
            else:
                port_string = f'{port["slot"]}:{port["port"]}==>{destination_node_name}:{destination_port_slot}'
            click.echo(f"        {port_string}")
            logical_index += 1


def json_output(node_list, out, json_schema_file):
    """Create a schema-validated JSON Topology file from the model."""
    model = []
    for node in node_list:
        model.append(node.serialize())

    with open(json_schema_file, "r") as file:
        json_schema = json.load(file)

    validator = jsonschema.Draft7Validator(json_schema)

    try:
        validator.check_schema(json_schema)
    except jsonschema.exceptions.SchemaError as err:
        click.secho(
            f"Schema {json_schema_file} is invalid: {[x.message for x in err.context]}\n"
            "Cannot generate and write Topology JSON file.",
            fg="red",
        )
        exit(1)

    errors = sorted(validator.iter_errors(model), key=str)
    if errors:
        click.secho("Topology JSON failed schema checks:", fg="red")
        for error in errors:
            click.secho(f"    {error.message} in {error.absolute_path}", fg="red")
        exit(1)

    json_model = json.dumps(model, indent=2)
    click.echo(json_model, file=out)
