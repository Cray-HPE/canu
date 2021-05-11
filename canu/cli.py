"""CANU (CSM Automatic Network Utility) floats through a new Shasta network and makes setup a breeze.

Currently CANU will identity firmware of Aruba switches on a Shasta network.
"""
import json
import os.path
import sys

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
import requests
import ruamel.yaml
import urllib3

from canu.network import network
from canu.switch import switch
from canu.validate import validate

yaml = ruamel.yaml.YAML()

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# To get the canu.yaml file
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    parent_directory = sys._MEIPASS
else:
    prog = __file__
    parent_directory = os.path.dirname(os.path.abspath(prog))

canu_config_file = os.path.join(parent_directory, "canu.yaml")


with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

CONTEXT_SETTING = dict(
    obj={
        "shasta": "",
        "config": canu_config,
    }
)


@click.group(
    context_settings=CONTEXT_SETTING,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--shasta",
    "-s",
    type=click.Choice(["1.4", "1.5"]),
    help="Shasta network version",
    required=True,
)
@click.option(
    "--cache",
    "cache_minutes",
    default=10,
    show_default=True,
    help="Max age in minutes of existing cache before making new API call.",
)
@click.version_option()
@click.pass_context
def cli(ctx, shasta, cache_minutes):
    """CANU (CSM Automatic Network Utility) floats through a new Shasta network and makes setup a breeze."""
    ctx.ensure_object(dict)

    ctx.obj["shasta"] = shasta
    ctx.obj["cache_minutes"] = cache_minutes


cli.add_command(switch.switch)
cli.add_command(network.network)
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
    "--out",
    required=True,
    help="Output file with CSI IP addresses",
    type=click.File("w"),
)
@click.pass_context
def init(ctx, csi_folder, auth_token, sls_address, out):
    """Initialize CANU by extracting all the switch IPs from yaml files in the CSI folder, or by getting IPs from SLS.

    To access SLS, a token must be passed in using the --auth-token flag.
    Tokens are typically stored in ~./config/cray/tokens/
    Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

    To initialize using CSI, pass in the CSI folder containing the sls_input_file.json file using the --csi-folder flag

    The sls_input_file.json file is generally stored in one of two places
    depending on how far the system is in the install process.


     - Early in the install process, when running off of the LiveCD the
     sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/config/SYSTEMNAME/`

     - Later in the install process, the sls_input_file.json file is
     generally in `/mnt/pitdata/prep/SYSTEMNAME/`

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        csi_folder: Directory containing the CSI json file
        auth_token: Token for SLS authentication
        sls_address: The address of SLS
        out: Name of the output file
    """
    switch_addresses = []

    # Parse sls_input_file.json file from CSI and filter "Node Management Network" IP addresses
    if csi_folder:
        try:
            with open(os.path.join(csi_folder, "sls_input_file.json"), "r") as f:
                input_json = json.load(f)

                # Format the input to be like the SLS JSON
                input_json_networks = [input_json["Networks"]["NMN"]]

                switch_addresses = parse_sls_json_for_ips(input_json_networks)

        except FileNotFoundError:
            click.secho(
                "The file sls_input_file.json was not found, check that this is the correct CSI directory.",
                fg="red",
            )
            return

    else:
        token = os.environ.get("SLS_TOKEN")

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
        url = "https://" + sls_address + "/apis/sls/v1/networks"
        try:
            response = requests.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=False,
            )
            response.raise_for_status()

            shasta_networks = response.json()

            switch_addresses = parse_sls_json_for_ips(shasta_networks)

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
        f"{len(switch_addresses)} IP addresses saved to {out.name}", fg="yellow"
    )


def parse_sls_json_for_ips(shasta):
    """Parse SLS JSON and return NMN IPv4 addresses.

    Args:
        shasta: The SLS JSON to be parsed.

    Returns:
        A list of switch IPs.
    """
    switch_addresses = []
    for sls_network in shasta:
        if sls_network["Name"] == "NMN":
            switch_addresses = [
                ip.get("IPAddress", None)
                for subnets in sls_network.get("ExtraProperties", {}).get("Subnets", {})
                for ip in subnets.get("IPReservations", {})
                # Only get the IP addresses if the name starts with "sw-"
                if ip.get("Name", "").startswith("sw-")
            ]

    return switch_addresses


if __name__ == "__main__":  # pragma: no cover
    cli()
