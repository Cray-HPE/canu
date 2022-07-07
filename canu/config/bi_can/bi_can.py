# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
"""CANU commands that configure bi-can."""
import ipaddress
import json

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_scrapli.tasks import send_commands, send_configs, send_config, send_command
from nornir_scrapli.functions import print_structured_result
from nornir_utils.plugins.functions import print_result
from nornir_salt.plugins.processors import DiffProcessor
from nornir_hier_config.plugins.tasks import remediation
from rich import print
from ttp import ttp
from deepdiff import DeepDiff
import dictdiffer
import re
import rich
from rich import inspect
import pysnooper
import logging

from canu.utils.host_alive import host_alive
from canu.utils.inventory import inventory
from canu.utils.sls import pull_sls_networks



@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--network",
    default="HMN",
    show_default=True,
    type=click.Choice(["HMN", "CMN"], case_sensitive=False),
    help="The network that is used to connect to the switches.",
)
@click.option(
    "--sls-file",
    help="File containing system SLS JSON data.",
    type=click.File("r"),
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
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
    is_flag=True,
    help="enable logging.",
    required=False,
)
@click.pass_context
#@pysnooper.snoop()
def bi_can(
    ctx,
    username,
    password,
    sls_file,
    sls_address,
    network,
    log_,
):
    if not password:
        password = click.prompt(
            "Enter the switch password",
            type=str,
            hide_input=True,
        )
    # set to ERROR otherwise nornir plugin logs debug messages to the screen.
    logging.basicConfig(level="ERROR")


    switch_inventory, sls_variables = inventory(username, password, network, sls_file, sls_inventory=True)

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
                f"WARNING: Could not reach {switch} via SSH",
                fg="red",
            )

    # jinja function to map switch name > IP
    def vlan_ip(sls_variables, host, network):
        for name, ip in sls_variables[network].items():
            if str(name) == str(host):
                return ip
    
    # Use scrapli to ssh to device and pull running config.
    def get_running_config(task):
        running_config = task.run(task=send_command, command="show running-config")
        task.host['running_config'] = running_config.result
        return Result(host=task.host, result = "running-configuration retrieved")
    
    def auto_confirm(task):
        task.run(task=send_command, command="auto-confirm")
        return Result(host=task.host, result = f"'auto-confirm' command ran on {task.host}")

    # Run the checkpoint command, this reverts the switch config to previous running config unless "checkpoint auto confirm" is ran
    def checkpoint_auto(task):
        result = task.run(task=send_command, command="checkpoint auto 1")
        print(f"Running 'checkpoint auto 1' on {task.host}")
        return Result(host = task.host, result = "checkpoint started, configuration will revert in 1 minutes unless 'checkpoint auto confirm' command is ran")

    def checkpoint_auto_confirm(task):
        checkpoint_result = task.run(task=send_command, command="checkpoint auto confirm")
        write_mem = task.run(task=send_command, command="write memory")
        print(f"Writing memory and confirming checkpoint on switch {task.host}")
        return Result(host = task.host, result = "checkpoint confirmed, switch configuration saved")

    # parse the running-config for ACL config and output to dictionary.
    def acl_parser(config):
        ttp_template = ("/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/acl.ttp")
        parser = ttp(data=config, template=ttp_template)
        parser.parse()
        parsed_response = parser.result()
        return parsed_response

    # parse the running-config for BGP config and output to dictionary.
    def bgp_parser(config):
        ttp_template = ("/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/bgp_aruba.ttp")
        parser = ttp(data=config, template=ttp_template)
        parser.parse()
        parsed_response = parser.result()
        return parsed_response

    # parse the running-config for vlan config and output to dictionary.
    def vlan_parser(config):
        ttp_template = ("/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/vlan.ttp")
        parser = ttp(data=config, template=ttp_template)
        parser.parse()
        parsed_response = parser.result()
        return parsed_response

    # generate CAN/CMN ACL
    def generate_acl_config(task):
        config = task.run(task=template_file,
                        template="acl.j2",
                        path="/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/",
                        variables=sls_variables,
                        hostname = str(task.host))
        task.host['acl_config'] = config.result
        return Result(host=task.host, result = "ACL config generated")

    # generate BGP config
    def generate_bgp_config(task):
        config = task.run(task=template_file,
                        template="bgp.j2",
                        path="/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/",
                        variables=sls_variables,
                        vlan_ip = vlan_ip,
                        hostname = str(task.host))
        task.host['bgp_gen_config'] = config.result
        return Result(host=task.host, result = "BGP configuration generated")

    # generate CAN/CMN vlan/interfaces
    def generate_vlan_config(task):
        config = task.run(task=template_file,
                        template="vlan.j2",
                        path="/Users/lucasbates/canu-container/canu/canu/config/bi_can/templates/",
                        variables=sls_variables,
                        vlan_ip = vlan_ip,
                        hostname = str(task.host))
        task.host['vlan_config'] = config.result
        return Result(host=task.host, result = "VLAN config generated")

    def configure_acl(task):
        task.run(task=generate_acl_config)
        task.run(task=auto_confirm)
        task.run(task=send_configs, configs=task.host["acl_config"].split("\n"))

    def configure_bgp(task):
        task.run(task=generate_bgp_config)
        task.run(task=auto_confirm)
        task.run(task=send_configs, configs=task.host["bgp_gen_config"].split("\n"))

    def configure_vlan(task):
        task.run(task=generate_vlan_config)
        task.run(task=auto_confirm)
        task.run(task=send_configs, configs=task.host["vlan_config"].split("\n"))

    def validate_acl_config(task):
        task.run(task=get_running_config)
        task.run(task=generate_acl_config)
        
        # parse for BGP configuration
        task.host["acl_gen"] = acl_parser(task.host["acl_config"])
        task.host["acl_run"] = acl_parser(task.host["running_config"])

        # run a diff on the generated BGP config vs running BGP config.
        task.host["acl_diff"] = DeepDiff(task.host["acl_run"], task.host["acl_gen"], ignore_order=True)
        return Result(host=task.host, result = "ACL config validated")

    def validate_bgp_config(task):
        task.run(task=get_running_config)
        task.run(task=generate_bgp_config)
        
        # parse for BGP configuration
        task.host["bgp_gen"] = bgp_parser(task.host["bgp_gen_config"])
        task.host["bgp_run"] = bgp_parser(task.host["running_config"])

        # run a diff on the generated BGP config vs running BGP config.
        diff = list(dictdiffer.diff(task.host["bgp_run"], task.host["bgp_gen"]))
        #ddiff = DeepDiff(task.host["bgp_run"], task.host["bgp_gen"], ignore_order=True)
        task.host["bgp_diff"] = diff
        return Result(host=task.host, result = "BGP config validated")

    def validate_vlan_config(task):
        task.run(task=get_running_config)
        task.run(task=generate_vlan_config)
        
        # parse for vlan interface config
        task.host["vlan_gen"] = vlan_parser(task.host["vlan_config"])
        task.host["vlan_run"] = vlan_parser(task.host["running_config"])
        # run a diff on the generated BGP config vs running BGP config.
        task.host["vlan_diff"] = DeepDiff(task.host["vlan_run"], task.host["vlan_gen"], ignore_order=True)
        return Result(host=task.host, result = "VLAN config validated")

    print(f"Setting checkpoint on switches, if we lose connection during configuration, the configs will be reverted to their current state.")
    checkpoint = online_hosts.run(task=checkpoint_auto)
    
    # configure ACLs
    results = online_hosts.run(task=validate_acl_config)
    for host, data in online_hosts.inventory.hosts.items():
        if data["acl_diff"]:
            switch = online_hosts.filter(filter_func=lambda h: host in h.name)
            print(f"ACL is incorrect on {host} re-running ACL configuration")
            switch.run(task=configure_acl)
            
            #re-run acl validate to check for diffs
            switch.run(task=validate_acl_config)
            if data["acl_diff"]:
                print(f"still diff in acl config on {host} after re-applying configuration")
            else:
                print(f"ACL config fixed on {host}")
        else:
            print(f"ACL config is correct on {host}")

    # configure vlans
    results = online_hosts.run(task=validate_vlan_config)
    for host, data in online_hosts.inventory.hosts.items():
        if data["vlan_diff"]:
            switch = online_hosts.filter(filter_func=lambda h: host in h.name)
            print(f"VLAN config is incorrect on {host} re-running VLAN configuration")
            switch.run(task=configure_vlan)
            switch.run(task=validate_vlan_config)
            if data["vlan_diff"]:
                print(f"still diff in VLAN config on {host} after re-applying configuration")
            else:
                print(f"VLAN config fixed on {host}")
                

        else:
            print(f"VLAN config is correct on {host}")

    # filter out spine switches
    nr_spine = online_hosts.filter(type="spine")
    # validate BGP config on spine switches
    nr_spine.run(task=validate_bgp_config)


            # if ("dictionary_item_removed") in data["bgp_diff"]:
            #     print(data["bgp_diff"])
            #     print(type(data["bgp_diff"]))
            #     for entry in data["bgp_diff"]["dictionary_item_removed"]:
            #         print(entry)
            #         print(type(entry))
            # # get incorrect route-maps
            # if ("dictionary_item_added") in data["bgp_diff"]:
            #     for entry in data["bgp_diff"]["dictionary_item_added"]:
            #         print(f"Config missing from {host} that's in generated")


    # configure BGP
    incorrect_route_maps = []

    # for host, data in nr_spine.inventory.hosts.items():
    #     print(data["bgp_diff"])
    #     print(data["bgp_diff"][0][2][0][0])
    #     for diff in data["bgp_diff"]:
    #         print(diff)

    #     if data["bgp_diff"]:
    #         print(data["bgp_diff"])
    #         route_map_str= str(data["bgp_diff"]['dictionary_item_removed'])
    #         print(route_map_str[26:-3])
    #         route_map = re.findall(r"^", route_map_str)
    #         string = route_map_str.startswith("[root[0][0]['route_map']['")
    #         print(string)

    for host, data in nr_spine.inventory.hosts.items():
        if data["bgp_diff"]:
            switch = nr_spine.filter(filter_func=lambda h: host in h.name)
            # print(data["bgp_run"][0][0])
            # print(data["bgp_diff"])
            #print(data["bgp_diff"]["dictionary_item_removed"])
            # get route-maps that need to be added
            #print(incorrect_route_maps)
            if "bgp_cfg" in data["bgp_run"][0][0]:
                bgp_asn = data["bgp_run"][0][0]["bgp_cfg"]["vrfs"]["default"]["asn"]
                print(f"BGP config found but not correct, removing config for router bgp {bgp_asn} and re-applying updated config")
                switch.run(task=send_command, command="auto-confirm")
                result = switch.run(task=send_config, config=f"no router bgp {bgp_asn}")
                switch.run(task=configure_bgp)
                switch.run(task=validate_bgp_config)
                if data["bgp_run"][0][0]:
                    print(f"BGP config updated successfully on {host}")
            else:
                print(f"No BGP config found on {host}")
                print(f"Applying BGP config on {host}")
                result = switch.run(task=configure_bgp)
                switch.run(task=validate_bgp_config)
                if data["bgp_run"][0][0]:
                    print(f"BGP config updated successfully on {host}")
        else:
            print(f"BGP config is correct on {host}")
    
    checkpoint_auto = online_hosts.run(task=checkpoint_auto_confirm)

    #inspect(online_hosts.config.inventory)

    # command_results = nr.run(task=send_command, command="show running-config bgp")

    #print(sls_variables)
    # print(print_structured_result(command_results, fail_to_string=True))
