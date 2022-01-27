# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""CANU commands that validate the paddle."""
import json
from collections import defaultdict

import click
from click_help_colors import HelpColorsCommand

from canu.validate.shcd.shcd import node_list_warnings
from canu.validate.shcd.shcd import print_node_list
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
from network_modeling.NetworkPort import NetworkPort
from network_modeling.NodeLocation import NodeLocation


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--ccj",
    help="CCJ (CSM Cabling JSON) File containing system topology.",
    type=click.File("r"),
)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.pass_context
def paddle(ctx, ccj, out):
    """Validate a CCJ file.

    Pass in a CCJ file to validate that it works architecturally. The validation will ensure that spine switches,
    leaf switches, edge switches, and nodes all are connected properly.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        ccj: Paddle CCJ file
        out: Filename for the JSON Topology if requested.
    """
    ccj_json = json.load(ccj)
    architecture = ccj_json.get("architecture")

    if architecture is None:
        click.secho(
            "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ.",
            fg="red",
        )
        return

    # Create Node factory
    factory = NetworkNodeFactory(architecture_version=architecture)

    node_list, warnings = node_model_from_paddle(factory, ccj_json)

    print_node_list(node_list, "CCJ", out)

    node_list_warnings(node_list, warnings, out=out)


def node_model_from_paddle(factory, ccj_json):
    """Create a list of nodes from CCJ.

    Args:
        factory: Node factory object
        ccj_json: Paddle JSON file

    Returns:
        node_list: A list of created nodes
        warnings: A list of warnings
    """
    # Validate Paddle
    factory.validate_paddle(ccj_json)

    # Get list of nodes
    node_list = node_list_from_ccj_json(factory, ccj_json)

    # Add location and Connect Ports
    add_location_and_ports_from_ccj_json(node_list, ccj_json)

    warnings = defaultdict(list)
    # FUTURE ==> warnings = factory.check_connections()
    return node_list, warnings


def node_list_from_ccj_json(factory, ccj_json):
    """Generate a list of nodes from the topology in the CCJ file.

    Args:
        factory: Node factory object
        ccj_json: Paddle JSON file

    Returns:
        node_list: A list of created nodes
    """
    # Get topology
    topology = ccj_json.get("topology")

    node_list = []
    for node in topology:
        ccj_node = factory.generate_node_from_paddle(node)
        node_list.append(ccj_node)

    return node_list


def add_location_and_ports_from_ccj_json(node_list, ccj_json):
    """Add location and port connections to node list.

    Args:
        node_list: A list of created nodes
        ccj_json: Paddle JSON file
    """
    # Get topology
    topology = ccj_json.get("topology")

    node_dict_by_id = defaultdict()
    node_dict_by_name = defaultdict()

    for node in node_list:
        name = node.common_name()
        id = node.id()
        node_dict_by_name[name] = node
        node_dict_by_id[id] = node

    for entry in topology:
        common_name = entry["common_name"]
        src_node = node_dict_by_name[common_name]

        # Add location
        src_location = NodeLocation()
        src_location.location_from_paddle(entry["location"])
        src_node.location(src_location)

        # Connect Ports
        for port in entry["ports"]:
            src_node_port_number = port["port"]
            src_node_slot = port["slot"]
            src_node_port = NetworkPort(
                number=src_node_port_number,
                slot=src_node_slot,
            )

            dst_node_id = port["destination_node_id"]
            dst_node = node_dict_by_id[dst_node_id]

            dst_node_port_number = port["destination_port"]
            dst_node_slot = port["destination_slot"]
            dst_node_port = NetworkPort(
                number=dst_node_port_number,
                slot=dst_node_slot,
            )

            src_node.connect(
                dst_node,
                src_port=src_node_port,
                dst_port=dst_node_port,
                strict=True,
                bidirectional=False,
            )
