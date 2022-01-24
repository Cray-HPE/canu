# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""CANU commands that validate the shcd against the current network cabling."""
from collections import defaultdict, OrderedDict
import ipaddress
import logging
from os import path
from pathlib import Path
import re
import sys

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import natsort
from netmiko import ssh_exception
from network_modeling.NetworkNodeFactory import NetworkNodeFactory
import requests
from ruamel.yaml import YAML

from canu.report.switch.cabling.cabling import get_lldp
from canu.utils.cache import cache_directory
from canu.validate.network.cabling.cabling import node_model_from_canu
from canu.validate.shcd.shcd import (
    node_list_warnings,
    node_model_from_shcd,
    shcd_to_sheets,
)

yaml = YAML()

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent

# Schema and Data files
canu_cache_file = path.join(cache_directory(), "canu_cache.yaml")
canu_config_file = path.join(project_root, "canu", "canu.yaml")

# Get CSM versions from canu.yaml
with open(canu_config_file, "r") as canu_f:
    canu_config = yaml.load(canu_f)

csm_options = canu_config["csm_versions"]

log = logging.getLogger("validate_shcd")


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--csm",
    type=click.Choice(csm_options),
    help="CSM network version",
    prompt="CSM network version",
    required=True,
    show_choices=True,
)
@click.option(
    "--architecture",
    "-a",
    type=click.Choice(["Full", "TDS", "V1"], case_sensitive=False),
    help="CSM architecture",
    required=True,
    prompt="Architecture type",
)
@click.option(
    "--shcd",
    help="SHCD file",
    type=click.File("rb"),
    required=True,
)
@click.option(
    "--tabs",
    help="The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.",
)
@click.option(
    "--corners",
    help="The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.",
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
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--log",
    "log_",
    help="Level of logging.",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="ERROR",
)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.option(
    "--macs",
    help="Print NCN MAC addresses",
    is_flag=True,
)
@click.pass_context
def shcd_cabling(
    ctx,
    csm,
    architecture,
    shcd,
    tabs,
    corners,
    ips,
    ips_file,
    macs,
    username,
    password,
    log_,
    out,
):
    """Validate a SHCD file against the current network cabling.

    Pass in a SHCD file and a list of IP address to compair the connections.

    The output of the `validate shcd-cabling` command will show a port by port comparison between the devices found in the SHCD and devices found on the network.
    If there is a difference in what is found connected to a devices port in SHCD and Cabling, the line will be highlighted in 'red'.

    --------
    \f
    # noqa: D301, B950

    Args:
        ctx: CANU context settings
        csm: csm version
        architecture: CSM architecture
        shcd: SHCD file
        tabs: The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.
        corners: The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'.
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        macs: Print NCN MAC addresses
        username: Switch username
        password: Switch password
        log_: Level of logging.
        out: Name of the output file
    """
    logging.basicConfig(format="%(name)s - %(levelname)s: %(message)s", level=log_)

    if architecture.lower() == "full":
        architecture = "network_v2"
    elif architecture.lower() == "tds":
        architecture = "network_v2_tds"
    elif architecture.lower() == "v1":
        architecture = "network_v1"

    # SHCD Parsing
    try:
        sheets = shcd_to_sheets(shcd, tabs, corners)
    except Exception:
        return

    # IP Address / LLDP Parsing
    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}

    errors = []
    ips_length = len(ips)

    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    # Get LLDP info (stored in cache)
                    get_lldp(str(ip), credentials, return_error=True)

                except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RequestException,
                    ssh_exception.NetmikoTimeoutException,
                    ssh_exception.NetmikoAuthenticationException,
                ) as err:
                    exception_type = type(err).__name__

                    if exception_type == "HTTPError":
                        error_message = f"Error connecting to switch {ip}, check the IP, username, or password."
                    elif exception_type == "ConnectionError":
                        error_message = f"Error connecting to switch {ip}, check the IP address and try again."
                    elif exception_type == "NetmikoTimeoutException":
                        error_message = f"Timeout error connecting to {ip}. Check the IP address and try again."
                    elif exception_type == "NetmikoAuthenticationException":
                        error_message = f"Auth error connecting to {ip}. Check the credentials or IP address and try again"
                    else:
                        error_message = f"Error connecting to switch {ip}."

                    errors.append([str(ip), error_message])

    # Create SHCD Node factory
    shcd_factory = NetworkNodeFactory(architecture_version=architecture)

    shcd_node_list, shcd_warnings = node_model_from_shcd(
        factory=shcd_factory,
        spreadsheet=shcd,
        sheets=sheets,
    )

    # Create Cabling Node factory
    cabling_factory = NetworkNodeFactory(architecture_version=architecture)

    # Open the updated cache to model nodes
    with open(canu_cache_file, "r+") as file:
        canu_cache = yaml.load(file)

    cabling_node_list, cabling_warnings = node_model_from_canu(
        cabling_factory,
        canu_cache,
        ips,
    )

    # Combine the SHCD and Cabling nodes
    combined_nodes = combine_shcd_cabling(
        shcd_node_list,
        cabling_node_list,
        canu_cache,
        ips,
        csm,
    )

    # canu can be used to generate information needed prior to an install
    # such as the MAC addresses of the NCNs
    # create two lists to hold these values
    ncn_nodes = []
    ncn_macs = []
    # loop through the combined nodes
    for node, node_info in combined_nodes.items():
        # the MACs are readable from the leaf or spine switches
        if node is not None:
            if node.startswith("sw-leaf") or node.startswith("sw-spine"):
                for k, v in node_info.items():
                    # The MACs are stored in the "ports" key
                    if k == "ports":
                        # now the list of ncn_nodes is populated
                        ncn_nodes.append(v)

    # for each ncn in the list
    for ncn in ncn_nodes:
        for _k, v in ncn.items():
            # if the node starts with a ncn-, we need it's mac address
            if v["shcd"] is not None and v["shcd"].startswith("ncn"):
                if v["cabling"] is not None:
                    # check if there is a mac address in the data
                    if re.match(
                        "[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}",
                        v["cabling"].lower(),
                    ):
                        node_name = v["shcd"].split(":")[0]
                        node_mac = v["cabling"].split(" ")[0]
                        # append it to a list
                        ncn_macs.append((node_name, node_mac))

    if macs:
        click.secho("\n")
        for m in ncn_macs:
            host_mac_string = ",".join([str(i) for i in m])
            click.secho(f"{host_mac_string}")
        sys.exit(0)

    double_dash = "=" * 100
    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "SHCD vs Cabling",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)

    print_combined_nodes(combined_nodes, out)

    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "SHCD Warnings",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)
    node_list_warnings(shcd_node_list, shcd_warnings, out)

    click.echo("\n", file=out)
    click.echo(double_dash, file=out)
    click.secho(
        "Cabling Warnings",
        fg="bright_white",
        file=out,
    )
    click.echo(double_dash, file=out)
    node_list_warnings(cabling_node_list, cabling_warnings, out)

    if len(errors) > 0:
        click.echo("\n", file=out)
        click.echo(double_dash, file=out)
        click.secho(
            "Errors",
            fg="red",
            file=out,
        )
        click.echo(double_dash, file=out)
        for error in errors:
            click.echo(
                "{:<15s} - {}".format(error[0], error[1]),
                file=out,
            )


def node_list_to_dict(node_list):
    """Convert node list to a dict.

    TODO:  Move this to model serialization

    Args:
        node_list: A list of nodes

    Returns:
        node_dict: The nodes converted to a dict
    """
    node_dict = defaultdict()
    node_id_dict = defaultdict()

    for node in node_list:
        node_id_dict[node.id()] = node.common_name()

    node_tmp = [node.serialize() for node in node_list]

    for node in node_tmp:
        for port in node["ports"]:
            port["destination_node_name"] = node_id_dict[port["destination_node_id"]]
        node_dict[node["common_name"]] = node

    return node_dict


def combine_shcd_cabling(shcd_node_list, cabling_node_list, canu_cache, ips, csm):
    """Print comparison of the SHCD and network.

    Args:
        shcd_node_list: A list of shcd nodes
        cabling_node_list: A list of nodes found on the network
        canu_cache: CANU cache file
        ips: Comma separated list of IPv4 addresses of switches
        csm: csm version

    Returns:
        combined_nodes: dict of the combined shcd and cabling nodes
    """
    shcd_dict = node_list_to_dict(shcd_node_list)
    for x in shcd_dict:
        for y in shcd_dict[x]["ports"]:
            del y["destination_node_id"]
    cabling_dict = node_list_to_dict(cabling_node_list)
    for x in cabling_dict:
        for y in cabling_dict[x]["ports"]:
            del y["destination_node_id"]

    # Add nodes from SHCD to combined_nodes
    combined_nodes = defaultdict()
    for hostname, node_info in shcd_dict.items():
        port_dict = defaultdict()
        for shcd_node_port in node_info["ports"]:
            shcd_port_number = shcd_node_port["port"]
            shcd_hostname = shcd_node_port["destination_node_name"]
            shcd_slot = shcd_node_port["destination_slot"]
            shcd_port = shcd_node_port["destination_port"]

            shcd_destination_port_name = None
            if shcd_slot is None:
                shcd_destination_port_name = f"{shcd_hostname}:{shcd_port}"
            else:
                shcd_destination_port_name = f"{shcd_hostname}:{shcd_slot}:{shcd_port}"

            port_dict[shcd_port_number] = {
                "shcd": shcd_destination_port_name,
                "cabling": None,
            }

        shcd_node_dict = {
            "model": node_info["model"],
            "location": node_info["location"],
            "ports": port_dict,
        }
        combined_nodes[hostname] = shcd_node_dict

    # Add nodes from Cabling to combined_nodes
    for cabling_hostname, node_info in cabling_dict.items():
        # For versions of csm < 1.2, the hostname might need to be renamed
        if float(csm) < 1.2:
            cabling_hostname = cabling_hostname.replace("-leaf-", "-leaf-bmc-")
            cabling_hostname = cabling_hostname.replace("-agg-", "-leaf-")

        cabling_port_dict = defaultdict()
        for cabling_node_port in node_info["ports"]:
            cabling_port_number = cabling_node_port["port"]
            dest_hostname = cabling_node_port["destination_node_name"]
            dest_slot = cabling_node_port["destination_slot"]
            dest_port = cabling_node_port["destination_port"]

            # For versions of csm < 1.2, the hostname might need to be renamed
            if float(csm) < 1.2:
                dest_hostname = dest_hostname.replace("-leaf-", "-leaf-bmc-")
                dest_hostname = dest_hostname.replace("-agg-", "-leaf-")

            cabling_dest_port_name = None
            if dest_slot is None:
                cabling_dest_port_name = f"{dest_hostname}:{dest_port}"
            else:
                cabling_dest_port_name = f"{dest_hostname}:{dest_slot}:{dest_port}"

            cabling_port_dict[cabling_port_number] = {
                "cabling": cabling_dest_port_name,
                "shcd": None,
            }

        # Update port info in combined_nodes
        if cabling_hostname in combined_nodes.keys():
            for port_number, port_info in cabling_port_dict.items():
                cabling_ports = combined_nodes[cabling_hostname]["ports"]

                if port_number in cabling_ports.keys():
                    cabling_ports[port_number]["cabling"] = port_info["cabling"]
                else:
                    cabling_ports.update({port_number: port_info})
        else:
            cabling_node_dict = {
                "ports": cabling_port_dict,
            }
            combined_nodes[cabling_hostname] = cabling_node_dict

    # Add in MAC addresses from canu_cache
    for switch in canu_cache["switches"]:
        if ipaddress.ip_address(switch["ip_address"]) in ips:
            cache_hostname = switch["hostname"]
            if float(csm) < 1.2:
                cache_hostname = cache_hostname.replace("-leaf-", "-leaf-bmc-")
                cache_hostname = cache_hostname.replace("-agg-", "-leaf-")

            # Need the hostname is not in the cache, skip it
            if cache_hostname in combined_nodes.keys():
                combined_ports = combined_nodes[cache_hostname]["ports"].items()
                for port_number, port_info in combined_ports:

                    if port_info["cabling"] is None:
                        cache_port = switch["cabling"].get(
                            f"1/1/{port_number}",
                            [{"neighbor_port": None, "neighbor_description": ""}],
                        )

                        cache_description = f"{cache_port[0]['neighbor_port']} {cache_port[0]['neighbor_description']}"
                        port_info["cabling"] = cache_description

    # Order the ports in natural order
    combined_nodes = OrderedDict(natsort.natsorted(combined_nodes.items()))

    return combined_nodes


def print_combined_nodes(combined_nodes, out="-", input_type="SHCD"):
    """Print device comparison by port between SHCD and cabling.

    Args:
        combined_nodes: dict of the combined shcd and cabling nodes
        out: Defaults to stdout, but will print to the file name passed in
        input_type: String for the input to compair, typically SHCD or CCJ
    """
    dash = "-" * 80
    for node, node_info in combined_nodes.items():
        click.secho(f"\n{node}", fg="bright_white", file=out)
        if "location" in node_info.keys():
            rack = node_info.get("location").get("rack")
            elevation = node_info.get("location").get("elevation")

            click.secho(
                f"Rack: {rack:<7s}  Elevation: {elevation}",
                file=out,
            )
        click.secho(dash, file=out)
        click.secho(
            f"{'Port':<7s}{input_type:<25s}{'Cabling'}",
            fg="bright_white",
            file=out,
        )
        click.secho(dash, file=out)

        for port_number, port_info in node_info["ports"].items():
            text_color = "red"
            if port_info["shcd"] == port_info["cabling"]:
                text_color = None
            click.secho(
                f"{str(port_number):<7s}{str(port_info['shcd']):<25s}{str(port_info['cabling'])}",
                fg=text_color,
                file=out,
            )
