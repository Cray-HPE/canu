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
"""CANU commands that test the network."""
import json
import logging
import sys
from os import path
from pathlib import Path

import click
import click_spinner
import yaml
from click_help_colors import HelpColorsCommand
from nornir import InitNornir
from nornir.core.filter import F
from nornir_salt import netmiko_send_commands
from nornir_salt import TabulateFormatter
from nornir_salt import tcp_ping
from nornir_salt import TestsProcessor
from nornir_salt.plugins.functions import ResultSerializer

from canu.utils.inventory import inventory

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys,
                                             "_MEIPASS"
                                             ):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent


@click.option("--username",
              default="admin",
              show_default=True,
              help="Switch username"
              )
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
    "--json",
    "json_",
    is_flag=True,
    help="JSON output.",
    required=False,
)
@click.option("--sls-address",
              default="api-gw-service-nmn.local",
              show_default=True
              )
@click.pass_context
def test(
        ctx,
        username,
        password,
        sls_file,
        sls_address,
        network,
        log_,
        json_,
):
    """Canu test commands."""
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

    # get the switch vendor name from the inventory
    # this is used to determine which tests to run
    platform = nr.filter(F(platform="aruba_os"))
    if platform.inventory.hosts.keys():
        vendor = "aruba"
    else:
        vendor = "dellanox"

    test_file = path.join(
        project_root,
        "canu",
        "test",
        vendor,
        "test_suite.yaml",
    )

    with open(test_file) as f:
        test_suite = yaml.safe_load(f.read())

    # check if switch is reachable before running tests
    ping_check = nr.run(task=tcp_ping)
    result_dictionary = ResultSerializer(ping_check)
    unreachable_hosts = []

    for hostname, result in result_dictionary.items():
        if result["tcp_ping"][22] is False:
            click.secho(
                f"{hostname} is not reachable via SSH, skipping tests.",
                fg="red",
            )
            unreachable_hosts.append(hostname)

    online_hosts = nr.filter(~F(name__in=unreachable_hosts))

    tests = online_hosts.with_processors([TestsProcessor(test_suite)])

    switch_commands = {"spine": [], "leaf-bmc": [], "leaf": [], "cdu": []}

    dict_results = {}
    pretty_results = []

    # get the commands to run for each switch type'
    with click_spinner.spinner():
        for switch in switch_commands.keys():
            print(
                "  Connecting",
                end="\r",
            )
            switch_nr = tests.filter(type=switch)

            for item in test_suite:
                device = item.get("device")

                for switch_type in device:

                    if switch_type == switch and isinstance(item["task"], str):
                        switch_commands[switch].append(item["task"])
            results = switch_nr.run(
                task=netmiko_send_commands,
                commands=switch_commands[switch],
            )

            dict_results.update(
                ResultSerializer(results, add_details=False, to_dict=True),
            )

            pretty_results += ResultSerializer(results,
                                               add_details=True,
                                               to_dict=False
                                               )

    if json_:
        click.secho(json.dumps(dict_results, indent=4))
    else:
        print(
            TabulateFormatter(
                pretty_results,
                tabulate="brief",
            ),
        )
