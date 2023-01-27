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
"""CANU commands that report the configuration version."""
import logging

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from nornir import InitNornir
from nornir.core.filter import F
from nornir_salt.plugins.tasks import netmiko_send_commands
from nornir_scrapli.tasks import send_command
from ttp import ttp

from canu.utils.host_alive import host_alive
from canu.utils.inventory import inventory


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
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.pass_context
def version(ctx, username, password, sls_file, sls_address, network, log_):
    """Report Switch Version.

    Args:
        ctx: CANU context settings
        username: Switch username
        password: Switch password
        sls_file: JSON file containing SLS data
        sls_address: The address of SLS
        network: The network that is used to connect to the switches.
        log_: enable logging
    """
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

    online_hosts, unreachable_hosts = host_alive(nr)

    if unreachable_hosts:
        for switch in unreachable_hosts:
            click.secho(
                f"WARNING: Could not reach {switch} via SSH, skipping version check",
                fg="red",
            )

    # ttp template to get CSM version and CANU version
    banner_ttp_aruba = (
        "# CSM version:  {{ csm_version }}\n# CANU version: {{ canu_version }}"
    )
    banner_ttp_dell = (
        " # CSM version:  {{ csm_version }}\n # CANU version: {{ canu_version }}"
    )
    banner_ttp_mellanox = (
        "    # CSM version:  {{ csm_version }}\n    # CANU version: {{ canu_version }}"
    )

    version = {}
    aruba_hosts = online_hosts.filter(F(platform="aruba_aoscx"))
    mellanox_hosts = online_hosts.filter(F(platform="mellanox"))
    dell_hosts = online_hosts.filter(F(platform="dell_os10"))

    # run the version check
    with click_spinner.spinner():
        print(
            "  Running version check on switches...",
            end="\r",
        )
        aruba_banner_check = aruba_hosts.run(
            task=send_command,
            command="show banner exec",
        )
        mellanox_banner_check = mellanox_hosts.run(
            task=netmiko_send_commands,
            commands="show banner",
        )
        dell_banner_check = dell_hosts.run(
            task=netmiko_send_commands,
            commands="show running-configuration | grep banner",
        )

    for switches in aruba_banner_check.keys():
        parser = ttp(
            data=str(aruba_banner_check[switches][0]),
            template=banner_ttp_aruba,
        )
        parser.parse()
        version[switches] = parser.result()

    for switches in mellanox_banner_check.keys():
        parser = ttp(
            data=str(mellanox_banner_check[switches][1]),
            template=banner_ttp_mellanox,
        )
        parser.parse()
        version[switches] = parser.result()

    for switches in dell_banner_check.keys():
        parser = ttp(data=str(dell_banner_check[switches][1]), template=banner_ttp_dell)
        parser.parse()
        version[switches] = parser.result()

    click.secho(
        "{:<17} {:<17} {:<5}".format("SWITCH", "CANU VERSION", "CSM VERSION"),
        fg="bright_white",
    )
    for key, value in version.items():
        if not value[0][0]:
            version[key][0][0] = {
                "canu_version": "BANNER NOT FOUND",
                "csm_version": "N/A",
            }
            click.secho(
                "{:<17} {:<17} {:<5}".format(
                    key,
                    value[0][0]["canu_version"],
                    value[0][0]["csm_version"],
                ),
                fg="red",
            )
        else:
            click.secho(
                "{:<17} {:<17} {:<5}".format(
                    key,
                    value[0][0]["canu_version"],
                    value[0][0]["csm_version"],
                ),
                fg="green",
            )
