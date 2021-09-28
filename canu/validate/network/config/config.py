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
"""CANU commands that validate the network config."""
from collections import defaultdict
from glob import glob
import ipaddress
import json
from os import path
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from hier_config import HConfig, Host
from netmiko import ssh_exception
from ruamel.yaml import YAML

from canu.cache import cache_directory
from canu.validate.switch.config.config import (
    compare_config,
    get_switch_config,
    print_config_diff_summary,
)

yaml = YAML()


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

canu_cache_file = path.join(cache_directory(), "canu_cache.yaml")
canu_config_file = path.join(project_root, "canu", "canu.yaml")

# Get Shasta versions from canu.yaml
with open(canu_config_file, "r") as canu_f:
    canu_config = yaml.load(canu_f)

shasta_options = canu_config["shasta_versions"]

options_file = path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "options.yaml",
)
with open(options_file, "r") as options_f:
    options = yaml.load(options_f)

host = Host("example.rtr", "aoscx", options)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--shasta",
    "-s",
    type=click.Choice(shasta_options),
    help="Shasta network version",
    prompt="Shasta network version",
    required=True,
    show_choices=True,
)
@optgroup.group(
    "Running config input sources",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--ips",
    help="Comma separated list of IPv4 addresses of switches",
    type=Ipv4AddressListParamType(),
)
@optgroup.option(
    "--ips-file",
    help="File with one IPv4 address per line",
    type=click.File("r"),
)
@optgroup.option(
    "--running",
    help="Folder containing running config files",
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
    "generated_folder",
    help="Config file folder",
    required=True,
)
@click.option("--json", "json_", is_flag=True, help="Output JSON")
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.pass_context
def config(
    ctx,
    shasta,
    ips,
    ips_file,
    running,
    username,
    password,
    generated_folder,
    json_,
    out,
):
    """Validate network config.

    Compare the current running switch config with a generated switch config.
    The running config for the network can be read from multiple IP addresses
    using `--ips` or `--ips-file` or it can be read from a directory using `--running`.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        shasta: Shasta version
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        running: The running switch config file folder
        username: Switch username
        password: Switch password
        generated_folder: Generated config file folder
        json_: Bool indicating json output
        out: Name of the output file
    """
    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    config_data = []
    config_json = defaultdict()
    errors = []

    if ips:
        if not password:
            password = click.prompt(
                "Enter the switch password",
                type=str,
                hide_input=True,
            )

        credentials = {"username": username, "password": password}
        ips_length = len(ips)
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                if not json_:
                    print(
                        f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                        end="\r",
                    )
                try:
                    hostname, switch_config = get_switch_config(
                        ip,
                        credentials,
                        return_error=True,
                    )

                    # For versions of Shasta < 1.6, the hostname might need to be renamed
                    if shasta:
                        if float(shasta) < 1.6:
                            hostname = hostname.replace("-leaf-", "-leaf-bmc-")
                            hostname = hostname.replace("-agg-", "-leaf-")

                    running_config_hier = HConfig(host=host)
                    running_config_hier.load_from_string(switch_config)

                    # Build Hierarchical Configuration object for the Generated Config
                    generated_config_hier = HConfig(host=host)
                    generated_config_hier.load_from_file(
                        f"{generated_folder.rstrip('/')}/{hostname}.cfg",
                    )

                    differences = compare_config(
                        running_config_hier,
                        generated_config_hier,
                        print_comparison=False,
                        out=out,
                    )
                    if json_:
                        config_json[hostname] = differences

                    else:
                        config_data.append(
                            [
                                hostname,
                                ip,
                                differences,
                            ],
                        )
                except (
                    ssh_exception.NetmikoTimeoutException,
                    ssh_exception.NetmikoAuthenticationException,
                    Exception,
                ) as error:

                    exception_type = type(error).__name__
                    if exception_type == "NetmikoTimeoutException":
                        error_message = (
                            "Timeout error. Check the IP address and try again."
                        )
                    elif exception_type == "NetmikoAuthenticationException":
                        error_message = "Authentication error. Check the credentials or IP address and try again"
                    else:  # pragma: no cover
                        error_message = f"Error connecting to switch {ip}, {exception_type} {error}."

                    errors.append([str(ip), error_message])

    else:
        # Search directory for config files
        running_config_list = glob(f"{running.rstrip('/')}/*")
        for config_file in running_config_list:

            running_config_hier = HConfig(host=host)
            try:
                running_config_hier.load_from_file(config_file)

            except UnicodeDecodeError:
                errors.append(
                    [
                        str(config_file),
                        f"The file {config_file} is not a valid config file.",
                    ],
                )
                continue

            hostname = ""
            for line in running_config_hier.all_children():
                if line.cisco_style_text().startswith("hostname "):
                    hostname = line.cisco_style_text().split()[1]
                    break

            if hostname == "":
                errors.append(
                    [
                        str(config_file),
                        f"The file {config_file} is not a valid config file.",
                    ],
                )
                continue
            # For versions of Shasta < 1.6, the hostname might need to be renamed
            # If the hostname contains "-leaf-bmc-", set the version to 1.6 so nothing will be renamed
            if shasta:
                if float(shasta) < 1.6:
                    if "-leaf-bmc-" in hostname:
                        shasta = 1.6
                    else:
                        hostname = hostname.replace("-leaf-", "-leaf-bmc-")
                        hostname = hostname.replace("-agg-", "-leaf-")

            # Build Hierarchical Configuration object for the Generated Config
            generated_config_hier = HConfig(host=host)
            generated_config_file = f"{generated_folder.rstrip('/')}/{hostname}.cfg"
            try:
                generated_config_hier.load_from_file(generated_config_file)

            except FileNotFoundError:
                errors.append(
                    [
                        str(hostname),
                        f"Could not find generated config file {generated_config_file}",
                    ],
                )

            differences = compare_config(
                running_config_hier,
                generated_config_hier,
                print_comparison=False,
                out=out,
            )
            if json_:
                config_json[hostname] = differences

            else:
                config_data.append(
                    [
                        hostname,
                        None,
                        differences,
                    ],
                )

    if json_:
        # Add errors dict to config_json
        if len(errors) > 0:
            error_json = defaultdict()
            for error in errors:
                error_json[error[0]] = error[1]
            config_json["errors"] = error_json

        click.echo(json.dumps(config_json, indent=2), file=out)

    else:
        for switch in config_data:
            print_config_diff_summary(switch[0], switch[1], switch[2], out)

        dash = "-" * 100
        if len(errors) > 0:
            click.secho("\nErrors", fg="red", file=out)
            click.echo(dash, file=out)
            for error in errors:
                click.echo("{:<15s} - {}".format(error[0], error[1]), file=out)
