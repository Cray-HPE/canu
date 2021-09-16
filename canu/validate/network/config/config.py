"""CANU commands that validate the network config."""
import ipaddress
import os
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
from hier_config import HConfig, Host
from netmiko import ssh_exception
import ruamel.yaml

from canu.utils.ssh import netmiko_command
from canu.validate.switch.config.config import (
    compare_config,
    print_config_diff_summary,
)

yaml = ruamel.yaml.YAML()


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

canu_cache_file = os.path.join(project_root, "canu", "canu_cache.yaml")
canu_config_file = os.path.join(project_root, "canu", "canu.yaml")

# Get Shasta versions from canu.yaml
with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

shasta_options = canu_config["shasta_versions"]

options_file = os.path.join(
    project_root,
    "canu",
    "validate",
    "switch",
    "config",
    "options.yaml",
)
options = yaml.load(open(options_file))
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
    "Network cabling IPv4 input sources",
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
# @click.option("--ip", required=True, help="The IP address of the switch")
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option("--config", "config_folder", help="Config file folder", required=True)
@click.pass_context
def config(ctx, shasta, ips, ips_file, username, password, config_folder):
    """Validate switch config.

    Compare the current running switch config with a generated switch config.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        shasta: Shasta version
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        config_folder: Config file folder
    """
    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    config_data = []
    errors = []
    ips_length = len(ips)
    command = "show running-config"

    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    hostname = netmiko_command(str(ip), credentials, "sh run | i host")
                    hostname = hostname.split()[1]
                    config = netmiko_command(str(ip), credentials, command)

                    # For versions of Shasta < 1.6, the hostname might need to be renamed
                    if shasta:
                        if float(shasta) < 1.6:
                            hostname = hostname.replace("-leaf-", "-leaf-bmc-")
                            hostname = hostname.replace("-agg-", "-leaf-")

                    running_config_hier = HConfig(host=host)
                    running_config_hier.load_from_string(config)

                    # Build Hierarchical Configuration object for the Generated Config
                    generated_config_hier = HConfig(host=host)
                    generated_config_hier.load_from_file(
                        f"{config_folder}/{hostname}.cfg",
                    )

                    differences = compare_config(
                        running_config_hier,
                        generated_config_hier,
                        False,
                    )

                    config_data.append(
                        [
                            hostname,
                            ip,
                            differences,
                        ],
                    )

                except ssh_exception.NetmikoTimeoutException:
                    errors.append(
                        [
                            str(ip),
                            f"Timeout error connecting to switch {ip}, check the IP address and try again.",
                        ],
                    )
                except ssh_exception.NetmikoAuthenticationException:
                    errors.append(
                        [
                            str(ip),
                            f"Authentication error connecting to switch {ip}, check the credentials or IP address and try again.",
                        ],
                    )
                except Exception as err:  # pragma: no cover
                    exception_type = type(err).__name__
                    errors.append(
                        [
                            str(ip),
                            f"{exception_type} {err}",
                        ],
                    )

    for switch in config_data:
        print_config_diff_summary(switch[0], switch[1], switch[2])

    dash = "-" * 100
    if len(errors) > 0:
        click.echo("\n")
        click.secho("Errors", fg="red")
        click.echo(dash)
        for error in errors:
            click.echo("{:<15s} - {}".format(error[0], error[1]))

    return
