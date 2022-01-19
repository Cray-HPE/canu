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
from os import path
from pathlib import Path
import pprint
import sys

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from nornir import InitNornir
from nornir_salt import netmiko_send_commands, TabulateFormatter, TestsProcessor
from nornir_salt.plugins.functions import ResultSerializer
import yaml

from canu.generate.switch.config.config import parse_sls_for_config
from canu.utils.sls import pull_sls_networks

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent

test_file = path.join(
    project_root,
    "canu",
    "test",
    "aruba",
    "test_suite.yaml",
)


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
    "--json",
    "json_",
    is_flag=True,
    help="JSON output.",
    required=False,
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
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
        sls_json = pull_sls_networks()

    if not password:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )
    # set to ERROR otherwise nornir plugin logs debug messages to the screen.
    logging.basicConfig(level="ERROR")

    sls_variables = parse_sls_for_config(sls_json)

    inventory = {"groups": "shasta", "hosts": {}}
    for k in sls_variables[network + "_IPs"]:
        if "sw" in k:
            inventory["hosts"].update(
                {
                    k: {
                        "hostname": str(sls_variables[network + "_IPs"][k]),
                        "platform": "generic",
                        "username": username,
                        "password": password,
                    },
                },
            )
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 10,
            },
        },
        inventory={
            "plugin": "DictInventory",
            "options": {
                "hosts": inventory["hosts"],
                "groups": {},
                "defaults": {},
            },
        },
        logging={"enabled": log_, "to_console": True, "level": "DEBUG"},
    )
    with open(test_file) as f:
        test_suite = yaml.safe_load(f.read())

    # add tests processor

    tests = nr.with_processors([TestsProcessor(test_suite)])

    spine_nr = tests.filter(filter_func=lambda h: "sw-spine" in h.name)
    leaf_nr = tests.filter(
        filter_func=lambda h: "sw-leaf" in h.name and "bmc" not in h.name,
    )
    leaf_bmc_nr = tests.filter(filter_func=lambda h: "sw-leaf-bmc" in h.name)
    cdu_nr = tests.filter(filter_func=lambda h: "sw-cdu" in h.name)

    # collect commands for devices
    spine_commands = []
    leaf_commands = []
    leaf_bmc_commands = []
    cdu_commands = []
    for item in test_suite:
        device = item.get("device")
        if "spine" in device and isinstance(item["task"], str):
            spine_commands.append(item["task"])
        elif isinstance(item["task"], list):
            spine_commands.extend(item["task"])
        if "leaf" in device and isinstance(item["task"], str):
            leaf_commands.append(item["task"])
        elif isinstance(item["task"], list):
            leaf_commands.extend(item["task"])
        if "leaf-bmc" in device and isinstance(item["task"], str):
            leaf_bmc_commands.append(item["task"])
        elif isinstance(item["task"], list):
            leaf_bmc_commands.extend(item["task"])
        if "cdu" in device and isinstance(item["task"], str):
            cdu_commands.append(item["task"])
        elif isinstance(item["task"], list):
            cdu_commands.extend(item["task"])

    # collect output from devices using netmiko_send_commands task plugin
    with click_spinner.spinner():
        print(
            "  Connecting...",
            end="\r",
        )
        spine_results = spine_nr.run(
            task=netmiko_send_commands,
            commands=spine_commands,
        )
        leaf_results = leaf_nr.run(task=netmiko_send_commands, commands=leaf_commands)
        leaf_bmc_results = leaf_bmc_nr.run(
            task=netmiko_send_commands,
            commands=leaf_bmc_commands,
        )
        cdu_results = cdu_nr.run(task=netmiko_send_commands, commands=cdu_commands)
    print(
        "                                                             ",
        end="\r",
    )
    # print out the results
    if json_:
        dict_results = ResultSerializer(spine_results, add_details=False, to_dict=True)
        dict_results.update(
            ResultSerializer(leaf_results, add_details=False, to_dict=True),
        )
        dict_results.update(
            ResultSerializer(spine_results, add_details=False, to_dict=True),
        )
        dict_results.update(
            ResultSerializer(leaf_bmc_results, add_details=False, to_dict=True),
        )
        dict_results.update(
            ResultSerializer(cdu_results, add_details=False, to_dict=True),
        )

        pprint.pprint(dict_results)
    else:
        spine = ResultSerializer(spine_results, add_details=True, to_dict=False)
        leaf = ResultSerializer(leaf_results, add_details=True, to_dict=False)
        leaf_bmc = ResultSerializer(leaf_bmc_results, add_details=True, to_dict=False)
        cdu = ResultSerializer(cdu_results, add_details=True, to_dict=False)
        print(
            TabulateFormatter(
                leaf + spine + leaf_bmc + cdu,
                tabulate="brief",
            ),
        )
