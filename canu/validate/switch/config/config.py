"""CANU commands that validate switch running config against a config file."""
from collections import defaultdict
import difflib
import os
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from hier_config import HConfig, Host
import yaml

from canu.utils.ssh import netmiko_command


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

options_file = os.path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "options.yaml",
)
tags_file = os.path.join(
    project_root, "canu", "validate", "switch", "config", "tags.yaml"
)

tags = yaml.safe_load(open(tags_file))
options = yaml.safe_load(open(options_file))
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

    command = "show running-config"
    with click_spinner.spinner():
        print(
            f"  Connecting to {ip}...",
            end="\r",
        )
        config = netmiko_command(ip, credentials, command)
        hostname = netmiko_command(ip, credentials, "sh run | i host")
    print("                                                             ", end="\r")

    hostname = hostname.split()[1]

    running_config_hier = HConfig(host=host)
    running_config_hier.load_from_string(config)

    # Build Hierarchical Configuration object for the Generated Config
    generated_config_hier = HConfig(host=host)
    generated_config_hier.load_from_file(config_file)

    # Build Hierarchical Configuration object for the Remediation Config
    remediation_config_hier = running_config_hier.config_to_get_to(
        generated_config_hier,
    )

    remediation_config_hier.add_tags(tags)

    dash = "-" * 73

    click.echo("\n")
    click.secho(
        "Config differences between running config and config file",
        fg="bright_white",
    )

    differences = compare_config(
        running_config_hier.difference(generated_config_hier),
        generated_config_hier.difference(running_config_hier),
    )

    click.echo("\n")

    click.secho(
        "Safe Commands"
        "\n"
        "These commands should be safe to run while the system is running.",
        fg="green",
    )
    click.echo(dash)
    for line in remediation_config_hier.with_tags({"safe"}).all_children():
        click.echo(line.cisco_style_text())
    click.echo(dash)
    click.secho(
        "Manual Commands"
        "\n"
        "These commands may cause disruption to the system and should be done only during a maintenance period."
        "\n"
        "It is recommended to have an out of band connection while running these commands.",
        fg="red",
    )
    click.echo(dash)
    for line in remediation_config_hier.with_tags({"manual"}).all_children():
        click.echo(line.cisco_style_text())
    click.echo(dash)
    click.secho(
        "Commands NOT classified as Safe or Manual"
        "\n"
        "These commands include authentication as well as unique commands for the system."
        "\n"
        "These should be looked over carefully before keeping/applying.",
        fg="yellow",
    )
    click.echo(dash)
    for line in remediation_config_hier.all_children_sorted_untagged():
        click.echo(line.cisco_style_text())
    click.echo(dash)
    print_config_diff_summary(hostname, ip, differences)

    return


def print_config_diff_summary(hostname, ip, differences):
    """Print a summary of the config differences.

    Args:
        hostname: Switch hostname
        ip: Switch ip
        differences: Dict containing config differences.
    """
    dash = "-" * 73
    click.echo("\n")
    click.secho(
        f"Switch: {hostname} ({ip})",
        fg="bright_white",
    )
    click.secho(
        "Differences",
        fg="bright_white",
    )
    click.echo(dash)

    print_difference_line(
        "In Generated Not In Running (+)",
        "",
        "In Running Not In Generated (-)",
        "",
    )
    click.echo(dash)

    print_difference_line(
        "Total Additions:",
        differences["additions"],
        "Total Deletions: ",
        differences["deletions"],
    )
    print_difference_line(
        "Hostname:",
        differences["hostname_additions"],
        "Hostname: ",
        differences["hostname_deletions"],
    )
    print_difference_line(
        "Interface:",
        differences["interface_additions"],
        "Interface: ",
        differences["interface_deletions"],
    )
    print_difference_line(
        "Interface Lag:",
        differences["interface_lag_additions"],
        "Interface Lag: ",
        differences["interface_lag_deletions"],
    )
    print_difference_line(
        "Spanning Tree:",
        differences["spanning_tree_additions"],
        "Spanning Tree: ",
        differences["spanning_tree_deletions"],
    )
    print_difference_line(
        "Script:",
        differences["script_additions"],
        "Script: ",
        differences["script_deletions"],
    )
    print_difference_line(
        "Router:",
        differences["router_additions"],
        "Router: ",
        differences["router_deletions"],
    )
    print_difference_line(
        "System Mac:",
        differences["system_mac_additions"],
        "System Mac: ",
        differences["system_mac_deletions"],
    )
    print_difference_line(
        "Inter Switch Link:",
        differences["isl_additions"],
        "Inter Switch Link: ",
        differences["isl_deletions"],
    )
    print_difference_line(
        "Role:",
        differences["role_additions"],
        "Role: ",
        differences["role_deletions"],
    )
    print_difference_line(
        "Keepalive:",
        differences["keepalive_additions"],
        "Keepalive: ",
        differences["keepalive_deletions"],
    )


def print_difference_line(additions, additions_int, deletions, deletions_int):
    """Print the additions and deletions in red and green text. Doesn't print if zero.

    Args:
        additions: (str) Text of the additions
        additions_int: (int) Number of additions
        deletions: (str) Text of the deletions
        deletions_int: (int) Number of deletions
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
    )


def compare_config(config1, config2, print=True):
    """Compare and print two switch configurations.

    Args:
        config1: (Str) Switch 1 config
        config2: (Str) Switch 2 config
        print: Print the comparison to the screen (defaults True)

    Returns:
        List with the number of additions and deletions
    """
    one = []
    two = []

    config1.set_order_weight()
    config2.set_order_weight()

    for line in config1.all_children_sorted():
        one.append(line.cisco_style_text())
    for line in config2.all_children_sorted():
        two.append(line.cisco_style_text())
    d = difflib.Differ()
    differences = defaultdict(int)
    for diff in d.compare(one, two):
        color = ""
        if diff.startswith("- "):
            color = "red"
            differences["deletions"] += 1
        elif diff.startswith("+ "):
            color = "green"
            differences["additions"] += 1
        elif diff.startswith("? "):
            color = "blue"

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
        if print:
            click.secho(diff, fg=color)

    return differences
