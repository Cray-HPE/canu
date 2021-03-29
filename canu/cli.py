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

yaml = ruamel.yaml.YAML()

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# To get the canu.yaml file in the parrent directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    parent_directory = sys._MEIPASS
else:
    prog = __file__
    current_directory = os.path.dirname(os.path.abspath(prog))
    parent_directory = os.path.split(current_directory)[0]

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
@click.version_option()
@click.pass_context
def cli(ctx, shasta):
    """CANU (CSM Automatic Network Utility) floats through a new Shasta network and makes setup a breeze."""
    ctx.ensure_object(dict)

    ctx.obj["shasta"] = shasta


cli.add_command(switch.switch)
cli.add_command(network.network)


@cli.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option("--csi-folder", help="Directory containing the CSI yaml files")
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

    To initialize using CSI, pass in the CSI folder containing the NMN.yaml file using the --csi-folder flag
    """
    switch_addresses = []

    # Parse NMN.yaml file from CSI and append them to a file with IPs
    if csi_folder:
        nmn_ips = parse_yaml_for_ips(csi_folder, "NMN.yaml")
        switch_addresses.extend(nmn_ips)
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

            for sls_network in shasta_networks:
                if sls_network["Name"] == "NMN":
                    switch_addresses = [
                        ip.get("IPAddress", None)
                        for subnets in sls_network.get("ExtraProperties", {}).get(
                            "Subnets", {}
                        )
                        for ip in subnets.get("IPReservations", {})
                        # Only get the IP addresses if the name starts with "sw-"
                        if ip.get("Name", "").startswith("sw-")
                        and "-cdu-" not in ip.get("Name", "")
                    ]

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


def parse_yaml_for_ips(folder, file):
    """Parse CSI YAML files and return IPv4 addresses.

    :param folder: The folder containing the YAML file to be parsed.

    :param file: The name of the YAML file to be parsed.

    :return: A list of switch IPs.
    """
    switch_ips = []

    try:
        with open(os.path.join(folder, file), "r") as f:
            f_yaml = yaml.load(f)

            for subnet in f_yaml["subnets"]:
                if subnet["full_name"] == "NMN Management Network Infrastructure":
                    switch_ips = [
                        ip.get("ip_address", None)
                        for ip in subnet.get("ip_reservations", {})
                        # Only get the IP addresses if the name starts with "sw-"
                        if ip.get("name", "").startswith("sw-")
                        and "-cdu-" not in ip.get("name", "")
                    ]

    except FileNotFoundError:
        click.secho(
            f"The file {file} was not found, check that this is the correct CSI directory.",
            fg="red",
        )
        return []

    return switch_ips


if __name__ == "__main__":  # pragma: no cover
    cli()
