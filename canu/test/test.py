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
"""CANU commands that test the network."""
import json
import logging
from os import path
from pathlib import Path
import sys

import click
from jinja2 import Environment
from nornir import InitNornir
from nornir.core.filter import F
from nornir_salt.plugins.functions import ResultSerializer, TabulateFormatter
from nornir_salt.plugins.processors import TestsProcessor
from nornir_salt.plugins.tasks import netmiko_send_commands, scrapli_send_commands
import yaml

from canu.style import Style
from canu.utils.host_alive import host_alive
from canu.utils.inventory import inventory
from canu.utils.json_load import load_json
from canu.utils.sls import sls_dump
from canu.utils.sls_utils.Managers import NetworkManager

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent

# Get CSM versions from canu.yaml
canu_config_file = path.join(project_root, "canu", "canu.yaml")
with open(canu_config_file, "r") as file:
    canu_config = yaml.safe_load(file)

csm_options = canu_config["csm_versions"]


@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--csm",
    default="1.4",
    type=click.Choice(csm_options),
    help="CSM version",
    required=False,
    show_choices=True,
)
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
    "--json",
    "json_",
    is_flag=True,
    help="JSON output.",
    required=False,
)
@click.option(
    "--ping",
    "ping",
    is_flag=True,
    help="Ping test from all mgmt switches to all NCNs.",
    required=False,
)
@click.option(
    "--pre-install",
    "pre_install_",
    is_flag=True,
    help="Tests to run before installing CSM",
    required=False,
)
@click.option(
    "--vrf",
    "vrf",
    help="Named VRF used for CSM networks",
    required=False,
    default="CSM",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.pass_context
def test(
    ctx,
    username,
    csm,
    password,
    sls_file,
    sls_address,
    network,
    log_,
    json_,
    ping,
    pre_install_,
    vrf,
):
    """Run tests against the network.

    Args:
        ctx: CANU context settings
        username: Switch username
        csm: CSM version
        password: Switch password
        sls_file: JSON file containing SLS data
        sls_address: The address of SLS
        network: The network that is used to connect to the switches.
        log_: enable logging
        json_: output test results in JSON format
        ping: run the ping test suite
        pre_install_: Tests to run before CSM installation
        vrf: Named VRF used for CSM networks
    """
    if not password:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )

    # set to ERROR otherwise nornir plugin logs debug messages to the screen.
    logging.basicConfig(level="ERROR")

    csm = float(csm)

    # Get project root directory
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
        project_root = sys._MEIPASS
    else:
        project_root = Path(__file__).resolve().parent.parent.parent

    def get_vlan_ips(network):
        network_dict = {}
        for net in network:
            for subnet in networks.get(net).subnets().values():
                for reservation in subnet.reservations().values():
                    if "ncn" in reservation.name() or "sw" in reservation.name():
                        net_key = net.lower()
                        vlan = subnet.vlan()
                        name = reservation.name() + f"-{net}".lower()
                        ipv4_address = str(reservation.ipv4_address())

                        if net_key not in network_dict:
                            network_dict[net_key] = {"vlan": vlan, "ips": []}
                        network_dict[net_key]["ips"].append(
                            {"name": name, "ipv4_address": ipv4_address},
                        )
        return network_dict

    def send_ssh_commands(vendor, commands, nornir_object):
        if vendor == "aruba":
            results = nornir_object.run(task=scrapli_send_commands, commands=commands)
        else:
            results = nornir_object.run(
                task=netmiko_send_commands,
                commands=commands,
                enable=True,
            )
        return results

    if sls_file:
        sls_json = load_json(file=sls_file)
    else:
        sls_json = sls_dump(path="dumpstate")

    networks = NetworkManager(sls_json["Networks"])

    vlan_ips = get_vlan_ips(["HMN", "CMN", "NMN"])

    switch_inventory, sls_variables = inventory(
        username,
        password,
        network,
        sls_file,
        sls_inventory=True,
    )
    sls_variables["CSM_VRF"] = vrf
    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 25,
            },
        },
        inventory=switch_inventory,
        logging={"enabled": log_, "to_console": True, "level": "DEBUG"},
    )
    # get the switch vendor name from the inventory
    # this is used to determine which tests to run
    platform = nr.filter(F(platform="aruba_aoscx"))
    if platform.inventory.hosts.keys():
        vendor = "aruba"
    else:
        vendor = "dellanox"

    online_hosts, unreachable_hosts = host_alive(nr)

    if unreachable_hosts:
        for switch in unreachable_hosts:
            click.secho(
                f"WARNING: Could not reach {switch} via SSH, skipping tests",
                fg="red",
            )

    if ping:
        ping = {
            "device": ["leaf", "leaf-bmc", "cdu", "spine"],
            "err_msg": "",
            "name": "",
            "pattern": "bytes from",
            "test": "contains",
        }

        ping_test = []

        # construct pings tests for switches
        for _net, net_data in vlan_ips.items():
            for data in net_data.get("ips", []):
                ip = data["ipv4_address"]
                name = data["name"]
                ping["err_msg"] = f"{name} is not reachable"
                ping["name"] = f"ping {name} {ip}"
                if vendor == "aruba":
                    if "cmn" in name:
                        ping["task"] = f"ping {ip} vrf Customer repetitions 1"
                    else:
                        ping["task"] = f"ping {ip} repetitions 1"
                elif vendor == "dellanox":
                    if "cmn" in name:
                        ping["task"] = f"ping vrf Customer {ip} -c 1"
                    else:
                        ping["task"] = f"ping {ip} -c 1"
                ping_test.append(ping.copy())

        nr_with_tests = online_hosts.with_processors([TestsProcessor(ping_test)])

        commands = []
        for item in ping_test:
            if isinstance(item["task"], str):
                commands.append(item["task"])
            elif isinstance(item["task"], list):
                commands.extend(item["task"])

        results = send_ssh_commands(vendor, commands, nr_with_tests)
        pretty_results = ResultSerializer(results, add_details=True, to_dict=False)
        dict_results = ResultSerializer(results, add_details=False, to_dict=True)
    else:
        test_file = path.join(
            project_root,
            "canu",
            "test",
            vendor,
            "test_suite.yaml",
        )

        with open(test_file) as f:
            test_suite = yaml.safe_load(f.read())
        switch_commands = {"spine": [], "leaf-bmc": [], "leaf": [], "cdu": []}
        switch_test_suite = {"spine": [], "leaf-bmc": [], "leaf": [], "cdu": []}

        dict_results = {}
        pretty_results = []
        # get the commands and the test suite for each switch type.
        environment = Environment(autoescape=True)
        for switch in switch_commands.keys():
            for test_command in test_suite:
                devices = test_command.get("device")
                csm_test_version = test_command.get("csm")
                test_type = test_command.get("test")
                pre_install = test_command.get("pre_install")

                if pre_install_ and pre_install is None:
                    continue

                if csm_test_version is not None and csm not in csm_test_version:
                    continue

                if switch in devices:
                    switch_test_suite[switch].append(test_command)

                if switch in devices and isinstance(test_command["name"], str):
                    template = environment.from_string(test_command["name"])
                    test_name = template.render(variables=sls_variables)
                    test_command["name"] = test_name

                if switch in devices and isinstance(test_command["task"], str):
                    template = environment.from_string(test_command["task"])
                    command = template.render(variables=sls_variables)
                    test_command["task"] = command
                    switch_commands[switch].append(test_command["task"])
                    if test_type == "custom":
                        custom_test = test_command.get("function_file")
                        test_path = path.join(
                            project_root,
                            "canu",
                            "test",
                            vendor,
                            custom_test,
                        )
                        # Update the dictionary entry
                        test_command["function_file"] = test_path
                        test_command["function_kwargs"] = {"vlan_ips": vlan_ips}

                elif switch in devices and isinstance(test_command["task"], list):
                    switch_commands.extend(test_command["task"])

        for switch in switch_commands.keys():
            if not json_:
                click.secho(f"Running tests on {switch} switches...", fg="green")
            # filter out each switch type
            switch_nr = online_hosts.filter(type=switch)
            # get the tests for each switch type
            test_nr = switch_nr.with_processors(
                [TestsProcessor(switch_test_suite[switch])],
            )

            commands = switch_commands[switch]
            results = send_ssh_commands(vendor, commands, test_nr)
            dict_results.update(
                ResultSerializer(results, add_details=False, to_dict=True),
            )

            pretty_results += ResultSerializer(results, add_details=True, to_dict=False)

        # print the results
    if json_:
        click.secho(json.dumps(dict_results, indent=4))
    else:
        print(
            TabulateFormatter(
                pretty_results,
                tabulate="brief",
            ),
        )
