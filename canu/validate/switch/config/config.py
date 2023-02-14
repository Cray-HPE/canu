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
"""CANU commands that validate switch running config against a config file."""
import difflib
from os import path
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS
import click_spinner
from hier_config import HConfig, Host
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
from ruamel.yaml import YAML

from canu.utils.ssh import netmiko_command, netmiko_commands
from canu.utils.vendor import switch_vendor

yaml = YAML()

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

options_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "aoscx_options.yaml",
)
dell_options_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "dellOS10_options.yaml",
)
mellanox_options_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "onyx_options.yaml",
)
tags_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "tags.yaml",
)

dell_tags_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "dell_tags.yaml",
)

mellanox_tags_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "mellanox_tags.yaml",
)

with open(tags_file, "r") as tags_f:
    tags = yaml.load(tags_f)

with open(dell_tags_file, "r") as tags_f:
    dell_tags = yaml.load(tags_f)

with open(mellanox_tags_file, "r") as tags_f:
    mellanox_tags = yaml.load(tags_f)

with open(options_file, "r") as options_f:
    options = yaml.load(options_f)

with open(dell_options_file, "r") as options_f:
    dell_options = yaml.load(options_f)

with open(mellanox_options_file, "r") as options_f:
    mellanox_options = yaml.load(options_f)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@optgroup.group(
    "Running config source",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--ip",
    help="The IP address of the switch with running config",
    type=IPV4_ADDRESS,
)
@optgroup.option(
    "--running",
    help="The running switch config file",
)
@click.option(
    "--vendor",
    type=click.Choice(["Aruba", "Dell", "Mellanox"], case_sensitive=False),
    help="The vendor is needed if passing in the running config from a file",
)
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--generated",
    "generated_config",
    help="Generated config file",
)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.option(
    "--remediation",
    is_flag=True,
    help="Outputs commands to get from the running-config to generated config",
    required=False,
)
@click.pass_context
def config(
    ctx,
    ip,
    running,
    username,
    password,
    generated_config,
    out,
    vendor,
    remediation,
):
    """Validate switch config.

    After config has been generated, CANU can validate the generated config against running switch config. The running config can be from either an IP address, or a config file.

    - To get running config from an IP address, use the flags '--ip 192.168.1.1 --username USERNAME --password PASSWORD'.

    - To get running config from a file, use the flag '--running RUNNING_CONFIG.cfg' instead.


    After running the 'validate switch config' command, you will be shown a line by line comparison of the currently running switch config against the config file that was passed in. You will also be given a list of remediation commands that can be typed into the switch to get the running config to match the config file. There will be a summary table at the end highlighting the most important differences between the configs.

    - Lines that are red and start with a '-' are in the running config, but not in the config file

    - Lines that are green and start with a '+' are not in the running config, but are in the config file

    - Lines that are blue and start with a '?' are attempting to point out specific line differences

    --------
    \f
    # noqa: D301, B950

    Args:
        ctx: CANU context settings
        ip: The IP address of the switch
        running: The running switch config file
        username: Switch username
        password: Switch password
        generated_config: Generated config file
        out: Name of the output file
        vendor: Switch vendor. Aruba, Dell, or Mellanox
        remediation: output remediation config
    """
    if ip:
        ip = str(ip)
        if not password:
            password = click.prompt(
                "Enter the switch password",
                type=str,
                hide_input=True,
            )

        credentials = {"username": username, "password": password}

        with click_spinner.spinner():
            print(
                f"  Connecting to {ip}...",
                end="\r",
            )
            hostname, switch_config, vendor = get_switch_config(ip, credentials)
        print(
            "                                                             ",
            end="\r",
        )
        if not hostname:
            click.secho(
                "There wan an error determining the vendor of the switch.",
                fg="white",
                bg="red",
            )
            return
        if vendor == "dell":
            host = Host("example.rtr", "dellOS10", dell_options)
        elif vendor == "mellanox":
            host = Host("example.rtr", "onyx", mellanox_options)
        elif vendor == "aruba":
            host = Host("example.rtr", "aoscx", options)
        running_config_hier = HConfig(host=host)
        running_config_hier.load_from_string(switch_config)
    else:
        if not vendor:
            vendor = click.prompt(
                "Please enter the vendor",
                type=click.Choice(["Aruba", "Dell", "Mellanox"], case_sensitive=False),
            )
        try:
            # Load config from file and parse hostname
            with open(running, "r") as f:
                running = f.read()
                vendor = vendor.lower()
                if vendor == "dell":
                    host = Host("example.rtr", "dellOS10", dell_options)
                elif vendor == "mellanox":
                    host = Host("example.rtr", "onyx", mellanox_options)
                    switch_config_list = []
                    for line in running.splitlines():
                        if line.startswith("   "):
                            switch_config_list.append(line.strip())
                        else:
                            switch_config_list.append(line)
                    running = ("\n").join(switch_config_list)
                elif vendor == "aruba":
                    host = Host("example.rtr", "aoscx", options)
                running_config_hier = HConfig(host=host)
                running_config_hier.load_from_string(running)
        except UnicodeDecodeError:
            click.secho(
                f"The file {running} is not a valid config file.",
                fg="white",
                bg="red",
            )
            return
        except FileNotFoundError:
            click.secho(
                f"The file {running} cannot be found",
                fg="red",
            )
            return

        hostname = ""
        for running_line in running_config_hier.all_children():
            if running_line.cisco_style_text().startswith("hostname "):
                hostname = running_line.cisco_style_text().split()[1]
                break

    # Build Hierarchical Configuration object for the Generated Config
    generated_config_hier = HConfig(host=host)
    generated_config_hier.load_from_file(generated_config)

    dash = "-" * 73
    compare_config_heir(
        running_config_hier.difference(generated_config_hier),
        generated_config_hier.difference(running_config_hier),
        vendor,
        out,
    )

    click.echo(dash, file=out)
    click.secho(
        "\n" + "Config differences between running config and generated config" + "\n",
        fg="bright_white",
        file=out,
    )
    click.secho(
        "\n"
        + 'lines that start with a minus "-" and RED: Config that is present in running config but not in generated config',
        fg="red",
        file=out,
    )
    click.secho(
        'lines that start with a plus "+" and GREEN: Config that is present in generated config but not in running config.'
        + "\n",
        fg="green",
        file=out,
    )

    # Build Hierarchical Configuration object for the Remediation Config
    if remediation:
        click.echo(dash, file=out)
        click.secho(
            "\n" + "Remediation Config" + "\n",
            fg="bright_white",
            file=out,
        )

        remediation_config_hier = running_config_hier.config_to_get_to(
            generated_config_hier,
        )

        if vendor == "aruba":
            aruba_banner(remediation_config_hier)
        for line in remediation_config_hier.all_children():
            click.echo(line.cisco_style_text(), file=out)


def get_switch_config(ip, credentials, return_error=False):
    """Get the running config of an Aruba, Dell, or Mellanox switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: Bool if the error should be printed or returned

    Returns:
        hostname: Switch hostname
        switch_config: Switch running config

    Raises:
        Exception: Netmiko exception
        NetmikoTimeoutException: Timeout error connecting to switch
        NetmikoAuthenticationException: Authentication error connecting to switch
    """
    try:
        vendor = switch_vendor(ip, credentials, return_error)

        if vendor is None:
            return None, None, None
        if vendor == "aruba":
            switch_config = netmiko_command(str(ip), credentials, "show running-config")
            hostname = netmiko_command(str(ip), credentials, "sh run | i host")
            hostname = hostname.split()[1]
        elif vendor == "dell":
            dell_commands = ["show running-configuration", "system hostname"]
            command_output = netmiko_commands(
                str(ip),
                credentials,
                dell_commands,
                "dell",
            )
            switch_config = command_output[0]
            hostname = command_output[1]
        elif vendor == "mellanox":
            mellanox_commands = [
                "show running-config expanded",
                "show hosts | include Hostname",
            ]
            command_output = netmiko_commands(
                str(ip),
                credentials,
                mellanox_commands,
                "mellanox",
            )

            switch_config_list = []
            for line in command_output[0].splitlines():
                if line.startswith("   "):
                    switch_config_list.append(line.strip())
                else:
                    switch_config_list.append(line)

            switch_config = ("\n").join(switch_config_list)
            hostname = command_output[1].split()[1]

    except (
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
        Exception,
    ) as error:
        if return_error:
            raise error

        exception_type = type(error).__name__
        if exception_type == "NetmikoTimeoutException":
            error_message = "Timeout error. Check the IP address and try again."
        elif exception_type == "NetmikoAuthenticationException":
            error_message = "Authentication error. Check the credentials or IP address and try again"
        else:  # pragma: no cover
            error_message = (
                f"Error connecting to switch {ip}, {exception_type} {error}."
            )

        click.secho(
            error_message,
            fg="white",
            bg="red",
        )
        return None, None, None

    return hostname, switch_config, vendor


def print_config_diff_summary(hostname, ip, differences, out):
    """Print a summary of the config differences.

    Args:
        hostname: Switch hostname
        ip: Switch ip
        differences: Dict containing config differences.
        out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 73
    click.echo("\n", file=out)
    if ip:
        title = f"Switch: {hostname} ({ip})"
    else:
        title = f"Switch: {hostname}"
    click.secho(
        title,
        fg="bright_white",
        file=out,
    )
    click.secho(
        "Differences",
        fg="bright_white",
        file=out,
    )
    click.echo(dash, file=out)

    print_difference_line(
        "In Generated Not In Running (+)",
        "",
        "In Running Not In Generated (-)",
        "",
        out,
    )
    click.echo(dash, file=out)
    # Always print total additions and deletions even if 0
    click.echo(
        "{:<40s}{:>12s}  |  {:<40s}{:>12s}".format(
            click.style("Total Additions:", fg="green"),
            click.style(str(differences["additions"]), fg="green"),
            click.style("Total Deletions: ", fg="red"),
            click.style(str(differences["deletions"]), fg="red"),
        ),
        file=out,
    )
    print_difference_line(
        "Hostname:",
        differences["hostname_additions"],
        "Hostname: ",
        differences["hostname_deletions"],
        out,
    )
    print_difference_line(
        "Interface:",
        differences["interface_additions"],
        "Interface: ",
        differences["interface_deletions"],
        out,
    )
    print_difference_line(
        "Interface Lag:",
        differences["interface_lag_additions"],
        "Interface Lag: ",
        differences["interface_lag_deletions"],
        out,
    )
    print_difference_line(
        "Spanning Tree:",
        differences["spanning_tree_additions"],
        "Spanning Tree: ",
        differences["spanning_tree_deletions"],
        out,
    )
    print_difference_line(
        "Script:",
        differences["script_additions"],
        "Script: ",
        differences["script_deletions"],
        out,
    )
    print_difference_line(
        "Router:",
        differences["router_additions"],
        "Router: ",
        differences["router_deletions"],
        out,
    )
    print_difference_line(
        "System Mac:",
        differences["system_mac_additions"],
        "System Mac: ",
        differences["system_mac_deletions"],
        out,
    )
    print_difference_line(
        "Inter Switch Link:",
        differences["isl_additions"],
        "Inter Switch Link: ",
        differences["isl_deletions"],
        out,
    )
    print_difference_line(
        "Role:",
        differences["role_additions"],
        "Role: ",
        differences["role_deletions"],
        out,
    )
    print_difference_line(
        "Keepalive:",
        differences["keepalive_additions"],
        "Keepalive: ",
        differences["keepalive_deletions"],
        out,
    )


def print_difference_line(additions, additions_int, deletions, deletions_int, out):
    """Print the additions and deletions in red and green text. Doesn't print if zero.

    Args:
        additions: (str) Text of the additions
        additions_int: (int) Number of additions
        deletions: (str) Text of the deletions
        deletions_int: (int) Number of deletions
        out: Defaults to stdout, but will print to the file name passed in
    """
    if additions_int == 0 and deletions_int == 0:
        return
    if additions_int == 0:
        additions = ""
        additions_int = ""
    if deletions_int == 0:
        deletions = ""
        deletions_int = ""
    additions = click.style(str(additions), fg="green")
    additions_int = click.style(str(additions_int), fg="green")
    deletions = click.style(str(deletions), fg="red")
    deletions_int = click.style(str(deletions_int), fg="red")
    click.echo(
        "{:<40s}{:>12s}  |  {:<40s}{:>12s}".format(
            additions,
            additions_int,
            deletions,
            deletions_int,
        ),
        file=out,
    )


def aruba_banner(config):
    """Hier config removes the ! from the end of the Aruba banner, this function adds it back.

    Args:
        config: hier config object

    Returns:
        corrected banner
    """
    banner = config.get_child("contains", "banner")
    if banner is None:
        return
    else:
        banner_str = str(banner) + "\n!"
        config.del_child(banner)
        config.add_child(banner_str)
        return config


def compare_config_heir(config1, config2, vendor, out="-"):
    """Compare and print two switch configurations.

    Args:
        config1: (Str) Switch 1 config
        config2: (Str) Switch 2 config
        vendor: Switch vendor. Aruba, Dell, or Mellanox
        out: Defaults to stdout, but will print to the file name passed in

    Returns:
        List with the number of additions and deletions
    """
    one = []
    two = []

    config1.set_order_weight()
    config2.set_order_weight()

    # fix aruba banner
    if vendor == "aruba":
        aruba_banner(config1)
        aruba_banner(config2)
    for config1_line in config1.all_children_sorted():
        one.append(config1_line.cisco_style_text())
    for config2_line in config2.all_children_sorted():
        two.append(config2_line.cisco_style_text())
    d = difflib.Differ()
    difflist = []

    for line in d.compare(one, two):
        difflist.append(line)
    if vendor == "mellanox":
        difflist.sort(reverse=True)
    for line in difflist:
        if "+" == line.strip()[0]:
            click.secho(line, fg="green", file=out)
        elif "-" == line.strip()[0]:
            click.secho(line, fg="red", file=out)
        elif line.startswith("? "):
            pass
        else:
            click.secho(line, fg="bright_white", file=out)
    return difflist


def compare_config(config1, config2, print_comparison=True, out="-"):
    """Compare and print two switch configurations.

    Args:
        config1: (Str) Switch 1 config
        config2: (Str) Switch 2 config
        print_comparison: Print the comparison to the screen (defaults True)
        out: Defaults to stdout, but will print to the file name passed in

    Returns:
        List with the number of additions and deletions
    """
    one = []
    two = []

    config1.set_order_weight()
    config2.set_order_weight()

    for config1_line in config1.all_children_sorted():
        one.append(config1_line.cisco_style_text())
    for config2_line in config2.all_children_sorted():
        two.append(config2_line.cisco_style_text())
    d = difflib.Differ()
    differences = {
        "additions": 0,
        "deletions": 0,
        "hostname_additions": 0,
        "hostname_deletions": 0,
        "interface_additions": 0,
        "interface_deletions": 0,
        "interface_lag_additions": 0,
        "interface_lag_deletions": 0,
        "spanning_tree_additions": 0,
        "spanning_tree_deletions": 0,
        "script_additions": 0,
        "script_deletions": 0,
        "router_additions": 0,
        "router_deletions": 0,
        "system_mac_additions": 0,
        "system_mac_deletions": 0,
        "isl_additions": 0,
        "isl_deletions": 0,
        "role_additions": 0,
        "role_deletions": 0,
        "keepalive_additions": 0,
        "keepalive_deletions": 0,
    }
    for diff in d.compare(one, two):
        color = ""
        if diff.startswith("- "):
            color = "red"
            differences["deletions"] += 1
        elif diff.startswith("+ "):
            color = "green"
            differences["additions"] += 1

        if diff.startswith("+ hostname"):
            differences["hostname_additions"] += 1
        if diff.startswith("- hostname"):
            differences["hostname_deletions"] += 1
        if diff.startswith("+ interface 1/1/"):
            differences["interface_additions"] += 1
        if diff.startswith("- interface 1/1/"):
            differences["interface_deletions"] += 1
        if diff.startswith("+ interface lag"):
            differences["interface_lag_additions"] += 1
        if diff.startswith("- interface lag"):
            differences["interface_lag_deletions"] += 1
        if diff.startswith("+ spanning-tree"):
            differences["spanning_tree_additions"] += 1
        if diff.startswith("- spanning-tree"):
            differences["spanning_tree_deletions"] += 1
        if diff.startswith("+ nae-script"):
            differences["script_additions"] += 1
        if diff.startswith("- nae-script"):
            differences["script_deletions"] += 1
        if diff.startswith("+ router"):
            differences["router_additions"] += 1
        if diff.startswith("- router"):
            differences["router_deletions"] += 1
        if diff.startswith("+   system-mac"):
            differences["system_mac_additions"] += 1
        if diff.startswith("-   system-mac"):
            differences["system_mac_deletions"] += 1
        if diff.startswith("+   inter-switch-link"):
            differences["isl_additions"] += 1
        if diff.startswith("-   inter-switch-link"):
            differences["isl_deletions"] += 1
        if diff.startswith("+   role"):
            differences["role_additions"] += 1
        if diff.startswith("-   role"):
            differences["role_deletions"] += 1
        if diff.startswith("+   keepalive"):
            differences["keepalive_additions"] += 1
        if diff.startswith("-   keepalive"):
            differences["keepalive_deletions"] += 1

        # Print the difference
        if print_comparison:
            click.secho(diff, fg=color, file=out)

    return differences
