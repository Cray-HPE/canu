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
"""CANU generate switch config commands."""
from collections import defaultdict
from itertools import groupby
import json
import os
from os import environ, path
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from hier_config import HConfig, Host
from jinja2 import Environment, FileSystemLoader, StrictUndefined
import natsort
import netaddr
from netutils.mac import is_valid_mac
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import requests
from ruamel.yaml import YAML
from ttp import ttp
import urllib3

from canu.utils.cache import cache_directory
from canu.utils.yaml_load import load_yaml
from canu.validate.paddle.paddle import node_model_from_paddle
from canu.validate.shcd.shcd import (
    node_model_from_shcd,
    shcd_to_sheets,
    switch_unused_ports,
)

yaml = YAML()

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

# Schema and Data files
canu_cache_file = path.join(cache_directory(), "canu_cache.yaml")
canu_config_file = path.join(project_root, "canu", "canu.yaml")
canu_version_file = path.join(project_root, "canu", ".version")

# ttp preserve templates
# pulls the interface and lag from switch configs.
ttp_templates = defaultdict()
for vendor in ["aruba", "dell", "mellanox"]:
    ttp_templates[vendor] = path.join(
        project_root,
        "canu",
        "generate",
        "switch",
        "config",
        "ttp_templates",
        f"{vendor}_lag.txt",
    )

mellanox_interface = path.join(
    project_root,
    "canu",
    "generate",
    "switch",
    "config",
    "ttp_templates",
    "mellanox_interface.txt",
)

# Import templates
network_templates_folder = path.join(
    project_root,
    "network_modeling",
    "configs",
    "templates",
)
env = Environment(
    loader=FileSystemLoader(network_templates_folder),
    undefined=StrictUndefined,
)

# Get CSM versions from canu.yaml
with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

csm_options = canu_config["csm_versions"]

# Get CANU version from .version
with open(canu_version_file, "r") as file:
    canu_version = file.readline()
canu_version = canu_version.strip()

dash = "-" * 60


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--csm",
    type=click.Choice(csm_options),
    help="CSM network version",
    prompt="CSM network version",
    required=True,
    show_choices=True,
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
    help="CSM architecture",
    required=True,
    prompt="Architecture type",
)
@optgroup.group(
    "Network input source",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--ccj",
    help="Paddle CCJ file",
    type=click.File("rb"),
)
@optgroup.option(
    "--shcd",
    help="SHCD file",
    type=click.File("rb"),
)
@click.option(
    "--tabs",
    help="The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.",
)
@click.option(
    "--corners",
    help="The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.",
)
@click.option(
    "--name",
    "switch_name",
    required=True,
    help="The name of the switch to generate config e.g. 'sw-spine-001'",
    prompt="Switch Name",
)
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
)
@click.option(
    "--auth-token",
    envvar="SLS_TOKEN",
    help="Token for SLS authentication",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.option(
    "--custom-config",
    help="Create and maintain custom switch configurations beyond generated plan-of-record",
    type=click.Path(),
)
@click.option(
    "--preserve",
    help="Path to current running configs.",
    type=click.Path(),
)
@click.option(
    "--reorder",
    is_flag=True,
    help="reorder config to heir config order",
    required=False,
)
@click.pass_context
def config(
    ctx,
    csm,
    architecture,
    ccj,
    shcd,
    tabs,
    corners,
    switch_name,
    sls_file,
    auth_token,
    sls_address,
    out,
    preserve,
    custom_config,
    reorder,
):
    """Generate switch config using the SHCD.

    In order to generate switch config, a valid SHCD must be passed in and system variables must be read in from either
    an SLS output file or the SLS API.

    ## CSI Input

    - In order to parse network data using SLS, pass in the file containing SLS JSON data (normally sls_file.json) using the '--sls-file' flag

    - If used, CSI-generated sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

    - Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory '/var/www/ephemeral/prep/SYSTEMNAME/'

    - Later in the install process, the sls_file.json file is generally in '/mnt/pitdata/prep/SYSTEMNAME/'


    ## SLS API Input

    - To parse the Shasta SLS API for IP addresses, ensure that you have a valid token.

    - The token file can either be passed in with the '--auth-token TOKEN_FILE' flag, or it can be automatically read if the environmental variable 'SLS_TOKEN' is set.

    - The SLS address is default set to 'api-gw-service-nmn.local'.

    - if you are operating on a system with a different address, you can set it with the '--sls-address SLS_ADDRESS' flag.


    ## SHCD Input

    - Use the '--tabs' flag to select which tabs on the spreadsheet will be included.

    - The '--corners' flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. If the corners are not specified, you will be prompted to enter them for each tab.

    - The table should contain the 11 headers: Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port.


    Use the '--folder FOLDERNAME' flag to output all the switch configs to a folder.

    ----------
    \f
    # noqa: D301, B950

    Args:
        ctx: CANU context settings
        csm: CSM version
        architecture: CSM architecture
        ccj: Paddle CCJ file
        shcd: SHCD file
        tabs: The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.
        corners: The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.
        switch_name: Switch name
        sls_file: JSON file containing SLS data
        auth_token: Token for SLS authentication
        sls_address: The address of SLS
        out: Name of the output file
        preserve: Folder where switch running configs exist.
        custom_config: yaml file containing customized switch configurations which is merged with the generated config.
        reorder: Filters generated configurations through hier_config generate a more natural running-configuration order.
    """
    # SHCD Parsing
    if shcd:
        try:
            sheets = shcd_to_sheets(shcd, tabs, corners)
        except Exception:
            return
        if not architecture:
            architecture = click.prompt(
                "Please enter the tabs to check separated by a comma, e.g. 10G_25G_40G_100G,NMN,HMN.",
                type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
            )
    # Paddle Parsing
    else:
        ccj_json = json.load(ccj)
        architecture = ccj_json.get("architecture")

        if architecture is None:
            click.secho(
                "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ.",
                fg="red",
            )
            return

    if architecture.lower() == "full" or architecture == "network_v2":
        architecture = "network_v2"
        template_folder = "full"
        vendor_folder = "aruba"
    elif architecture.lower() == "tds" or architecture == "network_v2_tds":
        architecture = "network_v2_tds"
        template_folder = "tds"
        vendor_folder = "aruba"
    elif architecture.lower() == "v1" or architecture == "network_v1":
        architecture = "network_v1"
        template_folder = "full"
        vendor_folder = "dellmellanox"

    # Create Node factory
    factory = NetworkNodeFactory(architecture_version=architecture)
    if shcd:
        # Get nodes from SHCD
        network_node_list, network_warnings = node_model_from_shcd(
            factory=factory,
            spreadsheet=shcd,
            sheets=sheets,
        )
    else:
        network_node_list, network_warnings = node_model_from_paddle(factory, ccj_json)
    # Parse SLS input file.

    if sls_file:
        try:
            input_json = json.load(sls_file)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho(
                f"The file {sls_file.name} is not valid JSON.",
                fg="red",
            )
            return

        # Format the input to be like the SLS JSON
        sls_json = [
            network[x] for network in [input_json.get("Networks", {})] for x in network
        ]

    else:
        # Get SLS config
        token = environ.get("SLS_TOKEN")

        # Token file takes precedence over the environmental variable
        if auth_token != token:
            try:
                with open(auth_token) as f:
                    data = json.load(f)
                    token = data["access_token"]

            except Exception:
                click.secho(
                    "Invalid token file, generate another token or try again.",
                    fg="white",
                    bg="red",
                )
                return

        # SLS
        url = "https://" + sls_address + "/apis/sls/v1/networks"
        try:
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=False,
            )
            response.raise_for_status()

            sls_json = response.json()

        except requests.exceptions.ConnectionError:
            return click.secho(
                f"Error connecting to SLS {sls_address}, check the address or pass in a new address using --sls-address.",
                fg="white",
                bg="red",
            )
        except requests.exceptions.HTTPError:
            bad_token_reason = (
                "environmental variable 'SLS_TOKEN' is correct."
                if auth_token == token
                else "token is valid, or generate a new one."
            )
            return click.secho(
                f"Error connecting SLS {sls_address}, check that the {bad_token_reason}",
                fg="white",
                bg="red",
            )
    sls_variables = parse_sls_for_config(sls_json)

    # For versions of csm < 1.2, the SLS Hostnames need to be renamed
    if csm:
        if float(csm) < 1.2:
            sls_variables = rename_sls_hostnames(sls_variables)

    switch_config, devices, unknown = generate_switch_config(
        csm,
        architecture,
        network_node_list,
        factory,
        switch_name,
        sls_variables,
        template_folder,
        vendor_folder,
        preserve,
        custom_config,
        reorder,
    )

    click.echo("\n")
    click.secho(dash, fg="bright_white")

    if custom_config:
        click.secho(
            f"{switch_name} Customized Configurations have been detected in the generated switch configurations",
            fg="yellow",
        )
        click.echo(switch_config, file=out)
    else:
        click.secho(f"{switch_name} Switch Config", fg="bright_white")
        click.echo(switch_config, file=out)

    if len(unknown) > 0:
        click.secho("\nWarning", fg="red")

        click.secho(
            "\nThe following devices were discovered in the input data, but the CANU model cannot determine "
            + "the type and generate a configuration.\nApplying this configuration without considering these "
            + "devices will likely result in loss of contact with these devices."
            + "\nEnsure valid input, submit a bug to CANU and manually add these devices to the configuration.",
            fg="red",
        )
        click.secho(dash)
        for x in unknown:
            click.secho(x, fg="bright_white")
    return


def get_shasta_name(name, mapper):
    """Parse mapper to get Shasta name."""
    for node in mapper:
        shasta_name = node[1]
        if shasta_name in name:
            return shasta_name


def add_custom_config(custom_config, switch_config, host, switch_os, custom_file_name):
    """Merge custom config into generated config."""
    switch_config_hier = HConfig(host=host)
    custom_config_hier = HConfig(host=host)
    # load configs in HConfig Objects
    custom_config_hier.load_from_string(custom_config)
    switch_config_hier.load_from_string(switch_config)

    # get the delta between the custom config and generated switch config
    # text at the top of generated config
    custom_config_merge = (
        f"# The following switch configurations were inserted into the plan-of-record configuration from {custom_file_name}\n"
        + "# Custom configurations are merged into the generated configuration to maintain"
        + "site-specific behaviors and (less frequently) to override known issues.\n"
    )
    diff = custom_config_hier.difference(switch_config_hier)
    for line in diff.all_children_sorted():
        custom_config_merge += "\n" + "# " + line.cisco_style_text()
    custom_config_merge += "\n"

    # delete custom config that exists in the generated config
    # If interface 1/1 has any config under it, it will be deleted and overwritten with the custom config
    for line_custom in custom_config_hier.all_children_sorted():
        switch_config_hier.add_ancestor_copy_of(line_custom)
        switch_config_hier.del_child_by_text(str(line_custom))

    if switch_os == "onyx":
        mellanox_config = ""
        for line in custom_config_hier.all_children_sorted():
            mellanox_config += "\n" + str(line)

        # parse out mellanox interfaces from custom config file
        parser = ttp(data=mellanox_config, template=mellanox_interface)
        parser.parse()
        interfaces = parser.result()

        # mellanox overwrite port configuration
        for port in interfaces[0][0]:
            override_port = port["interface"]
            for line in switch_config_hier.all_children_sorted():
                # match interfaces from custom config file
                if line.text.startswith(f"interface ethernet {override_port} "):
                    # delete interfaces from generated config
                    switch_config_hier.del_child(line)

    # merge custom config into generated switch config
    switch_config_hier.merge(custom_config_hier)

    # re-order config
    switch_config_hier.set_order_weight()
    if switch_os == "aoscx":
        # add ! to the end of the aruba banner.
        banner = switch_config_hier.get_child("contains", "banner")
        banner.add_child("!")
    for line in switch_config_hier.all_children_sorted():
        # add two spaces to indented config to match aruba formatting.
        if (
            line.cisco_style_text().startswith("  ")
            and "!" not in line.cisco_style_text()
            and switch_os == "aoscx"
        ):
            custom_config_merge += "\n" + "  " + line.cisco_style_text()
        elif switch_os == "dellOS10":
            custom_config_merge += "\n" + line.cisco_style_text()
        else:
            custom_config_merge += "\n" + line.cisco_style_text().lstrip()

    return custom_config_merge


def generate_switch_config(
    csm,
    architecture,
    network_node_list,
    factory,
    switch_name,
    sls_variables,
    template_folder,
    vendor_folder,
    preserve,
    custom_config,
    reorder,
):
    """Generate switch config.

    Args:
        csm: CSM version
        architecture: CSM architecture
        network_node_list: List of nodes from the SHCD / Paddle
        factory: Node factory object
        switch_name: Switch hostname
        sls_variables: Dictionary containing SLS variables
        template_folder: Architecture folder contaning the switch templates
        vendor_folder: Vendor folder contaning the template_folder
        preserve: Folder where switch running configs exist.  This folder should be populated from the "canu backup network"
        custom_config: yaml file containing customized switch configurations which is merged with the generated config.
        reorder: Filters generated configurations through hier_config generate a more natural running-configuration order.


    Returns:
        switch_config: The generated switch configuration
    """
    node_shasta_name = get_shasta_name(switch_name, factory.lookup_mapper())

    templates = {
        "sw-spine": {
            "primary": f"{csm}/{vendor_folder}/{template_folder}/sw-spine.primary.j2",
            "secondary": f"{csm}/{vendor_folder}/{template_folder}/sw-spine.secondary.j2",
        },
        "sw-cdu": {
            "primary": f"{csm}/{vendor_folder}/common/sw-cdu.primary.j2",
            "secondary": f"{csm}/{vendor_folder}/common/sw-cdu.secondary.j2",
        },
        "sw-leaf": {
            "primary": f"{csm}/{vendor_folder}/{template_folder}/sw-leaf.primary.j2",
            "secondary": f"{csm}/{vendor_folder}/{template_folder}/sw-leaf.secondary.j2",
        },
        "sw-leaf-bmc": {
            "primary": f"{csm}/{vendor_folder}/{template_folder}/sw-leaf-bmc.j2",
            "secondary": f"{csm}/{vendor_folder}/{template_folder}/sw-leaf-bmc.j2",
        },
    }

    if node_shasta_name is None:
        return Exception(
            click.secho(
                f"For switch {switch_name}, the type cannot be determined. Please check the switch name and try again.",
                fg="red",
            ),
        )
    elif node_shasta_name == "sw-edge" and float(csm) >= 1.2:
        templates["sw-edge"] = {
            "primary": f"{csm}/arista/sw-edge.primary.j2",
            "secondary": f"{csm}/arista/sw-edge.secondary.j2",
        }
    elif node_shasta_name not in [
        "sw-cdu",
        "sw-leaf-bmc",
        "sw-leaf",
        "sw-spine",
    ]:
        return Exception(
            click.secho(
                f"{switch_name} is not a switch. Only switch config can be generated.",
                fg="red",
            ),
        )

    if preserve:
        try:
            with open(os.path.join(f"{preserve}/{switch_name}.cfg"), "r") as f:
                device_running = f.read()
                # Get mellanox Switches
                if architecture == "network_v1" and "spine" in switch_name:
                    template = ttp_templates["mellanox"]
                    switch_config_list = []
                    for line in device_running.splitlines():
                        if line.startswith("   "):
                            switch_config_list.append(line.strip())
                        else:
                            switch_config_list.append(line)
                    device_running = ("\n").join(switch_config_list)
                # get Dell Switches
                elif architecture == "network_v1":
                    template = ttp_templates["dell"]
                # get Aruba switches
                else:
                    template = ttp_templates["aruba"]
                parser = ttp(device_running, template)
                parser.parse()
                preserve = parser.result()
        except FileNotFoundError:
            click.secho(
                "The running config was not found, check that you entered the right file name and path.",
                fg="red",
            )
            exit(1)
    if custom_config:
        custom_config_file = os.path.basename(custom_config)
        custom_config = load_yaml(custom_config)

    is_primary, primary, secondary = switch_is_primary(switch_name)

    template_name = templates[node_shasta_name][
        "primary" if is_primary else "secondary"
    ]

    def vsx_mac(switch_name):
        is_primary, primary, secondary = switch_is_primary(switch_name)
        primary_number = re.search(r"\d+", primary).group()
        hex_number = format(int(primary_number), "02x")
        if "sw-spine" in switch_name:
            vsx_mac = "02:00:00:00:" + hex_number + ":00"
        elif "sw-leaf" in switch_name:
            vsx_mac = "02:01:00:00:" + hex_number + ":00"
        elif "sw-cdu" in switch_name:
            vsx_mac = "02:02:00:00:" + hex_number + ":00"
        if is_valid_mac(vsx_mac):
            return vsx_mac
        else:
            click.secho(f"system-mac for VSX {switch_name} is not valid", fg="red")
            sys.exit(1)

    jinja_func = {"vsx_mac": vsx_mac}
    template = env.get_template(template_name)
    template.globals.update(jinja_func)

    native_vlan = 1

    leaf_bmc_vlan = [
        native_vlan,
        sls_variables["NMN_VLAN"],
        sls_variables["HMN_VLAN"],
    ]
    spine_leaf_vlan = [
        native_vlan,
        sls_variables["NMN_VLAN"],
        sls_variables["HMN_VLAN"],
        sls_variables["CAN_VLAN"],
    ]
    if sls_variables["CMN_VLAN"] and float(csm) >= 1.2:
        spine_leaf_vlan.append(sls_variables["CMN_VLAN"])
        leaf_bmc_vlan.append(sls_variables["CMN_VLAN"])

    elif sls_variables["CMN_VLAN"] and float(csm) < 1.2:
        click.secho(
            "\nCMN network found in SLS, the CSM version required to use this network has to be 1.2 or greater. "
            + "\nMake sure the --csm flag matches the CSM version you are using.",
            fg="red",
        )
        sys.exit(1)
    elif sls_variables["CMN_VLAN"] is None and float(csm) >= 1.2:
        click.secho(
            "\nCMN network not found in SLS, this is required for csm 1.2 "
            + "\nHas the CSM 1.2 SLS upgrade procedure been run?",
            fg="red",
        )
        sys.exit(1)
    spine_leaf_vlan = groupby_vlan_range(spine_leaf_vlan)
    leaf_bmc_vlan = groupby_vlan_range(leaf_bmc_vlan)

    variables = {
        "HOSTNAME": switch_name,
        "CSM_VERSION": csm,
        "CANU_VERSION": canu_version,
        "NCN_W001": sls_variables["ncn_w001"],
        "NCN_W002": sls_variables["ncn_w002"],
        "NCN_W003": sls_variables["ncn_w003"],
        "CAN": sls_variables["CAN"],
        "CAN_VLAN": sls_variables["CAN_VLAN"],
        "CAN_NETMASK": sls_variables["CAN_NETMASK"],
        "CAN_NETWORK_IP": sls_variables["CAN_NETWORK_IP"],
        "CAN_PREFIX_LEN": sls_variables["CAN_PREFIX_LEN"],
        "CHN": sls_variables["CHN"],
        "CHN_VLAN": sls_variables["CHN_VLAN"],
        "CHN_NETMASK": sls_variables["CHN_NETMASK"],
        "CHN_NETWORK_IP": sls_variables["CHN_NETWORK_IP"],
        "CHN_PREFIX_LEN": sls_variables["CHN_PREFIX_LEN"],
        "CHN_ASN": sls_variables["CHN_ASN"],
        "CMN": sls_variables["CMN"],
        "CMN_VLAN": sls_variables["CMN_VLAN"],
        "CMN_NETMASK": sls_variables["CMN_NETMASK"],
        "CMN_NETWORK_IP": sls_variables["CMN_NETWORK_IP"],
        "CMN_PREFIX_LEN": sls_variables["CMN_PREFIX_LEN"],
        "CMN_ASN": sls_variables["CMN_ASN"],
        "MTL_NETMASK": sls_variables["MTL_NETMASK"],
        "MTL_PREFIX_LEN": sls_variables["MTL_PREFIX_LEN"],
        "NMN": sls_variables["NMN"],
        "NMN_VLAN": sls_variables["NMN_VLAN"],
        "NMN_NETMASK": sls_variables["NMN_NETMASK"],
        "NMN_NETWORK_IP": sls_variables["NMN_NETWORK_IP"],
        "NMN_PREFIX_LEN": sls_variables["NMN_PREFIX_LEN"],
        "NMN_ASN": sls_variables["NMN_ASN"],
        "HMN": sls_variables["HMN"],
        "HMN_VLAN": sls_variables["HMN_VLAN"],
        "HMN_NETMASK": sls_variables["HMN_NETMASK"],
        "HMN_NETWORK_IP": sls_variables["HMN_NETWORK_IP"],
        "HMN_PREFIX_LEN": sls_variables["HMN_PREFIX_LEN"],
        "HMN_MTN": sls_variables["HMN_MTN"],
        "HMN_MTN_NETMASK": sls_variables["HMN_MTN_NETMASK"],
        "HMN_MTN_NETWORK_IP": sls_variables["HMN_MTN_NETWORK_IP"],
        "HMN_MTN_PREFIX_LEN": sls_variables["HMN_MTN_PREFIX_LEN"],
        "NMN_MTN": sls_variables["NMN_MTN"],
        "NMN_MTN_NETMASK": sls_variables["NMN_MTN_NETMASK"],
        "NMN_MTN_NETWORK_IP": sls_variables["NMN_MTN_NETWORK_IP"],
        "NMN_MTN_PREFIX_LEN": sls_variables["NMN_MTN_PREFIX_LEN"],
        "HMNLB": sls_variables["HMNLB"],
        "HMNLB_TFTP": sls_variables["HMNLB_TFTP"],
        "HMNLB_DNS": sls_variables["HMNLB_DNS"],
        "HMNLB_NETMASK": sls_variables["HMNLB_NETMASK"],
        "HMNLB_NETWORK_IP": sls_variables["HMNLB_NETWORK_IP"],
        "HMNLB_PREFIX_LEN": sls_variables["HMNLB_PREFIX_LEN"],
        "NMNLB": sls_variables["NMNLB"],
        "NMNLB_TFTP": sls_variables["NMNLB_TFTP"],
        "NMNLB_DNS": sls_variables["NMNLB_DNS"],
        "NMNLB_NETMASK": sls_variables["NMNLB_NETMASK"],
        "NMNLB_NETWORK_IP": sls_variables["NMNLB_NETWORK_IP"],
        "NMNLB_PREFIX_LEN": sls_variables["NMNLB_PREFIX_LEN"],
        "HMN_IP_GATEWAY": sls_variables["HMN_IP_GATEWAY"],
        "MTL_IP_GATEWAY": sls_variables["MTL_IP_GATEWAY"],
        "NMN_IP_GATEWAY": sls_variables["NMN_IP_GATEWAY"],
        "CAN_IP_GATEWAY": sls_variables["CAN_IP_GATEWAY"],
        "CAN_IP_PRIMARY": sls_variables["CAN_IP_PRIMARY"],
        "CAN_IP_SECONDARY": sls_variables["CAN_IP_SECONDARY"],
        "CHN_IP_GATEWAY": sls_variables["CHN_IP_GATEWAY"],
        "CHN_IP_PRIMARY": sls_variables["CHN_IP_PRIMARY"],
        "CHN_IP_SECONDARY": sls_variables["CHN_IP_SECONDARY"],
        "CMN_IP_GATEWAY": sls_variables["CMN_IP_GATEWAY"],
        "CMN_IP_PRIMARY": sls_variables["CMN_IP_PRIMARY"],
        "CMN_IP_SECONDARY": sls_variables["CMN_IP_SECONDARY"],
        "NMN_MTN_CABINETS": sls_variables["NMN_MTN_CABINETS"],
        "HMN_MTN_CABINETS": sls_variables["HMN_MTN_CABINETS"],
        "LEAF_BMC_VLANS": leaf_bmc_vlan,
        "SPINE_LEAF_VLANS": spine_leaf_vlan,
        "NATIVE_VLAN": native_vlan,
        "CAN_IPs": sls_variables["CAN_IPs"],
        "CHN_IPs": sls_variables["CHN_IPs"],
        "CMN_IPs": sls_variables["CMN_IPs"],
        "NMN_IPs": sls_variables["NMN_IPs"],
        "HMN_IPs": sls_variables["HMN_IPs"],
        "SWITCH_ASN": sls_variables["SWITCH_ASN"],
    }
    cabling = {}
    cabling["nodes"], unknown = get_switch_nodes(
        architecture,
        switch_name,
        network_node_list,
        factory,
        sls_variables,
        preserve,
    )
    unused_ports = switch_unused_ports(network_node_list)
    variables["UNUSED_PORTS"] = unused_ports[switch_name]

    if (
        switch_name not in sls_variables["HMN_IPs"].keys()
        and "sw-edge" not in switch_name
    ):
        click.secho(f"Cannot find {switch_name} in CSI / SLS nodes.", fg="red")
        sys.exit(1)

    # hack to rename edge switch to chn switch, this is a temporary fix until SLS/CSI is updated
    if "sw-edge" in switch_name:

        if switch_name == "sw-edge-001":
            switch_name = "chn-switch-1"
        if switch_name == "sw-edge-002":
            switch_name = "chn-switch-2"
        if sls_variables.get("CHN_IPs", {}).get(switch_name):
            variables["CHN_IP"] = sls_variables["CHN_IPs"][switch_name]
            last_octet = variables["CHN_IP"].split(".")[3]
            variables["LOOPBACK_IP"] = "10.2.1." + last_octet
            variables["EDGE_BGP_IP_PRIMARY"] = "10.2.3.2"
            variables["EDGE_BGP_IP_SECONDARY"] = "10.2.3.3"
        else:
            click.secho(
                f"\n{switch_name} found in SHCD but not in SLS"
                + "\nMake sure the CHN edge switches are used as inputs when running CSI.",
                fg="red",
            )
            sys.exit(1)
    else:
        variables["CMN_IP"] = sls_variables.get("CMN_IPs", {}).get(switch_name)
        variables["HMN_IP"] = sls_variables.get("HMN_IPs", {}).get(switch_name)
        variables["MTL_IP"] = sls_variables.get("MTL_IPs", {}).get(switch_name)
        variables["NMN_IP"] = sls_variables.get("NMN_IPs", {}).get(switch_name)
        last_octet = variables["HMN_IP"].split(".")[3]
        variables["LOOPBACK_IP"] = "10.2.0." + last_octet

    if node_shasta_name in ["sw-spine", "sw-leaf", "sw-cdu"]:
        # Get connections to switch pair
        pair_connections = get_pair_connections(cabling["nodes"], switch_name)
        length_connections = len(pair_connections)

        if length_connections == 3:
            variables["VSX_KEEPALIVE"] = pair_connections[0]
            variables["VSX_ISL_PORT1"] = pair_connections[1]
            variables["VSX_ISL_PORT2"] = pair_connections[2]
        elif length_connections == 2:
            variables["VSX_KEEPALIVE"] = "mgmt0"
            variables["VSX_ISL_PORT1"] = pair_connections[0]
            variables["VSX_ISL_PORT2"] = pair_connections[1]

    # get VLANs and IPs for CDU switches
    if "sw-cdu" in node_shasta_name:
        nodes_by_name = {}
        nodes_by_id = {}
        destination_rack_list = []
        variables["NMN_MTN_VLANS"] = []
        variables["HMN_MTN_VLANS"] = []

        for node in network_node_list:
            node_tmp = node.serialize()
            name = node_tmp["common_name"]
            nodes_by_name[name] = node_tmp
            nodes_by_id[node_tmp["id"]] = node_tmp
        for port in nodes_by_name[switch_name]["ports"]:
            destination_rack = nodes_by_id[port["destination_node_id"]]["location"][
                "rack"
            ]

            destination_rack_list.append(int(re.search(r"\d+", destination_rack)[0]))
        for cabinets in (
            sls_variables["NMN_MTN_CABINETS"] + sls_variables["HMN_MTN_CABINETS"]
        ):
            ip_address = netaddr.IPNetwork(cabinets["CIDR"])
            is_primary = switch_is_primary(switch_name)
            sls_rack_int = int(re.search(r"\d+", (cabinets["Name"]))[0])
            if sls_rack_int in destination_rack_list:
                if cabinets in sls_variables["NMN_MTN_CABINETS"]:
                    variables["NMN_MTN_VLANS"].append(cabinets)
                    variables["NMN_MTN_VLANS"][-1][
                        "PREFIX_LENGTH"
                    ] = ip_address.prefixlen
                    if is_primary[0]:
                        ip = str(ip_address[2])
                        variables["NMN_MTN_VLANS"][-1]["IP"] = ip
                    else:
                        ip = str(ip_address[3])
                        variables["NMN_MTN_VLANS"][-1]["IP"] = ip

                if cabinets in sls_variables["HMN_MTN_CABINETS"]:
                    variables["HMN_MTN_VLANS"].append(cabinets)
                    variables["HMN_MTN_VLANS"][-1][
                        "PREFIX_LENGTH"
                    ] = ip_address.prefixlen
                    if is_primary[0]:
                        ip = str(ip_address[2])
                        variables["HMN_MTN_VLANS"][-1]["IP"] = ip
                    else:
                        ip = str(ip_address[3])
                        variables["HMN_MTN_VLANS"][-1]["IP"] = ip

    switch_config = template.render(
        variables=variables,
        cabling=cabling,
    )
    devices = set()
    for node in cabling["nodes"]:
        devices.add(node["subtype"])

    def hier_options(switch_os):
        options_file = os.path.join(
            project_root,
            "canu",
            "validate",
            "switch",
            "config",
            f"{switch_os}_options.yaml",
        )
        return options_file

    def add_preserve_config(switch_config):
        preserve_lag_config = "# The interface to LAG mappings below have been preserved in the generated config\n"
        for port in preserve[0][0]:
            interface = port.get("interface")
            lag = port.get("lag")
            if lag is not None:
                preserve_lag_config += f"# interface {interface} LAG id {lag}\n"
        preserve_lag_config += "\n"
        preserve_lag_config += switch_config
        return preserve_lag_config

    def error_check_preserve_config(switch_config):
        if (
            "mlag-channel-group None" in switch_config
            or "lag None" in switch_config
            or "channel-group None" in switch_config
        ):
            click.secho(
                "Incorrect port > MLAG mapping, please verify that all the ports have a correct MLAG mapping.",
                fg="red",
            )
            sys.exit(1)

    if architecture == "network_v1" and node_shasta_name != "sw-edge":
        switch_config_v1 = ""
        if "sw-cdu" in switch_name or "sw-leaf-bmc" in switch_name:
            switch_os = "dellOS10"
            options = yaml.load(open(hier_options(switch_os)))
        elif "sw-spine" in switch_name:
            switch_os = "onyx"
            options = yaml.load(open(hier_options(switch_os)))
        hier_host = Host(switch_name, switch_os, options)
        if custom_config and custom_config.get(switch_name) is not None:
            switch_custom_config = custom_config.get(switch_name)
            switch_config_v1 = add_custom_config(
                switch_custom_config,
                switch_config,
                hier_host,
                switch_os,
                custom_config_file,
            )

        else:
            hier_v1 = HConfig(host=hier_host)
            hier_v1.load_from_string(switch_config)
            hier_v1.set_order_weight()
            for line in hier_v1.all_children_sorted():
                switch_config_v1 += line.cisco_style_text() + "\n"

        if preserve:
            preserve_lag_config = add_preserve_config(switch_config_v1)
            error_check_preserve_config(preserve_lag_config)
            return (preserve_lag_config, devices, unknown)

        return switch_config_v1, devices, unknown

    # defaults to aruba options file
    else:
        if custom_config:
            switch_custom_config = custom_config.get(switch_name)
            if switch_custom_config is not None:
                switch_os = "aoscx"
                options = yaml.load(open(hier_options(switch_os)))

                hier_host = Host(switch_name, switch_os, options)
                switch_config = add_custom_config(
                    switch_custom_config,
                    switch_config,
                    hier_host,
                    switch_os,
                    custom_config_file,
                )

    if preserve:
        preserve_lag_config = add_preserve_config(switch_config)
        error_check_preserve_config(preserve_lag_config)
        return (preserve_lag_config, devices, unknown)

    if reorder:
        switch_os = "aoscx"
        options = yaml.load(open(hier_options(switch_os)))
        host = Host(switch_name, switch_os, options)
        switch_config_hier = HConfig(host=host)
        switch_config_hier.load_from_string(switch_config)
        switch_config_hier.set_order_weight()
        # add ! to the end of the aruba banner.
        banner = switch_config_hier.get_child("contains", "banner")
        banner.add_child("!")
        config = ""
        for line in switch_config_hier.all_children_sorted():
            # add two spaces to indented config to match aruba formatting.
            if (
                line.cisco_style_text().startswith("  ")
                and "!" not in line.cisco_style_text()
            ):
                config += "\n" + "  " + line.cisco_style_text()
            else:
                config += "\n" + line.cisco_style_text().lstrip()
        switch_config = config

    return switch_config, devices, unknown


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
        if pair_hostname in x["config"]["DESCRIPTION"]:
            connections.append(x["config"]["PORT"])

    connections = natsort.natsorted(connections)
    return connections


def preserve_port(
    preserve,
    source_port,
    mellanox=None,
):
    """Get the nodes connected to the switch ports.

    Args:
        preserve: parsed running config
        source_port: port that is going to be assigned a LAG
        mellanox: if switch is mellanox parse the interface differently. (mellanox = 1/1, aruba/dell = 1/1/1)

    Returns:
        The LAG Number of the old running config.
    """
    for port in preserve[0][0]:
        if "lag" in port.keys() and (
            (str(source_port) == port["interface"][2:] and mellanox)
            or (str(source_port) == port["interface"][4:])
        ):
            return port["lag"]


def get_switch_nodes(
    architecture,
    switch_name,
    network_node_list,
    factory,
    sls_variables,
    preserve,
):
    """Get the nodes connected to the switch ports.

    Args:
        architecture: CSM architecture
        switch_name: Switch hostname
        network_node_list: List of nodes from the SHCD / Paddle
        factory: Node factory object
        sls_variables: Dictionary containing SLS variables.
        preserve: Parsed running config.

    Returns:
        List of nodes connected to the switch
        List of unknown nodes
    """
    nodes = []
    nodes_by_name = {}
    nodes_by_id = {}
    unknown = []

    # Make 2 dictionaries for easy node lookup
    for node in network_node_list:
        node_tmp = node.serialize()
        name = node_tmp["common_name"]

        nodes_by_name[name] = node_tmp
        nodes_by_id[node_tmp["id"]] = node_tmp

    if switch_name not in nodes_by_name.keys():
        click.secho(
            f"For switch {switch_name}, the type cannot be determined. Please check the switch name and try again.",
            fg="red",
        )
        sys.exit(1)

    for port in nodes_by_name[switch_name]["ports"]:
        destination_node_id = port["destination_node_id"]
        destination_node_name = nodes_by_id[destination_node_id]["common_name"]
        destination_rack = nodes_by_id[destination_node_id]["location"]["rack"]
        source_port = port["port"]
        destination_port = port["destination_port"]
        destination_slot = port["destination_slot"]

        shasta_name = get_shasta_name(destination_node_name, factory.lookup_mapper())
        primary_port = get_primary_port(nodes_by_name, switch_name, destination_node_id)
        if shasta_name == "ncn-m":
            new_node = {
                "subtype": "master",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "LAG_NUMBER": primary_port,
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "ncn-s":
            # ncn-s also needs destination_port to find the match
            primary_port_ncn_s = get_primary_port(
                nodes_by_name,
                switch_name,
                destination_node_id,
                destination_port,
            )
            new_node = {
                "subtype": "storage",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "LAG_NUMBER": primary_port_ncn_s,
                    "LAG_NUMBER_V1": primary_port,
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER_V1"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "ncn-w":
            new_node = {
                "subtype": "worker",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "LAG_NUMBER": primary_port,
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "cec":
            destination_rack_int = int(re.search(r"\d+", destination_rack)[0])
            for cabinets in sls_variables["HMN_MTN_CABINETS"]:
                sls_rack_int = int(re.search(r"\d+", (cabinets["Name"]))[0])
                if destination_rack_int == sls_rack_int:
                    hmn_mtn_vlan = cabinets["VlanID"]
            new_node = {
                "subtype": "cec",
                "slot": None,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "INTERFACE_NUMBER": f"{source_port}",
                    "NATIVE_VLAN": hmn_mtn_vlan,
                },
            }
            nodes.append(new_node)
        elif shasta_name == "cmm":
            destination_rack_int = int(re.search(r"\d+", destination_rack)[0])
            for cabinets in sls_variables["NMN_MTN_CABINETS"]:
                sls_rack_int = int(re.search(r"\d+", (cabinets["Name"]))[0])
                if destination_rack_int == sls_rack_int:
                    nmn_mtn_vlan = cabinets["VlanID"]
            for cabinets in sls_variables["HMN_MTN_CABINETS"]:
                sls_rack_int = int(re.search(r"\d+", (cabinets["Name"]))[0])
                if destination_rack_int == sls_rack_int:
                    hmn_mtn_vlan = cabinets["VlanID"]
            new_node = {
                "subtype": "cmm",
                "slot": None,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "LAG_NUMBER": primary_port,
                    "NATIVE_VLAN": nmn_mtn_vlan,
                    "TAGGED_VLAN": hmn_mtn_vlan,
                },
            }
            if preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name in {"uan", "login", "viz", "lmem", "gpu"}:
            primary_port_uan = get_primary_port(
                nodes_by_name,
                switch_name,
                destination_node_id,
                destination_port,
            )
            new_node = {
                "subtype": "uan",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "LAG_NUMBER": primary_port_uan,
                    "LAG_NUMBER_V1": primary_port,
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER_V1"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name in {"gateway", "ssn", "dvs"}:
            new_node = {
                "subtype": "river_ncn_node_4_port_1g_ocp",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "INTERFACE_NUMBER": f"{source_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "cn":
            new_node = {
                "subtype": "compute",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "INTERFACE_NUMBER": f"{source_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-hsn":
            new_node = {
                "subtype": "sw-hsn",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "INTERFACE_NUMBER": f"{source_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "pdu":
            new_node = {
                "subtype": "pdu",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "INTERFACE_NUMBER": f"{source_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "SubRack":
            new_node = {
                "subtype": "bmc",
                "slot": destination_slot,
                "destination_port": destination_port,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        destination_slot,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                    "INTERFACE_NUMBER": f"{source_port}",
                },
            }
            nodes.append(new_node)
        elif shasta_name == "sw-spine":
            # sw-leaf ==> sw-spine
            if switch_name.startswith("sw-leaf"):
                is_primary, primary, secondary = switch_is_primary(switch_name)
                digits = re.findall(r"(\d+)", primary)[0]
                lag_number = 100 + int(digits)

            # sw-cdu ==> sw-spine
            elif switch_name.startswith("sw-cdu"):
                lag_number = 255
                is_primary, primary, secondary = switch_is_primary(switch_name)

            # sw-leaf-bmc ==> sw-spine
            elif switch_name.startswith("sw-leaf-bmc"):
                lag_number = 255

            # sw-spine ==> sw-spine
            elif switch_name.startswith("sw-spine"):
                is_primary, primary, secondary = switch_is_primary(switch_name)
                lag_number = 256
            elif switch_name.startswith("sw-edge"):
                is_primary, primary, secondary = switch_is_primary(switch_name)
                lag_number = 250
            new_node = {
                "subtype": "spine",
                "slot": None,
                "primary": is_primary,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "LAG_NUMBER": lag_number,
                    "PORT": f"{source_port}",
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "sw-cdu":
            is_primary, primary, secondary = switch_is_primary(destination_node_name)
            # sw-spine ==> sw-cdu
            if switch_name.startswith("sw-spine"):
                digits = re.findall(r"(\d+)", primary)[0]
                lag_number = 200 + int(digits)

            # sw-cdu ==> sw-cdu
            elif switch_name.startswith("sw-cdu"):
                lag_number = 256
            new_node = {
                "subtype": "cdu",
                "slot": None,
                "primary": is_primary,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "LAG_NUMBER": lag_number,
                    "PORT": f"{source_port}",
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "sw-leaf":
            # sw-spine ==> sw-leaf
            is_primary, primary, secondary = switch_is_primary(destination_node_name)
            if switch_name.startswith("sw-spine"):
                digits = re.findall(r"(\d+)", primary)[0]
                lag_number = 100 + int(digits)

            # sw-leaf-bmc ==> sw-leaf
            elif switch_name.startswith("sw-leaf-bmc"):
                lag_number = 255

            # sw-leaf ==> sw-leaf
            elif switch_name.startswith("sw-leaf"):
                lag_number = 256
            new_node = {
                "subtype": "leaf",
                "slot": None,
                "primary": is_primary,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "LAG_NUMBER": lag_number,
                    "PORT": f"{source_port}",
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "sw-leaf-bmc":
            # sw-leaf ==> sw-leaf-bmc
            if switch_name.startswith("sw-leaf"):
                digits = re.findall(r"(\d+)", destination_node_name)[0]
                lag_number = 150 + int(digits)

            # sw-spine ==> sw-leaf-bmc
            elif switch_name.startswith("sw-spine"):
                digits = re.findall(r"(\d+)", destination_node_name)[0]
                lag_number = 150 + int(digits)
            new_node = {
                "subtype": "leaf-bmc",
                "slot": None,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "LAG_NUMBER": lag_number,
                    "PORT": f"{source_port}",
                },
            }
            if preserve and architecture == "network_v1":
                new_node["config"]["LAG_NUMBER"] = preserve_port(
                    preserve,
                    source_port,
                    mellanox=True,
                )
            elif preserve:
                new_node["config"]["LAG_NUMBER"] = preserve_port(preserve, source_port)
            nodes.append(new_node)
        elif shasta_name == "sw-edge":
            new_node = {
                "subtype": "edge",
                "slot": None,
                "config": {
                    "DESCRIPTION": get_description(
                        switch_name,
                        destination_node_name,
                        None,
                        destination_port,
                    ),
                    "PORT": f"{source_port}",
                },
            }
            nodes.append(new_node)
        else:  # pragma: no cover
            print("*********************************")
            print("Cannot determine destination connection")
            print("Source: ", switch_name)
            print("Port: ", port)
            print("Destination: ", destination_node_name)
            print("shasta_name", shasta_name)
            print("*********************************")
            unknown_description = get_description(
                switch_name,
                destination_node_name,
                destination_slot,
                destination_port,
            )
            new_node = {
                "subtype": "unknown",
                "slot": None,
                "config": {
                    "DESCRIPTION": unknown_description,
                },
            }
            nodes.append(new_node)
            unknown.append(unknown_description)
    return nodes, unknown


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


def groupby_vlan_range(vlan_list):
    """Reorders a list of VLANS to match switch format.

    Args:
        vlan_list: list of vlans

    Returns:
        list of vlans formatted
    """
    vlans = []
    for val in vlan_list:
        if val is not None:
            vlans.append(val)

    if not len(vlans):
        return ""

    def _group_id(item):
        return item[0] - item[1]

    values = []
    vlans.sort()
    for _group_id, members in groupby(enumerate(vlans), key=_group_id):  # noqa: B020
        members = list(members)
        first, last = members[0][1], members[-1][1]

        if first == last:
            values.append(str(first))
        else:
            values.append(f"{first}-{last}")

    return ",".join(values)


def parse_sls_for_config(input_json):
    """Parse the `sls_file.json` file or the JSON from SLS `/networks` API for config variables.

    Args:
        input_json: JSON from the SLS `/networks` API

    Returns:
        sls_variables: Dictionary containing SLS variables.
    """
    networks_list = []

    sls_variables = {
        "SWITCH_ASN": None,
        "CAN": None,
        "CAN_VLAN": None,
        "CAN_NETMASK": None,
        "CAN_PREFIX_LEN": None,
        "CAN_NETWORK_IP": None,
        "CHN": None,
        "CHN_VLAN": None,
        "CHN_NETMASK": None,
        "CHN_PREFIX_LEN": None,
        "CHN_NETWORK_IP": None,
        "CHN_ASN": None,
        "CMN": None,
        "CMN_VLAN": None,
        "CMN_NETMASK": None,
        "CMN_PREFIX_LEN": None,
        "CMN_NETWORK_IP": None,
        "CMN_ASN": None,
        "HMN": None,
        "HMN_VLAN": None,
        "HMN_NETMASK": None,
        "HMN_NETWORK_IP": None,
        "HMN_PREFIX_LEN": None,
        "MTL": None,
        "MTL_NETMASK": None,
        "MTL_NETWORK_IP": None,
        "MTL_PREFIX_LEN": None,
        "NMN": None,
        "NMN_VLAN": None,
        "NMN_NETMASK": None,
        "NMN_NETWORK_IP": None,
        "NMN_PREFIX_LEN": None,
        "NMN_ASN": None,
        "HMN_MTN": None,
        "HMN_MTN_NETMASK": None,
        "HMN_MTN_NETWORK_IP": None,
        "HMN_MTN_PREFIX_LEN": None,
        "NMN_MTN": None,
        "NMN_MTN_NETMASK": None,
        "NMN_MTN_NETWORK_IP": None,
        "NMN_MTN_PREFIX_LEN": None,
        "HMNLB": None,
        "HMNLB_NETMASK": None,
        "HMNLB_NETWORK_IP": None,
        "HMNLB_PREFIX_LEN": None,
        "HMNLB_TFTP": None,
        "HMNLB_DNS": None,
        "NMNLB": None,
        "NMNLB_NETMASK": None,
        "NMNLB_NETWORK_IP": None,
        "NMNLB_PREFIX_LEN": None,
        "NMNLB_TFTP": None,
        "NMNLB_DNS": None,
        "CAN_IP_GATEWAY": None,
        "CHN_IP_GATEWAY": None,
        "CMN_IP_GATEWAY": None,
        "HMN_IP_GATEWAY": None,
        "MTL_IP_GATEWAY": None,
        "NMN_IP_GATEWAY": None,
        "ncn_w001": None,
        "ncn_w002": None,
        "ncn_w003": None,
        "CAN_IP_PRIMARY": None,
        "CAN_IP_SECONDARY": None,
        "CHN_IP_PRIMARY": None,
        "CHN_IP_SECONDARY": None,
        "CMN_IP_PRIMARY": None,
        "CMN_IP_SECONDARY": None,
        "CAN_IPs": defaultdict(),
        "CHN_IPs": defaultdict(),
        "CMN_IPs": defaultdict(),
        "HMN_IPs": defaultdict(),
        "MTL_IPs": defaultdict(),
        "NMN_IPs": defaultdict(),
        "NMN_MTN_CABINETS": [],
        "HMN_MTN_CABINETS": [],
    }

    for sls_network in input_json:
        name = sls_network.get("Name", "")

        if name == "CAN":
            sls_variables["CAN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["CAN_NETMASK"] = sls_variables["CAN"].netmask
            sls_variables["CAN_PREFIX_LEN"] = sls_variables["CAN"].prefixlen
            sls_variables["CAN_NETWORK_IP"] = sls_variables["CAN"].ip
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "bootstrap_dhcp":
                    sls_variables["CAN_IP_GATEWAY"] = subnets["Gateway"]
                    sls_variables["CAN_VLAN"] = subnets["VlanID"]
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "can-switch-1":
                            sls_variables["CAN_IP_PRIMARY"] = ip["IPAddress"]
                        elif ip["Name"] == "can-switch-2":
                            sls_variables["CAN_IP_SECONDARY"] = ip["IPAddress"]
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if "ncn-w" in ip["Name"]:
                            sls_variables["CAN_IPs"][ip["Name"]] = ip["IPAddress"]

        if name == "CHN":
            sls_variables["CHN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["CHN_NETMASK"] = sls_variables["CHN"].netmask
            sls_variables["CHN_PREFIX_LEN"] = sls_variables["CHN"].prefixlen
            sls_variables["CHN_NETWORK_IP"] = sls_variables["CHN"].ip
            sls_variables["CHN_ASN"] = sls_network.get("ExtraProperties", {}).get(
                "MyASN",
                {},
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "bootstrap_dhcp":
                    sls_variables["CHN_IP_GATEWAY"] = subnets["Gateway"]
                    sls_variables["CHN_VLAN"] = subnets["VlanID"]
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "chn-switch-1":
                            sls_variables["CHN_IP_PRIMARY"] = ip["IPAddress"]
                        elif ip["Name"] == "chn-switch-2":
                            sls_variables["CHN_IP_SECONDARY"] = ip["IPAddress"]
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        sls_variables["CHN_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "CMN":
            sls_variables["CMN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["CMN_NETMASK"] = sls_variables["CMN"].netmask
            sls_variables["CMN_PREFIX_LEN"] = sls_variables["CMN"].prefixlen
            sls_variables["CMN_NETWORK_IP"] = sls_variables["CMN"].ip
            sls_variables["CMN_ASN"] = sls_network.get("ExtraProperties", {}).get(
                "MyASN",
                {},
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "bootstrap_dhcp":
                    sls_variables["CMN_IP_GATEWAY"] = subnets["Gateway"]
                    sls_variables["CMN_VLAN"] = subnets["VlanID"]
                if subnets["Name"] == "network_hardware":
                    for ip in subnets["IPReservations"]:
                        if "sw" in ip["Name"]:
                            sls_variables["CMN_IPs"][ip["Name"]] = ip["IPAddress"]
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if "ncn-w" in ip["Name"]:
                            sls_variables["CMN_IPs"][ip["Name"]] = ip["IPAddress"]
        elif name == "HMN":
            sls_variables["HMN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["HMN_NETMASK"] = sls_variables["HMN"].netmask
            sls_variables["HMN_PREFIX_LEN"] = sls_variables["HMN"].prefixlen
            sls_variables["HMN_NETWORK_IP"] = sls_variables["HMN"].ip
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "network_hardware":
                    sls_variables["HMN_IP_GATEWAY"] = subnets["Gateway"]
                    sls_variables["HMN_VLAN"] = subnets["VlanID"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["HMN_IPs"][ip["Name"]] = ip["IPAddress"]
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if "ncn-w" in ip["Name"]:
                            sls_variables["HMN_IPs"][ip["Name"]] = ip["IPAddress"]
        elif name == "MTL":
            sls_variables["MTL"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["MTL_NETMASK"] = sls_variables["MTL"].netmask
            sls_variables["MTL_PREFIX_LEN"] = sls_variables["MTL"].prefixlen
            sls_variables["MTL_NETWORK_IP"] = sls_variables["MTL"].ip
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "network_hardware":
                    sls_variables["MTL_IP_GATEWAY"] = subnets["Gateway"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["MTL_IPs"][ip["Name"]] = ip["IPAddress"]

        elif name == "NMN":
            sls_variables["NMN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["NMN_NETMASK"] = sls_variables["NMN"].netmask
            sls_variables["NMN_PREFIX_LEN"] = sls_variables["NMN"].prefixlen
            sls_variables["NMN_NETWORK_IP"] = sls_variables["NMN"].ip
            sls_variables["SWITCH_ASN"] = sls_network.get("ExtraProperties", {}).get(
                "PeerASN",
                {},
            )
            sls_variables["NMN_ASN"] = sls_network.get("ExtraProperties", {}).get(
                "MyASN",
                {},
            )
            sls_variables["NMN_NETMASK"] = sls_variables["NMN"].netmask
            sls_variables["NMN_PREFIX_LEN"] = sls_variables["NMN"].prefixlen
            sls_variables["NMN_NETWORK_IP"] = sls_variables["NMN"].ip
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "ncn-w001":
                            sls_variables["ncn_w001"] = ip["IPAddress"]
                        elif ip["Name"] == "ncn-w002":
                            sls_variables["ncn_w002"] = ip["IPAddress"]
                        elif ip["Name"] == "ncn-w003":
                            sls_variables["ncn_w003"] = ip["IPAddress"]
                if subnets["Name"] == "bootstrap_dhcp":
                    for ip in subnets["IPReservations"]:
                        if "ncn-w" in ip["Name"]:
                            sls_variables["NMN_IPs"][ip["Name"]] = ip["IPAddress"]
                elif subnets["Name"] == "network_hardware":
                    sls_variables["NMN_IP_GATEWAY"] = subnets["Gateway"]
                    sls_variables["NMN_VLAN"] = subnets["VlanID"]
                    for ip in subnets["IPReservations"]:
                        sls_variables["NMN_IPs"][ip["Name"]] = ip["IPAddress"]
        elif name == "NMN_MTN":
            sls_variables["NMN_MTN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["NMN_MTN_NETMASK"] = sls_variables["NMN_MTN"].netmask
            sls_variables["NMN_MTN_PREFIX_LEN"] = sls_variables["NMN_MTN"].prefixlen
            sls_variables["NMN_MTN_NETWORK_IP"] = sls_variables["NMN_MTN"].ip
            sls_variables["NMN_MTN_CABINETS"] = list(
                sls_network.get("ExtraProperties", {}).get("Subnets", {}),
            )

        elif name == "HMN_MTN":
            sls_variables["HMN_MTN"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            sls_variables["HMN_MTN_NETMASK"] = sls_variables["HMN_MTN"].netmask
            sls_variables["HMN_MTN_PREFIX_LEN"] = sls_variables["HMN_MTN"].prefixlen
            sls_variables["HMN_MTN_NETWORK_IP"] = sls_variables["HMN_MTN"].ip
            sls_variables["HMN_MTN_CABINETS"] = list(
                sls_network.get("ExtraProperties", {}).get("Subnets", {}),
            )
        elif name == "HMNLB":
            sls_variables["HMNLB"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "hmn_metallb_address_pool":
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "cray-tftp":
                            sls_variables["HMNLB_TFTP"] = ip["IPAddress"]
                        elif ip["Name"] == "unbound":
                            sls_variables["HMNLB_DNS"] = ip["IPAddress"]
            sls_variables["HMNLB_NETMASK"] = sls_variables["HMNLB"].netmask
            sls_variables["HMNLB_PREFIX_LEN"] = sls_variables["HMNLB"].prefixlen
            sls_variables["HMNLB_NETWORK_IP"] = sls_variables["HMNLB"].ip
            sls_variables["HMNLB_CABINETS"] = list(
                sls_network.get("ExtraProperties", {}).get("Subnets", {}),
            )
        elif name == "NMNLB":
            sls_variables["NMNLB"] = netaddr.IPNetwork(
                sls_network.get("ExtraProperties", {}).get(
                    "CIDR",
                    "",
                ),
            )
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                if subnets["Name"] == "nmn_metallb_address_pool":
                    for ip in subnets["IPReservations"]:
                        if ip["Name"] == "cray-tftp":
                            sls_variables["NMNLB_TFTP"] = ip["IPAddress"]
                        elif ip["Name"] == "unbound":
                            sls_variables["NMNLB_DNS"] = ip["IPAddress"]
            sls_variables["NMNLB_NETMASK"] = sls_variables["NMNLB"].netmask
            sls_variables["NMNLB_PREFIX_LEN"] = sls_variables["NMNLB"].prefixlen
            sls_variables["NMNLB_NETWORK_IP"] = sls_variables["NMNLB"].ip
            sls_variables["NMNLB_CABINETS"] = list(
                sls_network.get("ExtraProperties", {}).get("Subnets", {}),
            )
        for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):

            vlan = subnets.get("VlanID", "")
            networks_list.append([name, vlan])

    networks_list = {tuple(x) for x in networks_list}
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


def get_primary_port(
    nodes_by_name,
    switch_name,
    destination_node_id,
    destination_port=None,
):
    """Return the primary switch port number for a connection to a node.

    Args:
        nodes_by_name: Dictionary containing the node list where hostname is the key
        switch_name: Switch hostname
        destination_node_id: The node id of the destination device.
        destination_port: (Optional, only used with ncn-s) The destination port

    Returns:
        port: Port number of the primary connection to a device.
    """
    is_primary, primary, secondary = switch_is_primary(switch_name)

    for y in nodes_by_name[primary]["ports"]:
        if y["destination_node_id"] == destination_node_id:
            if not destination_port:
                return y["port"]
            # Since ncn-s can have multiple connections to a device, returns the correct one
            elif destination_port and y["destination_port"] == destination_port:
                return y["port"]


def get_description(
    source_node_name,
    destination_node_name,
    destination_slot,
    destination_port,
):
    """Return the port description for a node.

    Args:
        source_node_name: source device name
        destination_node_name: destination device name
        destination_slot: device slot name
        destination_port: device port number

    Returns:
        description: string for port/interface description
    """
    description = f"{destination_node_name}:{destination_slot}:{destination_port}<=={source_node_name}"
    if destination_slot is None:
        description = f"{destination_node_name}:{destination_port}<=={source_node_name}"

    return description
