"""CANU commands that validate the shcd."""
from collections import defaultdict, OrderedDict
import difflib

import click
from click_help_colors import HelpColorsCommand
from hier_config import HConfig, Host
import natsort
from netmiko import ConnectHandler
import requests
import yaml


options = yaml.safe_load(open("./canu/validate/config/options.yaml"))
host = Host("example.rtr", "aoscx", options)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option("--ip", required=True, help="The IP address of the switch")
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--config",
    "config_file",
    help="Config file",
)
# @click.option("--config", "config_file", help="Config file", type=click.File("r"))
@click.pass_context
def config(ctx, ip, username, password, config_file):
    """Validate switch config.

    Compare the current running switch config with a generated switch config.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        ip: The IP address of the switch
        username: Switch username
        password: Switch password
        config_file: Config file
    """
    credentials = {"username": username, "password": password}
    if config_file:
        with open(config_file, "r") as f:
            config_file_list = [line.strip("\n").replace("***===> ", "") for line in f]

    command = "show running-config"
    config = netmiko_command(ip, credentials, command)
    # print("config", config)

    (
        switch_interfaces,
        switch_headers,
        switch_acl,
        switch_vlan,
        switch_vsx,
    ) = parse_interface(config.splitlines())
    # (
    #     switch_interfaces,
    #     switch_headers,
    #     switch_acl,
    #     switch_vlan,
    #     switch_vsx,
    # ) = parse_interface(y.splitlines())
    switch_interfaces = sort_interfaces(switch_interfaces)

    (
        config_interfaces,
        config_headers,
        config_acl,
        config_vlan,
        config_vsx,
    ) = parse_interface(config_file_list)
    config_interfaces = sort_interfaces(config_interfaces)

    compare_config(
        switch_headers + switch_acl + switch_vlan + switch_interfaces + switch_vsx,
        config_headers + config_acl + config_vlan + config_interfaces + config_vsx,
    )

    running_config_hier = HConfig(host=host)
    running_config_hier.load_from_string(config)

    # Build Hierarchical Configuration object for the Generated Config
    generated_config_hier = HConfig(host=host)
    generated_config_hier.load_from_file(config_file)

    # Build Hierarchical Configuration object for the Remediation Config
    remediation_config_hier = running_config_hier.config_to_get_to(
        generated_config_hier
    )

    # print("======Config in generated config and not in running========")
    # in_generated = generated_config_hier.difference(running_config_hier)
    # for line in in_generated.all_children():
    #     print(line.cisco_style_text())

    # print("======Config in running config and not in generated========")
    # in_running = running_config_hier.difference(generated_config_hier)
    # for line in in_running.all_children():
    #     # print(line.cisco_style_text())
    #     print(line.cisco_style_text(style="merged"))

    # print()
    print("======Config needed to get running config to match generated========")
    for line in remediation_config_hier.all_children():
        # print(line.cisco_style_text(style="with_comments"))
        # print(line.cisco_style_text(style="merged"))
        print(line.cisco_style_text())

    # print(in_running.tags())

    return


def netmiko_command(ip, credentials, command):
    """Send a command to a switch using netmiko."""
    session = requests.Session()
    session.post(f"https://{ip}/rest/v10.04/login", data=credentials, verify=False)

    aruba1 = {
        "device_type": "aruba_osswitch",
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
    }

    click.secho(f"Connecting to {ip}...")
    with ConnectHandler(**aruba1) as net_connect:
        output = net_connect.send_command(command)
        # print(output)
        net_connect.disconnect()

    session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    return output


def compare_config(config1, config2):
    """Compare running and generated switch configurations."""
    d = difflib.Differ()
    for diff in d.compare(config1, config2):
        color = ""
        if diff.startswith("- "):
            color = "red"
        elif diff.startswith("+ "):
            color = "green"
        elif diff.startswith("? "):
            color = "blue"
        click.secho(diff, fg=color)

    return


def parse_interface(text):
    """Parse switch config text."""
    interface = []
    interface_name = None
    interfaces = defaultdict()
    headers = []
    acl = []
    acl_parse = False
    vlan = []
    vlan_parse = False
    vsx = []
    vsx_parse = False

    for x in text:
        # print("x", x)
        if x.startswith("interface"):
            # print("int elif1")
            if interface_name and len(interface) > 0:
                # print("**add previous to dict")
                interfaces[interface_name] = interface
                interface = []
                interface_name = None
            interface.append(x)
            # print("startswith", x)
            interface_name = x

        elif (
            len(interface) > 0
            and x.startswith("    ")
            and not acl_parse
            and not vsx_parse
            and not vlan_parse
        ):
            # print("int elif2")
            # print("next", x)
            # print("next", interface)
            interface.append(x)

        elif x.startswith("access-list"):
            # print("acl elif1")
            acl.append(x)
            acl_parse = True
            vlan_parse = False
            vsx_parse = False

        elif len(acl) > 0 and x.startswith("    ") and acl_parse:
            # print("acl elif2")
            acl.append(x)

        elif x.startswith("vlan"):
            # print("vlan elif1")
            vlan.append(x)
            vlan_parse = True
            acl_parse = False
            vsx_parse = False

        elif len(vlan) > 0 and x.startswith("    ") and vlan_parse:
            # print("vlan elif2")
            vlan.append(x)

        elif x.startswith("vsx"):
            # print("vsx elif1")
            vsx.append(x)
            vsx_parse = True
            acl_parse = False
            vlan_parse = False

        elif len(vsx) > 0 and x.startswith("    ") and vsx_parse:
            # print("vsx elif2")
            vsx.append(x)

        else:
            # print("else")
            # headers.append(x)
            if interface_name and len(interface) > 0:
                # print("else if")
                # print("else if interface_name", interface_name)
                interfaces[interface_name] = interface
                interface = []
                interface_name = None
                if x != "" and x != "!":
                    headers.append(x)

            elif acl_parse:
                # print("not acl_parsed")
                acl_parse = False
            elif vlan_parse:
                # print("not vlan_parsed")
                vlan_parse = False
            elif vsx_parse:
                # print("not vsx_parsed")
                vsx_parse = False
            else:
                # print("else else")
                if x != "" and x != "!":
                    # print("final else x", x)
                    headers.append(x)

    # print("interfaces", interfaces)
    # print("acl", acl)
    # print("*+*+*+*+vlan", vlan)
    # print("*+*+*+*+vsx", vsx)
    return interfaces, headers, acl, vlan, vsx


def sort_interfaces(interfaces):
    """Sort the interfaces in the switch config."""
    sorted_interfaces = OrderedDict(natsort.natsorted(interfaces.items()))

    # Turn the sorted interface dict into a single list
    sorted_list = [line for x in sorted_interfaces for line in sorted_interfaces[x]]
    print("\n********sorted_list", sorted_list)
    return sorted_list


# def cisco_style_text(
#     self, style: str = "without_comments", tag: Optional[str] = None
# ) -> str:
#     """ Return a Cisco style formated line i.e. indentation_level + text ! comments """

#     comments = []
#     if style == "without_comments":
#         pass
#     elif style == "merged":
#         # count the number of instances that have the tag
#         instance_count = 0
#         instance_comments: Set[str] = set()
#         for instance in self.instances:
#             if tag is None or tag in instance["tags"]:
#                 instance_count += 1
#                 instance_comments.update(instance["comments"])

#         # should the word 'instance' be plural?
#         word = "instance" if instance_count == 1 else "instances"

#         comments.append(f"{instance_count} {word}")
#         comments.extend(instance_comments)
#     elif style == "with_comments":
#         comments.extend(self.comments)

#     return f"{'  ' * (self.depth() - 1)}{self.text}{' !{}'.format(', '.join(sorted(comments))) if comments else ''}"
