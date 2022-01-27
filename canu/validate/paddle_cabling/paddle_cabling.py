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
"""CANU commands that validate the shcd against the current network cabling."""
import ipaddress
import json
import sys
from os import path
from pathlib import Path

import click
import click_spinner
import requests
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup
from click_option_group import RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS
from click_params import Ipv4AddressListParamType
from netmiko import ssh_exception
from ruamel.yaml import YAML

from canu.report.switch.cabling.cabling import get_lldp
from canu.utils.cache import cache_directory
from canu.validate.network.cabling.cabling import node_model_from_canu
from canu.validate.paddle.paddle import node_model_from_paddle
from canu.validate.shcd.shcd import node_list_warnings
from canu.validate.shcd_cabling.shcd_cabling import combine_shcd_cabling
from canu.validate.shcd_cabling.shcd_cabling import print_combined_nodes
from network_modeling.NetworkNodeFactory import NetworkNodeFactory

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
        out: Name of the output file
    """
    ccj_json = json.load(ccj)
    architecture = ccj_json.get("architecture")

    if architecture is None:
        click.secho(
            "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ.",
            fg="red",
        )
        return

    # IP Address / LLDP Parsing
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
                    get_lldp(str(ip), credentials, return_error=True)

                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    ssh_exception.NetmikoTimeoutException,
                    ssh_exception.NetmikoAuthenticationException,
                ) as err:
                    exception_type = type(err).__name__

                    if exception_type == "HTTPError":
                        error_message = f"Error connecting to switch {ip}, check the IP, username, or password."
                    elif exception_type == "ConnectionError":
                        error_message = f"Error connecting to switch {ip}, check the IP address and try again."
                    elif exception_type == "NetmikoTimeoutException":
                        error_message = f"Timeout error connecting to {ip}. Check the IP address and try again."
                    elif exception_type == "NetmikoAuthenticationException":
                        error_message = f"Auth error connecting to {ip}. Check the credentials or IP address and try again"
                    else:
                        error_message = f"Error connecting to switch {ip}."

                    errors.append([str(ip), error_message])

    # Create Paddle Node factory
    paddle_factory = NetworkNodeFactory(architecture_version=architecture)
    paddle_node_list, paddle_warnings = node_model_from_paddle(paddle_factory, ccj_json)

    # Create Cabling Node factory
    cabling_factory = NetworkNodeFactory(architecture_version=architecture)

    # Open the updated cache to model nodes
    with open(canu_cache_file, "r+") as file:
        canu_cache = yaml.load(file)

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
