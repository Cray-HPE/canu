# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""CANU backup network config."""
import logging
import os
import sys
from pathlib import Path

import click
import click_spinner
from netutils.config.clean import sanitize_config
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko import netmiko_send_command
from nornir_salt.plugins.functions import ResultSerializer
from nornir_salt.plugins.tasks import tcp_ping
from nornir_scrapli.tasks import send_command

from canu.style import Style
from canu.utils.inventory import inventory


def backup_switches(online_hosts, folder, sanitized=True):
    """Backup switch configurations to specified folder.

    Args:
        online_hosts: Nornir inventory with online switches
        folder: Directory to save backup files
        sanitized: Whether to remove sensitive data

    Returns:
        List of saved filenames
    """
    # Sanitization filters to remove sensitive data
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

    def save_config_to_file(hostname, config):
        if sanitized:
            config = sanitize_config(config, sanitize_filters)
        filename = f"{hostname}.cfg"
        filepath = os.path.join(folder, filename)
        with open(filepath, "w") as f:
            f.write(config)
        return filename

    # Create backup folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    # Get configs from all switch types
    backup_results = {}

    # Mellanox switches
    mellanox_backup = online_hosts.filter(platform="mellanox").run(
        task=netmiko_send_command,
        enable=True,
        command_string="show running-config expanded",
    )
    backup_results.update(mellanox_backup)

    # Aruba switches
    aruba_backup = online_hosts.filter(platform="aruba_aoscx").run(
        task=send_command,
        command="show running-config",
    )
    backup_results.update(aruba_backup)

    # Dell switches
    dell_backup = online_hosts.filter(platform="dell_os10").run(
        task=netmiko_send_command,
        enable=True,
        command_string="show running-configuration",
    )
    backup_results.update(dell_backup)

    # Save backup files
    saved_files = []
    for hostname in backup_results:
        if not backup_results[hostname].failed:
            filename = save_config_to_file(
                hostname=hostname,
                config=backup_results[hostname][0].result,
            )
            saved_files.append(filename)

    return saved_files


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
    cls=Style.CanuHelpColorsCommand,
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
    help="Folder to store config files",
    required=True,
    prompt="Folder for configs",
)
@click.option(
    "--no-sanitize",
    help="Retain sensitive data (skip sanitization)",
    is_flag=True,
    required=False,
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
    no_sanitize,
):
    """Canu backup network config."""
    if not password:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )

    # set to ERROR otherwise nornir plugin logs debug messages to the screen.
    logging.basicConfig(level="ERROR")
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

    # check if switch is reachable before backing up config

    ping_check = nr.run(task=tcp_ping)
    result_dictionary = ResultSerializer(ping_check)
    unreachable_hosts = []

    for hostname, result in result_dictionary.items():
        if result["tcp_ping"][22] is False:
            click.secho(
                f"{hostname} is not reachable via SSH, skipping backup.",
                fg="red",
            )
            unreachable_hosts.append(hostname)

    online_hosts = nr.filter(~F(name__in=unreachable_hosts))

    with click_spinner.spinner(
        beep=False,
        disable=False,
        force=False,
        stream=sys.stdout,
    ):
        print(
            "  Connecting",
            end="\r",
        )
        saved_files = backup_switches(online_hosts, folder, sanitized=not no_sanitize)

    click.secho("\nRunning Configs Saved\n---------------------", fg="green")
    for filename in saved_files:
        click.secho(f"{os.path.basename(filename)}", fg="green")
