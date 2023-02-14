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
"""Generates a dynamic Ansible inventory from SLS data."""
import json
import os
from pathlib import Path
import re
import socket
import sys

import certifi
import click
import requests

from canu.utils.inventory import inventory

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent


@click.option(
    "--list",
    "list_",
    is_flag=True,
    help="Dynamic inventory for all hosts.",
    required=False,
)
@click.option(
    "--host",
    "host_",
    help="Dynamic inventory for a specific host.",
    required=False,
    type=click.STRING,
)
@click.command()
def ansible_inventory(
    list_,
    host_,
):
    r"""Generate a dynamic Ansible inventory.

    Print an inventory of switches from the SLS API or an sls_input_file.json in the current working directory.

    $SLS_API_GW and $SLS_TOKEN (or $TOKEN) must be set in order to query the API.

    $SWITCH_USERNAME and $SWITCH_PASSWORD must be set in order to execute playbooks.

    The CA certificate on an NCN will be used by default.
    If running from outside the cluster, the CA certificate can be set using $REQUESTS_CA_BUNDLE.

    To find the HMN or CMN gateway:

      kubectl get svc -n istio-system istio-ingressgateway-hmn \
        -o jsonpath='{.metadata.external-dns\.alpha\.kubernetes\.io\/hostname}'

      kubectl get svc -n istio-system istio-ingressgateway-cmn \
        -o jsonpath='{.metadata.external-dns\.alpha\.kubernetes\.io\/hostname}'

    Args:
        list_ : A full inventory of all hosts.
        host_ : A specific host to query.

    Returns:
        None
    """
    if is_context_ncn():
        network = "HMN"
        # If running on an NCN, use the CA certificate from the NCN
        # The system python uses it by default, but the python in the venv does
        # not, nor does this binary version of canu{-inventory}
        crt_path = "/etc/pki/trust/anchors/platform-ca-certs.crt"
    else:
        # If running off an NCN, use the CA certificate defined by the env var
        # defaultig to what certifi thinks is the right one
        crt_path = os.getenv("REQUESTS_CA_BUNDLE", certifi.where())
        network = "CMN"

    sls_file = "./sls_input_file.json"
    password = os.getenv("SWITCH_PASSWORD")
    username = os.getenv("SWITCH_USERNAME")
    sls_address = os.getenv("SLS_API_GW")

    # use a local file if that exists
    if os.path.exists(sls_file):
        sls_file = click.open_file(sls_file, mode="r")
        try:
            with open(sls_file.name, "r", encoding="utf-8") as f:
                sls_json = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho(
                f"The file {sls_file.name} is not valid JSON.",
                fg="red",
            )
            sys.exit(1)
        dump = sls_json
    else:
        # SLS
        if sls_address is None:
            # If the address is not set, use the default
            sls_address = "api-gw-service-nmn.local"
        # If a TOKEN var is already set, use that
        if os.getenv("TOKEN") is not None:
            token = os.getenv("TOKEN")
        else:
            # Otherwise, look for SLS_TOKEN
            token = os.getenv("SLS_TOKEN")
        sls_url = "https://" + sls_address + "/apis/sls/v1/dumpstate"
        try:
            api_req = requests.get(
                sls_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=crt_path,
            )
            api_req.raise_for_status()
            dump = api_req.json()
            sls_file = None

        except requests.exceptions.ConnectionError as e:
            return click.secho(
                f"Error connecting to SLS at {sls_url}\n{e}",
                fg="white",
                bg="red",
            )
        except requests.exceptions.HTTPError:
            bad_token_reason = "environmental variable 'SLS_TOKEN' is correct."
            return click.secho(
                f"Error connecting SLS {sls_url}, check that the $SLS_API_GW and $SLS_TOKEN are correct.\\nn{bad_token_reason}",
                fg="white",
                bg="red",
            )

    switch_inventory, _ = inventory(
        username,
        password,
        network,
        sls_file=sls_file,
        sls_inventory=True,
        dumpstate=dump,
    )

    # if the --host is passed, return hostvars
    if host_:
        ansible_host(
            datasource=switch_inventory,
            hostname=host_,
        )

    # if --list is passed, return a full inventory
    if list_:
        ansible_list(
            datasource=switch_inventory,
        )


# is_context_ncn performs a stupid simple hostname regex to determine if this is
# running on an NCN.  If not, this returns false and assumes the CMN will be
# used.  Since there is no canonical way to determine a Shasta system--short of
# some large, messy checks--this will be put in place for now.
def is_context_ncn():
    """Perform a simple hostname check to determine the running context.

    If this is running on an NCN, return True.  If not, return False.

    Args:
        None

    Returns:
        None
    """
    host = socket.gethostname()
    host_reg = re.compile(r"(ncn|pit.*)-([s,w,m][0-9]{3})", re.VERBOSE)
    result = re.match(host_reg, host)
    if result:
        return True
    else:
        return False


# Produce json for ansible-inventory
def ansible_list(datasource=None):
    """Print entire inventory in JSON.

    Args:
        datasource : Data from the datasource.
    """
    # create an empty inventory object
    ansible_inventory = {}

    # _meta holds every host/group/vars and acts as a "cache" preventing
    # consecutive --host calls
    ansible_inventory["_meta"] = {"hostvars": {}}

    # add the "all" group
    if "all" not in ansible_inventory:
        ansible_inventory["all"] = {"children": ["ungrouped"]}

    # add hosts and groups to the inventory
    for sw in datasource["options"]["hosts"]:
        # add the host to the _meta hostvars if it doesn't exist
        if sw not in ansible_inventory["_meta"]["hostvars"]:
            ansible_inventory["_meta"]["hostvars"][sw] = ansible_hostvars(
                datasource=datasource,
                hostname=sw,
            )

        # get the groups for the host
        groups = get_groups(datasource=datasource, hostname=sw)

        # add the groups to the inventory
        # this is a different structure than what might be in a host entry
        for group in groups["groups"]:
            # ansible groups cannot have dashes
            group = group.replace("-", "_")
            # add the group if it doesn't exist
            if group not in ansible_inventory:
                ansible_inventory.update({group: {"hosts": [], "vars": {}}})
            # add the host to the group if it doesn't exist
            if sw not in ansible_inventory[group]["hosts"]:
                ansible_inventory[group]["hosts"].append(sw)
            # TODO: add group_vars

    # print the inventory
    click.echo(json.dumps(ansible_inventory, indent=4, ensure_ascii=True))


def get_switch_user(datasource=None, hostname=None):
    """Get the switch username from the datasource.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        dict: The user defined in the datasource.
    """
    ansible_user = datasource["options"]["hosts"][hostname]["username"]
    return {"ansible_user": ansible_user}


def get_switch_pass(datasource=None, hostname=None):
    """Get the switch password from the datasource.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        The password defined in the datasource.
    """
    ansible_password = datasource["options"]["hosts"][hostname]["password"]
    return {"ansible_password": ansible_password}


def get_switch_ip(datasource=None, hostname=None):
    """Get the IP from the datasource and set ansible_host.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        The IP defined in the datasource.
    """
    ansible_host = datasource["options"]["hosts"][hostname]["hostname"]
    return {"ansible_host": ansible_host}


def get_groups(datasource=None, hostname=None):
    """Get groups from the datasource.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        The groups defined in the datasource and others defined by this script.
    """
    host_groups = []

    # var for this hosts groups defined in SLS data
    datasource_groups = datasource["options"]["hosts"][hostname]["groups"]
    for group in datasource_groups:
        if group not in host_groups:
            host_groups.append(group)

    # the type of switch is a group name
    datasource_type = datasource["options"]["hosts"][hostname]["data"]["type"]
    if datasource_type not in host_groups:
        host_groups.append(datasource_type)

    return {"groups": host_groups}


def get_aruba_vars(datasource=None, hostname=None):
    """Get extra variables needed by Aruba ansible modules.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        The ansible user defined in the datasource.
    """
    # aruba needs extra variables for ansible community module
    if "aruba" in datasource["options"]["hosts"][hostname]["groups"]:
        # arubanetworks.aoscx.aoscx for API
        # network_cli for CLI/SSH
        # httpapi legacy
        ansible_network_os = "arubanetworks.aoscx.aoscx"
        ansible_connection = "arubanetworks.aoscx.aoscx"

        # Only required for REST API modules) Must always be True as
        # AOS-CX uses port 443 for REST
        ansible_httpapi_use_ssl = True

        # (Only required for REST API modules) Set True or False
        # depending on if Ansible should attempt to validate certificates
        ansible_httpapi_validate_certs = False

        # Set to True or False depending if Ansible should bypass
        # environment proxies to connect to AOS-CX, required.
        ansible_acx_no_proxy = False

        # Set to True or False depending if Ansible should bypass
        # validating certificates to connect to AOS-CX. Only required
        # when ansible_connection is set to arubanetworks.aoscx.aoscx
        ansible_aoscx_validate_certs = False

        # Set to True or False depending if Ansible should bypass
        # environment proxies to connect to AOS-CX. Only required when
        # ansible_connection is set to arubanetworks.aoscx.aoscx.
        ansible_aoscx_use_proxy = False

        return [
            {"ansible_network_os": ansible_network_os},
            {"ansible_connection": ansible_connection},
            {"ansible_httpapi_use_ssl": ansible_httpapi_use_ssl},
            {"ansible_httpapi_validate_certs": ansible_httpapi_validate_certs},
            {"ansible_acx_no_proxy": ansible_acx_no_proxy},
            {"ansible_aoscx_validate_certs": ansible_aoscx_validate_certs},
            {"ansible_aoscx_use_proxy": ansible_aoscx_use_proxy},
        ]


def get_dellos10_vars(datasource=None, hostname=None):
    """Get extra variables needed by Aruba ansible modules.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        The ansible user defined in the datasource.
    """
    # aruba needs extra variables for ansible community module
    if "dell" in datasource["options"]["hosts"][hostname]["groups"]:
        # arubanetworks.aoscx.aoscx for API
        # network_cli for CLI/SSH
        # httpapi legacy
        ansible_network_os = "dellemc.os10.os10"
        ansible_connection = "network_cli"

        return [
            {"ansible_network_os": ansible_network_os},
            {"ansible_connection": ansible_connection},
            {"authorize": True},
        ]


def ansible_host(datasource=None, hostname=None):
    """Print a specific host inventory in JSON.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns: None
    """
    # create an empty inventory object
    ansible_inventory = {}
    # get the hostvars for the host
    ansible_inventory = ansible_hostvars(datasource=datasource, hostname=hostname)

    # print the inventory
    click.echo(json.dumps(ansible_inventory, indent=4, ensure_ascii=True))


def ansible_hostvars(datasource=None, hostname=None):
    """Aggregate various hostvars for a specific host.

    Args:
        datasource : Data from the datasource.
        hostname : The hostname to query.

    Returns:
        All the hostvars for the specified host.
    """
    # create an empty inventory object
    ansible_inventory = {}

    # get the hostvars for the host
    ansible_inventory.update(get_switch_ip(datasource, hostname))
    ansible_inventory.update(get_switch_user(datasource, hostname))
    ansible_inventory.update(get_switch_pass(datasource, hostname))
    ansible_inventory.update(get_groups(datasource, hostname))
    # add aruba vars if needed
    if "aruba" in ansible_inventory["groups"]:
        aruba_vars = get_aruba_vars(datasource, hostname)
        for var in aruba_vars:
            ansible_inventory.update(var)

    if "dell" in ansible_inventory["groups"]:
        dell_vars = get_dellos10_vars(datasource, hostname)
        for var in dell_vars:
            ansible_inventory.update(var)

    return ansible_inventory


if __name__ == "__main__":
    ansible_inventory()
