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
"""CANU support file."""
import os
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from netutils.config.clean import sanitize_config
from nornir import InitNornir
from nornir_netmiko import netmiko_send_command

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
    "--folder",
    help="Folder to store support files",
    required=True,
    prompt="Folder for support files",
)
@click.option(
    "--unsanitized",
    help="Retain sensitive data",
    is_flag=True,
    required=False,
)
@click.option(
    "--name",
    "switch_name",
    required=False,
    help="The name of the switch that you want to back up. e.g. 'sw-spine-001'",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.pass_context
def network(
    ctx,
    username,
    password,
    sls_file,
    sls_address,
    network,
    log_,
    folder,
    unsanitized,
    switch_name,
):
    """Canu backup network config."""
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

    # Save the netmiko config.
    def save_config_to_file(hostname, config):
        if not unsanitized:
            config = sanitize_config(config, sanitize_filters)
        filename = f"{hostname}.cfg"
        with open(os.path.join(folder, filename), "w") as f:
            f.write(config)
            click.secho(f"{filename}", fg="green")

    # Use netmiko to SSH to switches and retrieve config.
    def get_netmiko_backups():
        # If we only want to backup one switch.
        if switch_name:
            nr_name = nr.filter(filter_func=lambda h: switch_name in h.name)
            backup_results = nr_name.run(
                task=netmiko_send_command,
                enable=True,
                command_string="show run",
            )
        else:
            backup_results = nr.run(
                task=netmiko_send_command,
                enable=True,
                command_string="show run",
            )
        click.secho("\nRunning Configs Saved\n---------------------", fg="green")
        for hostname in backup_results:
            exist = os.path.exists(folder)
            if not exist:
                os.makedirs(folder)
            save_config_to_file(
                hostname=hostname,
                config=backup_results[hostname][0].result,
            )

    # filters to sanitize sensitive data.
    sanitize_filters = [
        {
            "regex": r"()(?<=ciphertext).+",
            "replace": r"\1 <removed>",
        },
        {
            "regex": r"()(?<=password 7).+",
            "replace": r"\1 <removed>",
        },
        {
            "regex": r"()(?<=password).+",
            "replace": r"\1 <removed>",
        },
        {
            "regex": r"()(?<=md5).+",
            "replace": r"\1 <removed>",
        },
    ]
    with click_spinner.spinner():
        get_netmiko_backups()
