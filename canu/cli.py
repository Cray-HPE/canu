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
"""CANU (CSM Automatic Network Utility) floats through a new Shasta network and makes setup a breeze."""
from collections import defaultdict
import json
from os import environ, path
import sys

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
import requests
import ruamel.yaml
import urllib3

from canu.cache import cache_switch
from canu.config import config
from canu.generate import generate
from canu.report import report
from canu.validate import validate

yaml = ruamel.yaml.YAML()

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# To get the canu.yaml file
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    parent_directory = sys._MEIPASS
else:
    parent_directory = path.abspath(path.dirname(path.dirname(__file__)))

canu_config_file = path.join(parent_directory, "canu", "canu.yaml")
canu_version_file = path.join(parent_directory, "canu", ".version")

with open(canu_version_file, "r") as version_file:
    version = version_file.read().replace("\n", "")

with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

CONTEXT_SETTING = {
    "obj": {
        "config": canu_config,
    },
}


@click.group(
    context_settings=CONTEXT_SETTING,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--cache",
    "cache_minutes",
    default=10,
    show_default=True,
    help="Max age in minutes of existing cache before making new API call.",
)
@click.version_option(version)
@click.pass_context
def cli(ctx, cache_minutes):
    """CANU (CSM Automatic Network Utility) floats through a new Shasta network and makes setup a breeze."""
    ctx.ensure_object(dict)

    ctx.obj["cache_minutes"] = cache_minutes


cli.add_command(config.config)
cli.add_command(generate.generate)
cli.add_command(report.report)
cli.add_command(validate.validate)


@cli.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option("--csi-folder", help="Directory containing the CSI json file")
@click.option(
    "--auth-token",
    envvar="SLS_TOKEN",
    help="Token for SLS authentication",
)
@click.option("--sls-address", default="api-gw-service-nmn.local", show_default=True)
@click.option(
    "--network",
    default="NMN",
    help="Switch network e.g. (CAN, MTL, NMN)",
    show_default=True,
)
@click.option(
    "--out",
    required=True,
    help="Output file with CSI IP addresses",
    type=click.File("w"),
)
@click.pass_context
def init(ctx, csi_folder, auth_token, sls_address, network, out):
    """Initialize CANU by extracting all the switch IPs from yaml files in the CSI folder, or by getting IPs from SLS.

    To access SLS, a token must be passed in using the --auth-token flag.
    Tokens are typically stored in ~./config/cray/tokens/
    Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

    To initialize using CSI, pass in the CSI folder containing the sls_input_file.json file using the --csi-folder flag

    The sls_input_file.json file is generally stored in one of two places
    depending on how far the system is in the install process.


     - Early in the install process, when running off of the LiveCD the
     sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

     - Later in the install process, the sls_input_file.json file is
     generally in `/mnt/pitdata/prep/SYSTEMNAME/`

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        csi_folder: Directory containing the CSI json file
        auth_token: Token for SLS authentication
        sls_address: The address of SLS
        network: Switch network e.g. (CAN, MTL, NMN).
        out: Name of the output file
    """
    switch_addresses = []

    # Parse sls_input_file.json file from CSI and filter "Node Management Network" IP addresses
    if csi_folder:
        try:
            with open(path.join(csi_folder, "sls_input_file.json"), "r") as f:
                input_json = json.load(f)

                # Format the input to be like the SLS JSON
                input_json_networks = [input_json["Networks"][network]]
                input_json_hardware = input_json.get("Hardware", {})

                switch_addresses, switch_dict = parse_sls_json_for_ips(
                    input_json_networks,
                    network,
                )
                parse_sls_json_for_vendor(input_json_hardware, switch_dict)

        except FileNotFoundError:
            click.secho(
                "The file sls_input_file.json was not found, check that this is the correct CSI directory.",
                fg="red",
            )
            return

    else:
        token = environ.get("SLS_TOKEN")

        # Token file takes precedence over the environmental variable
        if auth_token != token:
            try:
                with open(auth_token) as f:
                    data = json.load(f)
                    token = data["access_token"]

            except Exception:
                return click.secho(
                    "Invalid token file, generate another token or try again.",
                    fg="white",
                    bg="red",
                )

        # SLS
        networks_url = "https://" + sls_address + "/apis/sls/v1/networks"
        hardware_url = "https://" + sls_address + "/apis/sls/v1/hardware"
        try:
            # Networks
            networks_response = requests.get(
                networks_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=False,
            )
            networks_response.raise_for_status()
            shasta_networks = networks_response.json()
            switch_addresses, switch_dict = parse_sls_json_for_ips(
                shasta_networks,
                network,
            )

            # Hardware
            hardware_response = requests.get(
                hardware_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=False,
            )
            hardware_response.raise_for_status()
            shasta_hardware = hardware_response.json()
            parse_sls_json_for_vendor(shasta_hardware[0], switch_dict)

        except requests.exceptions.ConnectionError:
            return click.secho(
                f"Error connecting to SLS {sls_address}, check the address or pass in a new address using --sls-address.",
                fg="white",
                bg="red",
            )
        except requests.exceptions.HTTPError:
            bad_token_reason = (
                "environmental variable 'SLS_TOKEN' is correct."
                if auth_token == token
                else "token is valid, or generate a new one."
            )
            return click.secho(
                f"Error connecting SLS {sls_address}, check that the {bad_token_reason}",
                fg="white",
                bg="red",
            )

    # Put the IP addresses into a file
    for ip in switch_addresses:
        click.echo(ip, file=out)
    click.secho(
        f"{len(switch_addresses)} IP addresses saved to {out.name}",
        fg="yellow",
    )


def parse_sls_json_for_ips(shasta, network="NMN"):
    """Parse SLS JSON and return IPv4 addresses.

    Defaults to the "NMN" network, but another network can be passed in. Cache the switch IP and hostname.

    Args:
        shasta: The SLS JSON to be parsed.
        network: Switch network e.g. (CAN, MTL, NMN).

    Returns:
        switch_addresses: A list of switch IPs.
        switch_dict: Dictionary of IP addresses and hostnames

    """
    switch_addresses = []
    switch_dict = defaultdict()
    for sls_network in shasta:
        if sls_network["Name"] == network:
            for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {}):
                for ip in subnets.get("IPReservations", {}):
                    # Only get the IP addresses if the name starts with "sw-"
                    if ip.get("Name", "").startswith("sw-"):
                        ip_address = ip.get("IPAddress", None)
                        hostname = ip.get("Name", "")
                        switch_json = {
                            "ip_address": ip_address,
                            "hostname": hostname,
                        }
                        cache_switch(switch_json)
                        switch_addresses.append(ip_address)
                        switch_dict[hostname] = ip_address

    return switch_addresses, switch_dict


def parse_sls_json_for_vendor(shasta, switch_dict):
    """Parse SLS JSON for switch vendor and cache the results.

    Args:
        shasta: The SLS JSON to be parsed.
        switch_dict: Dictionary of IP addresses and hostnames
    """
    for device in shasta:
        alias_list = shasta[device].get("ExtraProperties", {}).get("Aliases", [])

        for alias in alias_list:
            if alias.startswith("sw-"):
                vendor = shasta[device]["ExtraProperties"].get("Brand", "").lower()
                hostname = alias

                switch_json = {
                    "ip_address": switch_dict[hostname],
                    "hostname": hostname,
                    "vendor": vendor,
                }
                cache_switch(switch_json)

    return


if __name__ == "__main__":  # pragma: no cover
    cli()
