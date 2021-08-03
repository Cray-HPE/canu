"""CANU commands that validate the shcd."""
from collections import defaultdict, OrderedDict
import difflib

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from hier_config import HConfig, Host
import natsort
from netmiko import ConnectHandler
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

    (
        switch_interfaces,
        switch_headers,
        switch_acl,
        switch_vlan,
        switch_vsx,
    ) = parse_interface(config.splitlines())
    switch_interfaces = sort_interfaces(switch_interfaces)

    (
        config_interfaces,
        config_headers,
        config_acl,
        config_vlan,
        config_vsx,
    ) = parse_interface(config_file_list)
    config_interfaces = sort_interfaces(config_interfaces)

    running_config_hier = HConfig(host=host)
    running_config_hier.load_from_string(config)

    # Build Hierarchical Configuration object for the Generated Config
    generated_config_hier = HConfig(host=host)
    generated_config_hier.load_from_file(config_file)

    # Build Hierarchical Configuration object for the Remediation Config
    remediation_config_hier = running_config_hier.config_to_get_to(
        generated_config_hier
    )

    dash = "-" * 60

    click.echo("\n")
    click.secho(
        "Config differences between running config and config file",
        fg="bright_white",
    )
    click.echo(dash)
    differences = compare_config(
        switch_headers + switch_acl + switch_vlan + switch_interfaces + switch_vsx,
        config_headers + config_acl + config_vlan + config_interfaces + config_vsx,
    )

    click.echo("\n")
    click.secho(
        "Comands needed to get running config to match config file",
        fg="bright_white",
    )
    click.echo(dash)
    for line in remediation_config_hier.all_children():
        click.echo(line.cisco_style_text())

    click.echo("\n")
    click.secho(
        "Differences",
        fg="bright_white",
    )
    click.echo(dash)
    click.secho(f"Total Deletions (-): {differences[0]}", fg="red")
    click.secho(f"Total Additions (+): {differences[1]}", fg="green")

    return


def netmiko_command(ip, credentials, command):
    """Send a command to a switch using netmiko.

    Args:
        ip: Switch ip
        credentials: Switch credentials
        command: Command to be run on the switch

    Returns:
        output: Text output from the command run.
    """
    with click_spinner.spinner():

        aruba1 = {
            "device_type": "aruba_os",
            "host": ip,
            "username": credentials["username"],
            "password": credentials["password"],
        }

        print(
            f"  Connecting to {ip}...",
            end="\r",
        )
        with ConnectHandler(**aruba1) as net_connect:
            output = net_connect.send_command(command)
            net_connect.disconnect()

    return output


def compare_config(config1, config2):
    """Compare and print two switch configurations.

    Args:
        config1: (Str) Switch 1 config
        config2: (Str) Switch 2 config

    Returns:
        List with thenumber of additions and deletions
    """
    d = difflib.Differ()
    additions = 0
    deletions = 0
    for diff in d.compare(config1, config2):
        color = ""
        if diff.startswith("- "):
            color = "red"
            deletions += 1
        elif diff.startswith("+ "):
            color = "green"
            additions += 1
        elif diff.startswith("? "):
            color = "blue"
        click.secho(diff, fg=color)

    return [additions, deletions]


def parse_interface(text):
    """Parse switch config text.

    Args:
        text: (Str) Switch config

    Returns:
        interfaces: Parsed interfaces
        headers: Parsed headers
        acl: Parsed acl
        vlan: Parsed vlan
        vsx: Parsed vsx
    """
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
        if x.startswith("interface"):
            if interface_name and len(interface) > 0:
                interfaces[interface_name] = interface
                interface = []
                interface_name = None
            interface.append(x)
            interface_name = x

        elif (
            len(interface) > 0
            and x.startswith("    ")
            and not acl_parse
            and not vsx_parse
            and not vlan_parse
        ):
            interface.append(x)

        elif x.startswith("access-list"):
            acl.append(x)
            acl_parse = True
            vlan_parse = False
            vsx_parse = False

        elif len(acl) > 0 and x.startswith("    ") and acl_parse:
            acl.append(x)

        elif x.startswith("vlan"):
            vlan.append(x)
            vlan_parse = True
            acl_parse = False
            vsx_parse = False

        elif len(vlan) > 0 and x.startswith("    ") and vlan_parse:
            vlan.append(x)

        elif x.startswith("vsx"):
            vsx.append(x)
            vsx_parse = True
            acl_parse = False
            vlan_parse = False

        elif len(vsx) > 0 and x.startswith("    ") and vsx_parse:
            vsx.append(x)

        else:
            if interface_name and len(interface) > 0:
                interfaces[interface_name] = interface
                interface = []
                interface_name = None
                if x != "" and x != "!":
                    headers.append(x)

            elif acl_parse:
                acl_parse = False
            elif vlan_parse:
                vlan_parse = False
            elif vsx_parse:
                vsx_parse = False
            else:
                if x != "" and x != "!":
                    headers.append(x)

    return interfaces, headers, acl, vlan, vsx


def sort_interfaces(interfaces):
    """Sort the interfaces in the switch config.

    Args:
        interfaces: Dictionary containing the parsed interfaces from the switch config

    Returns:
        A sorted list of interfaces in the switch config
    """
    sorted_interfaces = OrderedDict(natsort.natsorted(interfaces.items()))

    # Turn the sorted interface dict into a single list
    sorted_list = [line for x in sorted_interfaces for line in sorted_interfaces[x]]

    return sorted_list
