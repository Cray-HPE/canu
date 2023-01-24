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
"""Generates a dynamic Ansible inventory from SLS data."""
import json
import logging
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


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
# urllib3 shows stuff by default, which messes with clean output ansible needs
# so just display WARNINGS and above
logging.getLogger("urllib3").setLevel(logging.WARNING)


@click.option(
    "--debug",
    "debug_",
    help="Show debug output.",
    default=False,
    required=False,
    is_flag=True,
)
@click.option(
    "--examples",
    "examples_",
    help="Example commands to run.",
    required=False,
    is_flag=True,
)
@click.option(
    "--sls-file",
    "sls_file_",
    envvar="SLS_FILE",
    help="Path to a local SLS dumpstate file (or a path in the container).",
    default="./sls_input_file.json",
    show_default=True,
    required=False,
    show_envvar=True,
    type=click.Path(dir_okay=False, readable=True, allow_dash=True),
)
@click.option(
    "--sls-api-gw",
    "sls_address_",
    envvar="SLS_API_GW",
    help="The SLS API gateway address.",
    default="api-gw-service-nmn.local",
    show_default=True,
    required=False,
    show_envvar=True,
    type=click.STRING,
)
@click.option(
    "--sls-token",
    "sls_token_",
    envvar="SLS_TOKEN",
    help="The SLS API token.",
    required=False,
    show_envvar=True,
    hide_input=True,
    type=click.STRING,
)
@click.option(
    "--ca-path",
    "ca_path_",
    default=certifi.where(),
    envvar="REQUESTS_CA_BUNDLE",
    show_default=True,
    help="The path to the CA certificate to use for the SLS API (or a path in the container).",
    required=False,
    show_envvar=True,
    type=click.Path(dir_okay=False, readable=True),
)
@click.option(
    "--network",
    "network_",
    envvar="CANU_NET",
    help="The network plays should be executed over.",
    default="HMN",
    show_default=True,
    required=False,
    show_envvar=True,
    type=click.STRING,
)
@click.option(
    "--switch-username",
    "switch_username_",
    envvar="SWITCH_USERNAME",
    help="The username to use when connecting to switches.",
    default="admin",
    show_default=True,
    required=False,
    show_envvar=True,
    type=click.STRING,
)
@click.option(
    "--switch-password",
    "switch_password_",
    envvar="SWITCH_PASSWORD",
    help="The password to use when connecting to switches.",
    required=False,
    show_envvar=True,
    hide_input=True,
    type=click.STRING,
)
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
    debug_,
    examples_,
    sls_file_,
    switch_username_,
    switch_password_,
    sls_token_,
    sls_address_,
    ca_path_,
    network_,
    list_,
    host_,
):
    # noqa: DAR101, DAR201
    """Generate a dynamic Ansible inventory."""
    if examples_:
        examples()
        sys.exit(0)

    if debug_:
        logging.debug(f"Network: {network_}")

    if network_ == "HMN" and ca_path_ == "":
        # If running on an NCN, use the CA certificate from the NCN
        # The system python uses it by default, but the python in the venv does
        # not, nor does this binary version of canu{-inventory}
        ca_path_ = "/etc/pki/trust/anchors/platform-ca-certs.crt"

    # use a local file if that exists
    if os.path.exists(sls_file_):
        if sls_file_ is not None:
            if debug_:
                logging.debug(f"Using local file {sls_file_}")
            sls_file_ = click.open_file(sls_file_, mode="r")
            try:
                with open(sls_file_.name, "r", encoding="utf-8") as f:
                    sls_json = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                click.secho(
                    f"The file {sls_file_.name} is not valid JSON.",
                    fg="red",
                )
                sys.exit(1)
            dump = sls_json
    else:
        if debug_:
            logging.debug("Using API")
            logging.debug(f"CA: {ca_path_}")
            logging.debug(f"Using API at {sls_address_}")

        if sls_token_ is None:
            logging.debug("No SLS token provided. Please set the $SLS_TOKEN environment variable.")
            return click.secho(
                "No SLS token provided. Please set the $SLS_TOKEN environment variable.",
                fg="white",
                bg="red",
            )
        sls_url = "https://" + sls_address_ + "/apis/sls/v1/dumpstate"
        try:
            api_req = requests.get(
                sls_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {sls_token_}",
                },
                verify=ca_path_,
            )
            api_req.raise_for_status()
            dump = api_req.json()
            sls_file_ = None

        except requests.exceptions.ConnectionError as e:
            return click.secho(
                f"Error connecting to SLS at {sls_url}\n{e}",
                fg="white",
                bg="red",
            )
        except requests.exceptions.HTTPError as e:
            return click.secho(
                f"Error connecting SLS {sls_url}, check that the $SLS_API_GW and $SLS_TOKEN are correct.\n{e}",
                fg="white",
                bg="red",
            )
        except OSError as e:
            return click.secho(
                f"Could not find a suitable TLS CA certificate bundle\n{e}",
                fg="white",
                bg="red",
            )

    switch_inventory, _ = inventory(
        switch_username_,
        switch_password_,
        network_,
        sls_file=sls_file_,
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

    return ansible_inventory


def examples():
    # noqa: DAR101, DAR201
    """Print examples of using the script."""
    # noqa: D301
    click.secho(r"""
ENVIRONMENTAL VARIABLES AND VOLUME MOUNTS:

Required query the API:

  - $SLS_API_GW or --sls-api-gw (default: api-gw-service-nmn.local)
  - $SLS_TOKEN or --sls-token
  - $REQUESTS_CA_BUNDLE or --ca-path (default: /etc/pki/trust/anchors/platform-ca-certs.crt)

Required to query a local file:

  - $SLS_FILE or --sls-file (default: /home/canu/sls_input_file.json)

Optional (must be set in order to execute playbooks):

  - $SWITCH_USERNAME or --switch-username (default: admin)
  - $SWITCH_PASSWORD or --switch-password


IMPORTANT: sls_input_file.json and/or a CA bundle must be volume mounted into the container:

  - docker -v "${PWD}"/sls_input_file.json:/home/canu/sls_input_file.json ...
  - podman -v "${PWD}"/platform-ca-certs.crt:/etc/pki/trust/anchors/platform-ca-certs.crt ...

GATHERING ENVIRONMENTAL VARIABLE VALUES:

To find the gateway (use -cmn or -hmn to specify the network):

  - kubectl get svc -n istio-system istio-ingressgateway-xxx \
    -o=jsonpath='{range .items[*]}{.metadata.annotations.external-dns\.alpha\.kubernetes\.io\/hostname}{"\n"}' \
    | tr ',' '\n'


EXAMPLES:

Query the API (gateway, token, and a volume-mounted cert are required):

docker run \
  --entrypoint canu-inventory \
  -e SLS_API_GW=$SLS_API_GW \
  -e SLS_TOKEN=$SLS_TOKEN \
  -v "${PWD}"/platform-ca-certs.crt:/etc/pki/trust/anchors/platform-ca-certs.crt \
  cray-canu:x.x.x \
  --host sw-leaf-bmc-001


Query the API using canu-inventory flags instead of ENV vars:

docker run \
  --entrypoint canu-inventory \
  -v "${PWD}"/platform-ca-certs.crt:/etc/pki/trust/anchors/platform-ca-certs.crt \
  cray-canu:x.x.x \
  --sls-api-gw $SLS_API_GW \
  --sls-token $SLS_TOKEN \
  --network CMN \
  --list


Use a local SLS file (a local file volume mount is required):

docker run \                                                                                                         14:20
  --entrypoint canu-inventory \
  -v "${PWD}"/sls_input_file.json:/home/canu/sls_input_file.json \
  cray-canu:x.x.x --host sw-spine-001


""")


if __name__ == "__main__":
    ansible_inventory()
