"""CANU commands that validate the shcd."""
import difflib

import click
from click_help_colors import HelpColorsCommand
import click_spinner
from hier_config import HConfig, Host
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

    command = "show running-config"
    config = netmiko_command(ip, credentials, command)

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
        running_config_hier,
        generated_config_hier,
    )

    click.echo("\n")
    click.secho(
        "Commands needed to get running config to match config file",
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
    one = []
    two = []
    for line in config1.all_children():
        one.append(line.cisco_style_text())
    for line in config2.all_children():
        two.append(line.cisco_style_text())
    d = difflib.Differ()
    additions = 0
    deletions = 0
    for diff in d.compare(one, two):
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
