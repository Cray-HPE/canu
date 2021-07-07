"""CANU switch config commands."""
from collections import defaultdict
import json
import os
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from jinja2 import Environment, FileSystemLoader
import natsort
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import ruamel.yaml
import urllib3

from canu.validate.shcd.shcd import node_model_from_shcd

yaml = ruamel.yaml.YAML()

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

canu_cache_file = os.path.join(project_root, "canu", "canu_cache.yaml")

# Import templates
network_templates_folder = os.path.join(
    project_root, "network_modeling", "configs", "templates"
)
env = Environment(
    loader=FileSystemLoader(network_templates_folder),
    # trim_blocks=True,
)


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
    "--name",
    "switch_name",
    required=True,
    help="The name of the switch to generate config e.g. 'sw-spine-001'",
    prompt="Switch Name",
)
# @click.option("--ip", required=True, help="The IP address of the switch")
# @click.option("--username", default="admin", show_default=True, help="Switch username")
# @click.option(
#     "--password",
#     prompt=True,
#     hide_input=True,
#     confirmation_prompt=False,
#     help="Switch password",
# )
@click.option("--csi-folder", help="Directory containing the CSI json file")
@click.option(
    "--out", help="Output results to a file", type=click.File("w"), default="-"
)
@click.pass_context
def config(
    ctx,
    architecture,
    shcd,
    tabs,
    corners,
    switch_name,
    csi_folder,
    out
    # ip, username, password
):
    """Switch config commands.

    Configure Aruba switch.
    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        architecture: Shasta architecture
        shcd: SHCD file
        tabs: The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.
        corners: The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.
        switch_name: Switch name
        csi_folder: Directory containing the CSI json file
        out: Name of the output file
    """
    if architecture.lower() == "full":
        architecture = "network_v2"
    elif architecture.lower() == "tds":
        architecture = "network_v2_tds"

    # SHCD Parsing
    sheets = []

    if corners:
        if len(tabs.split(",")) * 2 != len(corners.split(",")):
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

    # credentials = {"username": username, "password": password}

    # Create Node factory
    factory = NetworkNodeFactory(
        hardware_schema=hardware_schema_file,
        hardware_data=hardware_spec_file,
        architecture_schema=architecture_schema_file,
        architecture_data=architecture_spec_file,
        architecture_version=architecture,
    )

    # Open the updated cache to model nodes
    # with open(canu_cache_file, "r+") as file:
    #     canu_cache = yaml.load(file)

    # Get nodes from SHCD
    shcd_node_list, shcd_warnings = node_model_from_shcd(
        factory=factory, spreadsheet=shcd, sheets=sheets
    )

    sls_variables = parse_sls(csi_folder)

    # For versions of Shasta < 1.6, the SLS Hostnames need to be renamed
    if ctx.obj["shasta"]:
        shasta = ctx.obj["shasta"]
        # print("shasta", shasta)
        if float(shasta) < 1.6:
            sls_variables = rename_sls_hostnames(sls_variables)

    switch_config = generate_switch_config(
        shcd_node_list, factory, switch_name, sls_variables
    )

    click.echo(switch_config, file=out)
    return


def get_shasta_name(name, mapper):
    """Parse mapper to get Shasta name."""
    for node in mapper:
        shasta_name = node[1]
        if shasta_name in name:
            return shasta_name


def generate_switch_config(shcd_node_list, factory, switch_name, sls_variables):
    """Generate switch config.

    Args:
        shcd_node_list: List of nodes from the SHCD
        factory: Node factory object
        switch_name: Switch hostname
        sls_variables: Dictionary containing SLS variables

    Returns:
        switch_config: The generated switch configuration
    """
    node_shasta_name = get_shasta_name(switch_name, factory.lookup_mapper())
    is_primary, primary, secondary = switch_is_primary(switch_name)

    templates = {
        "sw-spine": {
            "primary": "sw-spine.primary.j2",
            "secondary": "sw-spine.secondary.j2",
        },
        "sw-cdu": {
            "primary": "sw-cdu.primary.j2",
            "secondary": "sw-cdu.secondary.j2",
        },
        "sw-leaf": {
            "primary": "sw-leaf.primary.j2",
            "secondary": "sw-leaf.secondary.j2",
        },
        "sw-leaf-bmc": {
            "primary": "sw-leaf-bmc.j2",
            "secondary": "sw-leaf-bmc.j2",
        },
    }
    template_name = templates[node_shasta_name][
        "primary" if is_primary else "secondary"
    ]
    template = env.get_template(template_name)

    HOSTNAME = switch_name
    # {{ PASSWORD }}
    NCN_W001 = sls_variables["ncn_w001"]
    NCN_W002 = sls_variables["ncn_w002"]
    NCN_W003 = sls_variables["ncn_w003"]
    NMN = sls_variables["NMN"]
    HMN = sls_variables["HMN"]
    HMN_MTN = sls_variables["HMN_MTN"]
    NMN_MTN = sls_variables["NMN_MTN"]

    HMN_IP_GATEWAY = sls_variables["HMN_IP_GATEWAY"]
    MTL_IP_GATEWAY = sls_variables["MTL_IP_GATEWAY"]
    NMN_IP_GATEWAY = sls_variables["NMN_IP_GATEWAY"]
    CAN_IP_GATEWAY = sls_variables["CAN_IP_GATEWAY"]

    CAN_IP_PRIMARY = sls_variables["CAN_IP_PRIMARY"]
    CAN_IP_SECONDARY = sls_variables["CAN_IP_SECONDARY"]

    cabling = {}
    cabling["nodes"] = get_switch_nodes(switch_name, shcd_node_list, factory)

    if node_shasta_name == "sw-spine" or node_shasta_name == "sw-leaf":

        HMN_IP = sls_variables["HMN_IPs"][HOSTNAME]
        MTL_IP = sls_variables["MTL_IPs"][HOSTNAME]
        NMN_IP = sls_variables["NMN_IPs"][HOSTNAME]

        # Get connections to switch pair
        pair_connections = get_pair_connections(cabling["nodes"], switch_name)
        VSX_KEEPALIVE = pair_connections[0]
        VSX_ISL_PORT1 = pair_connections[1]
        VSX_ISL_PORT2 = pair_connections[2]

        # {{ LOOPBACK_IP }}
        # {{ IPV6_IP }}

    elif node_shasta_name == "sw-cdu":

        HMN_IP = None
        MTL_IP = None
        NMN_IP = None

        # Get connections to switch pair
        pair_connections = get_pair_connections(cabling["nodes"], switch_name)
        VSX_KEEPALIVE = pair_connections[0]
        VSX_ISL_PORT1 = pair_connections[1]
        VSX_ISL_PORT2 = pair_connections[2]
        # {{ LOOPBACK_IP }}
        # {{ IPV6_IP }}

    elif node_shasta_name == "sw-leaf-bmc":
        # Use `sw-leaf-bmc.j2` template
        print("leaf-bmc")
        # Should the template include: {% include 'ncn-m.lag.j2' %} {% include 'ncn-w.lag.j2' %} {% include 'ncn-s.lag.j2' %}
        # Should there be a leaf-bmc-to-leaf template?

        # [{'subtype': 'master', 'config': {'DESCRIPTION': 'ncn-m002', 'INTERFACE_LAG': '1/1/29', 'LAG_NUMBER': 29}},
        # {'subtype': 'worker', 'config': {'DESCRIPTION': 'ncn-w001', 'INTERFACE_LAG': '1/1/30', 'LAG_NUMBER': 30}},
        # {'subtype': 'worker', 'config': {'DESCRIPTION': 'ncn-w002', 'INTERFACE_LAG': '1/1/31', 'LAG_NUMBER': 31}},
        # {'subtype': 'worker', 'config': {'DESCRIPTION': 'ncn-w003', 'INTERFACE_LAG': '1/1/32', 'LAG_NUMBER': 32}},
        # {'subtype': 'storage', 'config': {'DESCRIPTION': 'ncn-s001', 'INTERFACE_LAG': '1/1/33', 'LAG_NUMBER': 33}},
        # {'subtype': 'storage', 'config': {'DESCRIPTION': 'ncn-s002', 'INTERFACE_LAG': '1/1/34', 'LAG_NUMBER': 34}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan001', 'INTERFACE_LAG': '1/1/35', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 35}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan002', 'INTERFACE_LAG': '1/1/36', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 36}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan003', 'INTERFACE_LAG': '1/1/37', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 37}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan004', 'INTERFACE_LAG': '1/1/38', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 38}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan005', 'INTERFACE_LAG': '1/1/39', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 39}},
        # {'subtype': 'application', 'config':
        #   {'DESCRIPTION': 'uan006', 'INTERFACE_LAG': '1/1/40', 'INTERFACE_NUMBER': 'I DONT KNOW', 'LAG_NUMBER': 40}},
        # {'subtype': 'leaf', 'config': {'DESCRIPTION': 'sw-leaf-001', 'LAG_NUMBER': 51, 'INTERFACE_LAG': '1/1/51'}},
        # {'subtype': 'leaf', 'config': {'DESCRIPTION': 'sw-leaf-002', 'LAG_NUMBER': 52, 'INTERFACE_LAG': '1/1/52'}}]

        HMN_IP = sls_variables["HMN_IPs"][HOSTNAME]
        MTL_IP = sls_variables["MTL_IPs"][HOSTNAME]
        NMN_IP = sls_variables["NMN_IPs"][HOSTNAME]

        VSX_KEEPALIVE = None
        VSX_ISL_PORT1 = None
        VSX_ISL_PORT2 = None

        # {{ LOOPBACK_IP }}
        # {{ IPV6_IP }}

        # sw-leaf-bmc-uplink.j2
        # {{ LEAF_UPLINK_PORT_PRIMARY }} #connection from leaf-bmc to spine primary
        # {{ LEAF_UPLINK_PORT_SECONDARY }} #connection from leaf-bmc to spine secondary (from SHCD)

    switch_config = template.render(
        HOSTNAME=HOSTNAME,
        NCN_W001=NCN_W001,
        NCN_W002=NCN_W002,
        NCN_W003=NCN_W003,
        NMN=NMN,
        HMN=HMN,
        HMN_MTN=HMN_MTN,
        NMN_MTN=NMN_MTN,
        VSX_KEEPALIVE=VSX_KEEPALIVE,
        VSX_ISL_PORT1=VSX_ISL_PORT1,
        VSX_ISL_PORT2=VSX_ISL_PORT2,
        HMN_IP=HMN_IP,
        MTL_IP=MTL_IP,
        NMN_IP=NMN_IP,
        HMN_IP_GATEWAY=HMN_IP_GATEWAY,
        MTL_IP_GATEWAY=MTL_IP_GATEWAY,
        NMN_IP_GATEWAY=NMN_IP_GATEWAY,
        CAN_IP_GATEWAY=CAN_IP_GATEWAY,
        CAN_IP_PRIMARY=CAN_IP_PRIMARY,
        CAN_IP_SECONDARY=CAN_IP_SECONDARY,
        cabling=cabling,
    )

    return switch_config


def get_pair_connections(nodes, switch_name):
    """Given a hostname and nodes, return connections to the primary or secondary switch.

    Args:
        nodes: List of nodes connected to the switch
        switch_name: Switch hostname

    Returns:
        List of connections to the paired switch
    """
    is_primary, primary, secondary = switch_is_primary(switch_name)

    if is_primary:
        pair_hostname = secondary
    else:
        pair_hostname = primary

    connections = []
    for x in nodes:
        if x["config"]["DESCRIPTION"] == pair_hostname:
            connections.append(x["config"]["INTERFACE_LAG"])

    connections = natsort.natsorted(connections)
    return connections


def get_switch_nodes(switch_name, shcd_node_list, factory):
    """Get the nodes connected to the switch ports.

    Args:
        switch_name: Switch hostname
        shcd_node_list: List of nodes from the SHCD
        factory: Node factory object

    Returns:
        List of nodes connected to the switch
    """
    nodes = []
    nodes_by_name = {}
    nodes_by_id = {}

    # Make 2 dictionaries for easy node lookup
    for node in shcd_node_list:
        node_tmp = node.serialize()
        name = node_tmp["common_name"]

        nodes_by_name[name] = node_tmp
        nodes_by_id[node_tmp["id"]] = node_tmp

    for port in nodes_by_name[switch_name]["ports"]:

        destination_node_name = nodes_by_id[port["destination_node_id"]]["common_name"]
        destination_port = port["port"]

        shasta_name = get_shasta_name(destination_node_name, factory.lookup_mapper())

        if shasta_name == "ncn-m":
            new_node = {
                "subtype": "master",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "LAG_NUMBER": destination_port,
                },
            }
            nodes.append(new_node)
        elif shasta_name == "ncn-s":
            new_node = {
                "subtype": "storage",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "LAG_NUMBER": destination_port,
                },
            }
            nodes.append(new_node)
        elif shasta_name == "ncn-w":
            new_node = {
                "subtype": "worker",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "LAG_NUMBER": destination_port,
                },
            }
            nodes.append(new_node)
        elif shasta_name == "uan":
            new_node = {
                "subtype": "uan",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "INTERFACE_NUMBER": "I DONT KNOW",
                    "LAG_NUMBER": destination_port,
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-spine":
            new_node = {
                "subtype": "spine",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "LAG_NUMBER": destination_port,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "PT_TO_PT_IP": "****TBD",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-cdu":
            new_node = {
                "subtype": "cdu",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                    "PT_TO_PT_IP": "****TBD",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-leaf":
            new_node = {
                "subtype": "leaf",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "LAG_NUMBER": destination_port,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-leaf-bmc":
            new_node = {
                "subtype": "leaf-bmc",
                "config": {
                    "DESCRIPTION": destination_node_name,
                    "LAG_NUMBER": destination_port,
                    "INTERFACE_LAG": f"1/1/{destination_port}",
                },
            }
            nodes.append(new_node)
        else:
            print("*********************************")
            print("I don't know what this is")
            print("switch_name", switch_name)
            print("shasta_name", shasta_name)
            print("port", port)
            print("*********************************")

    return nodes


def switch_is_primary(switch):
    """Determine if the switch is primary or secondary.

    Args:
        switch: Switch hostname

    Returns:
        is_primary: Bool if the switch is primary
        primary: Primary switch hostname
        secondary: Secondary switch hostname
    """
    # Determine if PRIMARY or SECONDARY
    digits = re.findall(r"(\d+)", switch)[0]
    middle = re.findall(r"(?:sw-)([a-z-]+)", switch)[0]

    if int(digits) % 2 == 0:  # Switch is Secondary
        is_primary = False
        primary = f"sw-{middle.rstrip('-')}-{int(digits)-1 :03d}"
        secondary = switch
    else:  # Switch is Primary
        is_primary = True
        secondary = f"sw-{middle.rstrip('-')}-{int(digits)+1 :03d}"
        primary = switch

    return is_primary, primary, secondary


def parse_sls(csi_folder):
    """Parse the `sls_input_file.json` file for variables.

    Args:
        csi_folder: Directory containing the CSI json file

    Returns:
        sls_variables: Dictionary containing SLS variables.
    """
    networks_list = []

    sls_variables = {
        "CAN": None,
        "HMN": None,
        "MTL": None,
        "NMN": None,
        "HMN_MTN": None,
        "NMN_MTN": None,
        "CAN_IP_GATEWAY": None,
        "HMN_IP_GATEWAY": None,
        "MTL_IP_GATEWAY": None,
        "NMN_IP_GATEWAY": None,
        "ncn_w001": None,
        "ncn_w002": None,
        "ncn_w003": None,
        "CAN_IP_PRIMARY": None,
        "CAN_IP_SECONDARY": None,
        "HMN_IPs": defaultdict(),
        "MTL_IPs": defaultdict(),
        "NMN_IPs": defaultdict(),
    }

    try:
        with open(os.path.join(csi_folder, "sls_input_file.json"), "r") as f:
            input_json = json.load(f)

            for network in [input_json.get("Networks", {})]:
                for x in network:
                    name = network[x].get("Name", "")

                    if name == "CAN":
                        sls_variables["CAN"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )
                        sls_variables["CAN_IP_GATEWAY"] = (
                            network[x]
                            .get("ExtraProperties", {})
                            .get("Subnets", {})[0]
                            .get("Gateway", "")
                        )
                        for subnets in (
                            network[x].get("ExtraProperties", {}).get("Subnets", {})
                        ):
                            if subnets["FullName"] == "CAN Bootstrap DHCP Subnet":
                                for ip in subnets["IPReservations"]:
                                    if ip["Name"] == "can-switch-1":
                                        sls_variables["CAN_IP_PRIMARY"] = ip[
                                            "IPAddress"
                                        ]
                                    elif ip["Name"] == "can-switch-2":
                                        sls_variables["CAN_IP_SECONDARY"] = ip[
                                            "IPAddress"
                                        ]

                    elif name == "HMN":
                        sls_variables["HMN"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )
                        sls_variables["HMN_IP_GATEWAY"] = (
                            network[x]
                            .get("ExtraProperties", {})
                            .get("Subnets", {})[0]
                            .get("Gateway", "")
                        )
                        for subnets in (
                            network[x].get("ExtraProperties", {}).get("Subnets", {})
                        ):
                            if (
                                subnets["FullName"]
                                == "HMN Management Network Infrastructure"
                            ):
                                for ip in subnets["IPReservations"]:
                                    sls_variables["HMN_IPs"][ip["Name"]] = ip[
                                        "IPAddress"
                                    ]

                    elif name == "MTL":
                        sls_variables["MTL"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )
                        sls_variables["MTL_IP_GATEWAY"] = (
                            network[x]
                            .get("ExtraProperties", {})
                            .get("Subnets", {})[0]
                            .get("Gateway", "")
                        )
                        for subnets in (
                            network[x].get("ExtraProperties", {}).get("Subnets", {})
                        ):
                            if (
                                subnets["FullName"]
                                == "MTL Management Network Infrastructure"
                            ):
                                for ip in subnets["IPReservations"]:
                                    sls_variables["MTL_IPs"][ip["Name"]] = ip[
                                        "IPAddress"
                                    ]

                    elif name == "NMN":
                        sls_variables["NMN"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )
                        sls_variables["NMN_IP_GATEWAY"] = (
                            network[x]
                            .get("ExtraProperties", {})
                            .get("Subnets", {})[0]
                            .get("Gateway", "")
                        )

                        for subnets in (
                            network[x].get("ExtraProperties", {}).get("Subnets", {})
                        ):
                            if subnets["FullName"] == "NMN Bootstrap DHCP Subnet":
                                for ip in subnets["IPReservations"]:
                                    if ip["Name"] == "ncn-w001":
                                        sls_variables["ncn_w001"] = ip["IPAddress"]
                                    elif ip["Name"] == "ncn-w002":
                                        sls_variables["ncn_w002"] = ip["IPAddress"]
                                    elif ip["Name"] == "ncn-w003":
                                        sls_variables["ncn_w003"] = ip["IPAddress"]
                            elif (
                                subnets["FullName"]
                                == "NMN Management Network Infrastructure"
                            ):
                                for ip in subnets["IPReservations"]:
                                    sls_variables["NMN_IPs"][ip["Name"]] = ip[
                                        "IPAddress"
                                    ]

                    elif name == "NMN_MTN":
                        sls_variables["NMN_MTN"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )
                    elif name == "HMN_MTN":
                        sls_variables["HMN_MTN"] = (
                            network[x].get("ExtraProperties", {}).get("CIDR", "")
                        )

                    for subnets in (
                        network[x].get("ExtraProperties", {}).get("Subnets", {})
                    ):

                        vlan = subnets.get("VlanID", "")
                        networks_list.append([name, vlan])

        networks_list = set(tuple(x) for x in networks_list)

    except FileNotFoundError:
        click.secho(
            "The file sls_input_file.json was not found, check that this is the correct CSI directory.",
            fg="red",
        )
        return

    return sls_variables


def rename_sls_hostnames(sls_variables):
    """Parse and rename SLS switch names.

    The operation needs to be done in two passes to prevent naming conflicts.

    Args:
        sls_variables: Dictionary containing SLS variables.

    Returns:
        sls_variables: Dictionary containing renamed SLS variables.
    """
    # First pass rename leaf ==> leaf-bmc
    for key, value in sls_variables["HMN_IPs"].copy().items():
        new_name = key.replace("-leaf-", "-leaf-bmc-")
        sls_variables["HMN_IPs"].pop(key)
        sls_variables["HMN_IPs"][new_name] = value

    for key, value in sls_variables["MTL_IPs"].copy().items():
        new_name = key.replace("-leaf-", "-leaf-bmc-")
        sls_variables["MTL_IPs"].pop(key)
        sls_variables["MTL_IPs"][new_name] = value

    for key, value in sls_variables["NMN_IPs"].copy().items():
        new_name = key.replace("-leaf-", "-leaf-bmc-")
        sls_variables["NMN_IPs"].pop(key)
        sls_variables["NMN_IPs"][new_name] = value

    # Second pass rename agg ==> leaf
    for key, value in sls_variables["HMN_IPs"].copy().items():
        new_name = key.replace("-agg-", "-leaf-")
        sls_variables["HMN_IPs"].pop(key)
        sls_variables["HMN_IPs"][new_name] = value

    for key, value in sls_variables["MTL_IPs"].copy().items():
        new_name = key.replace("-agg-", "-leaf-")
        sls_variables["MTL_IPs"].pop(key)
        sls_variables["MTL_IPs"][new_name] = value

    for key, value in sls_variables["NMN_IPs"].copy().items():
        new_name = key.replace("-agg-", "-leaf-")
        sls_variables["NMN_IPs"].pop(key)
        sls_variables["NMN_IPs"][new_name] = value

    return sls_variables
