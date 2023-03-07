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
    help="Outputs commands to get from the running-config to generated config, Mellanox not supported",
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
    if vendor == "aruba":
        aruba_banner(generated_config_hier)
        aruba_banner(running_config_hier)
    unified_diff = list(running_config_hier.unified_diff(generated_config_hier))
    for line in unified_diff:
        if "+" == line.strip()[0]:
            click.secho(line, fg="green", file=out)
        elif "-" == line.strip()[0]:
            click.secho(line, fg="red", file=out)
        elif line.startswith("? "):
            pass
        else:
            click.secho(line, fg="bright_white", file=out)

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
    if vendor == "mellanox":
        click.secho(
            "Remediation not supported for Mellanox",
            fg="white",
            bg="red",
        )

    else:
        click.echo(dash, file=out)
        click.secho(
            "\n" + "Remediation Config" + "\n",
            fg="bright_white",
            file=out,
        )

        remediation_config_hier = running_config_hier.config_to_get_to(
            generated_config_hier,
        )
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
            switch_config_list = []
            # dell automagically appends whitespace to the banner.  Delete them.
            for line in command_output[0].splitlines():
                switch_config_list.append(line.rstrip())
            switch_config = ("\n").join(switch_config_list)
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
        banner_str = str(banner.cisco_style_text()) + "\n!"
        config.del_child(banner)
        config.add_child(banner_str)
        return config
