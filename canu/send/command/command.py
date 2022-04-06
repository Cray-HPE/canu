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
"""CANU send command."""
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_result

from canu.utils.inventory import inventory

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent


@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
)
@click.option(
    "--network",
    default="HMN",
    show_default=True,
    type=click.Choice(["HMN", "CMN"], case_sensitive=False),
    help="The network that is used to connect to the switches.",
)
@click.option(
    "--log",
    "log_",
    is_flag=True,
    help="enable logging.",
    required=False,
)
@click.option(
    "--command",
    help="command to send to the switches e.g. show version",
    required=True,
    prompt="command to send to the switches e.g. show version",
)
@click.option(
    "--switch-type",
    required=False,
    help="The type of switches to run the command on, the default for this is all switches e.g. spine",
)
@click.option(
    "--name",
    required=False,
    help="The name of the switch to run the command on, the default for this is all switches e.g. sw-leaf-bmc-001",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.pass_context
def command(
    ctx,
    username,
    password,
    sls_file,
    sls_address,
    network,
    log_,
    command,
    switch_type,
    name,
):
    """Canu send command."""
    if not password:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )
    switch_inventory = inventory(username, password, network, sls_file)

    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 10,
            },
        },
        inventory=switch_inventory,
        logging={"enabled": log_, "to_console": True, "level": "DEBUG"},
    )

    def send_command():
        if switch_type:
            nr_switch_type = nr.filter(type=switch_type)
            results = nr_switch_type.run(
                task=netmiko_send_command,
                command_string=command,
            )
        if name:
            nr_switch_type = nr.filter(filter_func=lambda h: name in h.name)
            results = nr_switch_type.run(
                task=netmiko_send_command,
                command_string=command,
            )
        else:
            results = nr.run(
                task=netmiko_send_command,
                command_string=command,
            )
        return results

    with click_spinner.spinner():
        print_result(send_command())
