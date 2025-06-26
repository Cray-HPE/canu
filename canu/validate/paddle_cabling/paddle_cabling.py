# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
"""CANU commands that validate the shcd against the current network cabling."""
import ipaddress
import json
import logging
from os import path
from pathlib import Path
import sys
import datetime
import re
from collections import defaultdict

import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import requests
from ruamel.yaml import YAML

from canu.report.switch.cabling.cabling import get_lldp
from canu.style import Style
from canu.utils.cache import cache_directory
from canu.validate.network.cabling.cabling import node_model_from_canu
from canu.validate.paddle.paddle import node_model_from_paddle
from canu.validate.shcd.shcd import node_list_warnings
from canu.validate.shcd_cabling.shcd_cabling import (
    combine_shcd_cabling,
    print_combined_nodes,
)

yaml = YAML()

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent

# Schema and Data files
canu_cache_file = path.join(cache_directory(), "canu_cache.yaml")
canu_config_file = path.join(project_root, "canu", "canu.yaml")

# Get CSM versions from canu.yaml
with open(canu_config_file, "r") as canu_f:
    canu_config = yaml.load(canu_f)

csm_options = canu_config["csm_versions"]

log = logging.getLogger("validate_paddle_cabling")


def create_cache_structure_from_lldp(switch_info, lldp_dict, arp):
    """Create a cache structure from LLDP data that matches the expected format.
    
    Args:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary
        
    Returns:
        Dictionary representing switch in cache format
    """
    switch = {
        "ip_address": switch_info["ip"],
        "cabling": defaultdict(list),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": switch_info["hostname"],
        "platform_name": switch_info["platform_name"],
        "vendor": switch_info["vendor"],
    }

    for port_number, port in lldp_dict.items():
        for index, _entry in enumerate(port):
            arp_list = []
            if port[index]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == port[index]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)
            neighbor_description = (
                f"{port[index]['chassis_description'][:54]} {str(arp_list)}"
            )
            port_info = {
                "neighbor": port[index]["chassis_name"],
                "neighbor_description": neighbor_description,
                "neighbor_port": port[index]["port_id"],
                "neighbor_port_description": re.sub(
                    r"(Interface\s+\d+ as )",
                    "",
                    port[index]["port_description"],
                ),
                "neighbor_chassis_id": port[index]["chassis_id"],
            }

            switch["cabling"][port_number].append(port_info)
    
    switch["cabling"] = dict(switch["cabling"])
    return switch


@click.command(
    cls=Style.CanuHelpColorsCommand,
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
    "--ccj",
    help="CCJ (CSM Cabling JSON) File containing system topology.",
    type=click.File("r"),
    required=True,
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
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.pass_context
def paddle_cabling(
    ctx,
    csm,
    ccj,
    ips,
    ips_file,
    username,
    password,
    log_,
    out,
):
    """Validate a CCJ file against the current network cabling.

    Pass in a CCJ file to validate that it works architecturally.

    This command will also use LLDP to determine the neighbors of the IP addresses passed in to validate that the network
    is properly connected architecturally.

    The validation will ensure that spine switches, leaf switches,
    edge switches, and nodes all are connected properly.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        csm: csm version
        ccj: Paddle CCJ file
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        log_: Level of logging
        out: Name of the output file
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

    ccj_json = json.load(ccj)
    architecture = ccj_json.get("architecture")

    if architecture is None:
        click.secho(
            "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ.",
            fg="red",
        )
        return

    # Create Paddle Node factory and model
    log.debug("Creating model from CCJ data")
    paddle_factory = NetworkNodeFactory(architecture_version=architecture)
    paddle_node_list, paddle_warnings = node_model_from_paddle(paddle_factory, ccj_json)

    # IP Address / LLDP Parsing
    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    errors = []
    ips_length = len(ips)
    
    # Create in-memory cache structure from live LLDP data
    switches_list = []

    if ips:
        with click_spinner.spinner(
            beep=False,
            disable=False,
            force=False,
            stream=sys.stdout,
        ):
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    # Get LLDP info directly (without caching to file)
                    switch_info, lldp_dict, arp = get_lldp(str(ip), credentials, return_error=True)
                    
                    if switch_info and lldp_dict:
                        # Create cache structure from live LLDP data
                        switch_cache_entry = create_cache_structure_from_lldp(switch_info, lldp_dict, arp)
                        switches_list.append(switch_cache_entry)

                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    NetmikoTimeoutException,
                    NetmikoAuthenticationException,
                ) as err:
                    exception_type = type(err).__name__

                    if exception_type == "HTTPError":
                        error_message = f"Error connecting to switch {ip}, check the IP, username, or password."
                    elif exception_type == "ConnectionError":
                        error_message = f"Error connecting to switch {ip}, check the entered username, IP address and password."
                    elif exception_type == "NetmikoTimeoutException":
                        error_message = f"Timeout error connecting to {ip}. Check the IP address and try again."
                    elif exception_type == "NetmikoAuthenticationException":
                        error_message = f"Auth error connecting to {ip}. Check the credentials or IP address and try again"
                    else:
                        error_message = f"Error connecting to switch {ip}."

                    errors.append([str(ip), error_message])

    # Create in-memory cache structure that matches expected format
    canu_cache = {
        "version": "1.0",  # Using a default version
        "switches": switches_list
    }

    # Create Cabling Node factory and model
    log.debug("Creating model from switch LLDP data")
    cabling_factory = NetworkNodeFactory(architecture_version=architecture)
    cabling_node_list, cabling_warnings = node_model_from_canu(
        cabling_factory,
        canu_cache,
        ips,
    )

    double_dash = "=" * 100

    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "CCJ vs Cabling",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)

    # Combine the Paddle and Cabling nodes
    combined_nodes = combine_shcd_cabling(
        paddle_node_list,
        cabling_node_list,
        canu_cache,
        ips,
        csm,
    )

    print_combined_nodes(combined_nodes, out, input_type="CCJ")

    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "CCJ Warnings",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)
    node_list_warnings(paddle_node_list, paddle_warnings, out)

    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "Cabling Warnings",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)
    node_list_warnings(cabling_node_list, cabling_warnings, out)

    if len(errors) > 0:
        click.echo("\n", file=out)
        click.echo(double_dash, file=out)
        click.secho(
            "Errors",
            fg="red",
            file=out,
        )
        click.echo(double_dash, file=out)
        for error in errors:
            click.echo(
                "{:<15s} - {}".format(error[0], error[1]),
                file=out,
            )
