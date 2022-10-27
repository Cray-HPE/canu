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
"""CANU commands that generate the config of the entire Shasta network."""
import json
import logging
from os import environ, makedirs, path
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import requests
from ruamel.yaml import YAML
import urllib3

from canu.generate.switch.config.config import (
    generate_switch_config,
    get_shasta_name,
    parse_sls_for_config,
    rename_sls_hostnames,
)
from canu.utils.cache import cache_directory
from canu.validate.paddle.paddle import node_model_from_paddle
from canu.validate.shcd.shcd import node_model_from_shcd, shcd_to_sheets

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

log = logging.getLogger(("generate_network_config"))

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
    "--folder",
    help="Folder to store config files",
    required=True,
    prompt="Folder for configs",
)
@click.option(
    "--custom-config",
    help="Custom switch configuration",
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
@click.option(
    "--bgp-control-plane",
    type=click.Choice(["CMN", "CHN"], case_sensitive=False),
    help="Network used for BGP control plane",
    required=False,
    default="CHN",
)
@click.option(
    "--log",
    "log_",
    help="Level of logging.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="ERROR",
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
    sls_file,
    auth_token,
    sls_address,
    folder,
    preserve,
    custom_config,
    reorder,
    bgp_control_plane,
    log_,
):
    """Generate the config of all switches (Aruba, Dell, or Mellanox) on the network using the SHCD.

    In order to generate network switch config, a valid SHCD must be passed in and system variables must be read in from either
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
        sls_file: Directory containing the CSI json file
        auth_token: Token for SLS authentication
        sls_address: The address of SLS
        folder: Folder to store config files
        preserve: Folder where switch running configs exist.  This folder should be populated from the "canu backup network" command.
        custom_config: yaml file containing customized switch configurations which is merged with the generated config.
        reorder: Filters generated configurations through hier_config generate a more natural running-configuration order.
        bgp_control_plane: Network used for BGP control plane
        log_: Level of logging.
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

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

    # make folder
    if not path.exists(folder):
        makedirs(folder)
    all_devices = {
        "cdu",
        "cec",
        "cmm",
        "leaf",
        "leaf-bmc",
        "master",
        "spine",
        "storage",
        "uan",
        "worker",
        "edge",
    }
    config_devices = set()
    all_unknown = []
    for node in network_node_list:
        switch_name = node.common_name()
        node_shasta_name = get_shasta_name(switch_name, factory.lookup_mapper())

        if (
            node_shasta_name
            in [
                "sw-cdu",
                "sw-leaf-bmc",
                "sw-leaf",
                "sw-spine",
            ]
            or node_shasta_name == "sw-edge"
            and float(csm) >= 1.2
        ):

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
                bgp_control_plane,
            )
            all_unknown.extend(unknown)
            config_devices.update(devices)
            with open(f"{folder}/{switch_name}.cfg", "w+") as f:
                f.write(switch_config)
            if "# Custom configurations" in switch_config:
                click.secho(
                    f"{switch_name} Customized Configurations have been detected in the generated switch configurations",
                    fg="yellow",
                )
            else:
                click.secho(f"{switch_name} Config Generated", fg="bright_white")
    missing_devices = all_devices.difference(config_devices)
    dash = "-" * 60
    if len(missing_devices) > 0:
        log.warning(
            "The following devices often exist in Plan-of-Record system configurations, but",
        )
        log.warning(
            "were not found on the current system.  This warning is simply a last minute",
        )
        log.warning(
            "reminder to completely check the currrent system configuration for the following nodes:",
        )
        for x in missing_devices:
            log.warning(f"    {x}")

    if len(all_unknown) > 0:
        click.secho(
            (
                "\n"
                "Warning\n"
                "CANU is unable to find a network configuration template for the following connections.\n"
                "    Applying the generated configurations as-iswill likely result in loss of connectivity\n"
                "    with these devices.  Two possibilities exist:\n"
                "    1. The devices do not follow Plan-of-Record cabling specifications.\n"
                "       In this case either bring the system to PoR or use the next possibility.\n"
                "    2. The connections are meant to be configured using a missing --custom-config YAML.\n"
                "       In this case add the missing configurations to a --custom-config YAML file.\n",
            ),
            fg="red",
        )
        click.secho(dash)
        for x in all_unknown:
            click.secho(x, fg="bright_white")

    return
