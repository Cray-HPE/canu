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
import os
from pathlib import Path
import re
import requests
import socket
import sys
import urllib3

import click

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
# @pysnooper.snoop()
@click.command()
def ansible_inventory(
    list_,
    host_,
):
    """Generate a dynamic Ansible inventory

    Returns an inventory of switches from SLS or an sls_input_file.json
    from the current working directory.

    Note: $SLS_API_GW and $SLS_TOKEN must be set in order to query the API
    
    To find the CMN GW: kubectl -n istio-system get services istio-ingressgateway-cmn
    """

    sls_file = "./sls_input_file.json"
    password = os.getenv("SWITCH_PASSWORD")
    username = os.getenv("SWITCH_USERNAME")
    sls_address = os.getenv("SLS_API_GW")
    token = os.getenv("SLS_TOKEN")

    # if ansible is running on an NCN, use HMN
    if is_context_ncn():
        network = "HMN"
    # otherwise, use CMN
    else:
        network = "CMN"

    # use a local file if that exists
    if os.path.exists(sls_file):
        sls_file = click.open_file(sls_file, mode="r")
        try:
            with open(sls_file.name, 'r', encoding='utf-8') as f:
                sls_json = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho(
                f"The file {sls_file.name} is not valid JSON.",
                fg="red",
            )
            sys.exit(1)
        dump=None
    else:
        # SLS
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        sls_url = "https://" + sls_address + "/apis/sls/v1/dumpstate"
        try:
            api_req = requests.get(
                sls_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                verify=False,
            )
            api_req.raise_for_status()
            dump = api_req.json()
            sls_file=None

        except requests.exceptions.ConnectionError:
            return click.secho(
                f"Error connecting to SLS {sls_address}, check the address or pass in a new address using --sls-address.",
                fg="white",
                bg="red",
            )
        except requests.exceptions.HTTPError:
            bad_token_reason = (
                "environmental variable 'SLS_TOKEN' is correct."
            )
            return click.secho(
                f"Error connecting SLS {sls_address}, check that the {bad_token_reason}",
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

    # Get switch details
    if sls_file:
        nw = get_switch_nw_details(sls_json, network)
    else:
        nw = get_switch_nw_details(dump, network)
    # Get info from "Networks" key
    reservations = get_mn_reservations(nw, network)

    # if the --host is passed, return hostvars
    if host_:
        ansible_host(
                    inventory=switch_inventory, 
                    reservations=reservations, 
                    hostname=host_,
                    )

    # if --list is passed, return a full inventory
    if list_:
        ansible_list(
                    inventory=switch_inventory,
                    reservations=reservations,
                    )


# get_switch_nw_details returns the "Networks" key from an SLS dump
def get_switch_nw_details(networks, network):
    net = networks["Networks"].get(network)
    return net


# get_mn_reservations gets the management network data from SLS, which
# includes the IP of the device, which is set to ansible_host
# this allows for dynamicaly using ansible on the system or externally without
# issue
def get_mn_reservations(networks_key, net_name):
    # each network has multiple entries, we need a specific one to get the right
    # IP for access from outside the system
    if net_name == "CMN":
        full = "CMN Management Network Infrastructure"
    elif net_name == "HMN":
        full = "HMN Management Network Infrastructure"
    else:
        full = ""
    # if a key in the SLS data matches the name passed in
    if networks_key["Name"] == net_name:
      for net in networks_key["ExtraProperties"]["Subnets"]:
        # and the full name also matched
        if net["FullName"] == full:
          # return the reservations for that subnet
          
          return net["IPReservations"]

# is_context_ncn performs a stupid simple hostname regex to determine if this is
# running on an NCN.  If not, this returns false and assumes the CMN will be
# used.  Since there is no canonical way to determine a Shasta system--short of
# some large, messy checks--this will be put in place for now.
def is_context_ncn():
    host = socket.gethostname()
    hostReg = re.compile(r'(ncn|pit.*)-([s,w,m][0-9]{3})', re.VERBOSE)
    result = re.match(hostReg, host)
    if result:
      return True
    else:
      return False


# Produce json for ansible-inventory
def ansible_list(inventory=None, reservations=None, password=""):
    """Print entire inventory in JSON"""
    ansible_inventory = {}
    # _meta holds every host/group/vars and acts as a "cache" preventing
    # consecutive --host calls
    ansible_inventory["_meta"] = {"hostvars": {}}
    meta = ansible_inventory["_meta"]
    hvars = ansible_inventory["_meta"]["hostvars"]

    if "all" not in ansible_inventory:
        ansible_inventory["all"] = {"children": ["ungrouped"]}

    # add hosts and groups to the inventory
    for sw in inventory["options"]["hosts"]:
        # create a variable for the host being manipulated
        if sw not in hvars:
            hvars[sw] = {}

        # var for this hosts groups defined in SLS data
        groups = inventory["options"]["hosts"][sw]["groups"]
        
        # add a groups key to each host if it doesn't exist
        if "groups" not in hvars[sw]:
            hvars[sw]["groups"] = []

        # also append the existing groups from sls.py to the list
        for g in groups:
            if g not in ansible_inventory:
                ansible_inventory[g] = {"hosts": [], "vars": {}}
            
            # append the host to the group
            if sw not in ansible_inventory[g]["hosts"]:
              ansible_inventory[g]["hosts"].append(sw)
    
            if g not in hvars[sw]["groups"]:
                hvars[sw]["groups"].append(g)

            # add the group to the "all" group
            if g not in ansible_inventory["all"]["children"]:
                ansible_inventory["all"]["children"].append(g)
            # TODO: add group_vars

        # common info for ansible
        ansible_user = inventory["options"]["hosts"][sw]["username"]
        hvars[sw]["ansible_user"] = ansible_user
        
        ansible_password = inventory["options"]["hosts"][sw]["password"]
        hvars[sw]["ansible_password"] = ansible_password

        # the type of switch is a group name
        switch_type = inventory["options"]["hosts"][sw]["data"]["type"]

        # add it as a group name
        if switch_type not in ansible_inventory:
            ansible_inventory[switch_type] = {"hosts": [], "vars": {}}

        if switch_type not in hvars[sw]["groups"]:
            hvars[sw]["groups"].append(switch_type)

            # add the group to the "all" group
            if switch_type not in ansible_inventory["all"]["children"]:
                ansible_inventory["all"]["children"].append(switch_type)

        # append the host to the "hosts" key in the group
        if sw not in ansible_inventory[switch_type]["hosts"]:
            ansible_inventory[switch_type]["hosts"].append(sw)

        # aruba needs extra variables for ansible community module
        if "aruba" in groups:
            ansible_network_os = "arubanetworks.aoscx.aoscx"
            hvars[sw]["ansible_network_os"] = ansible_network_os

            # arubanetworks.aoscx.aoscx for API
            # network_cli for CLI/SSH
            # httpapi legacy
            # ansible_connection = "arubanetworks.aoscx.aoscx"
            ansible_connection = "arubanetworks.aoscx.aoscx"
            hvars[sw]["ansible_connection"] = ansible_connection

            # Only required for REST API modules) Must always be True as
            # AOS-CX uses port 443 for REST
            ansible_httpapi_use_ssl = True
            hvars[sw]["ansible_httpapi_use_ssl"] = ansible_httpapi_use_ssl

            # (Only required for REST API modules) Set True or False
            # depending on if Ansible should attempt to validate certificates
            ansible_httpapi_validate_certs = False
            hvars[sw]["ansible_httpapi_validate_certs"] = ansible_httpapi_validate_certs

            # Set to True or False depending if Ansible should bypass
            # environment proxies to connect to AOS-CX, required.
            ansible_acx_no_proxy = False
            hvars[sw]["ansible_acx_no_proxy"] = ansible_acx_no_proxy

            # Set to True or False depending if Ansible should bypass
            # validating certificates to connect to AOS-CX. Only required
            # when ansible_connection is set to arubanetworks.aoscx.aoscx
            ansible_aoscx_validate_certs = False
            hvars[sw]["ansible_aoscx_validate_certs"] = ansible_aoscx_validate_certs

            # Set to True or False depending if Ansible should bypass
            # environment proxies to connect to AOS-CX. Only required when
            # ansible_connection is set to arubanetworks.aoscx.aoscx.
            ansible_aoscx_use_proxy = False
            hvars[sw]["ansible_aoscx_use_proxy"] = ansible_aoscx_use_proxy

        # hostvars should also include IP for the ansible_host
        for res in reservations:
            if res["Name"] == sw:
                xn = res["Comment"]
                hvars[sw]["xname"] = xn

                ansible_host = res["IPAddress"]
                hvars[sw]["ansible_host"] = ansible_host
                continue

    # print the inventory
    click.echo(json.dumps(ansible_inventory, ensure_ascii=True))


# Produce json for ansible-inventory
def ansible_host(inventory=None, reservations=None, password="", hostname=None):
    """Print a specific host inventory in JSON"""
    ansible_inventory = {}

    # var for this hosts groups defined in SLS data
    groups = inventory["options"]["hosts"][hostname]["groups"]

    # common info for ansible
    ansible_user = inventory["options"]["hosts"][hostname]["username"]
    ansible_inventory.update({"ansible_user": ansible_user})
    
    ansible_password = inventory["options"]["hosts"][hostname]["password"]
    ansible_inventory.update({"ansible_password": ansible_password})

    ansible_host = inventory["options"]["hosts"][hostname]["hostname"]
    ansible_inventory.update({"ansible_host": ansible_host})

    # the type of switch is a group name
    switch_type = inventory["options"]["hosts"][hostname]["data"]["type"]

    # add it as a group name
    if switch_type not in inventory:
        ansible_inventory.update({"type": switch_type})
    
    # aruba needs extra variables for ansible community module
    if "aruba" in groups:
        ansible_network_os = "arubanetworks.aoscx.aoscx"
        ansible_inventory.update({"ansible_network_os": ansible_network_os})

        # arubanetworks.aoscx.aoscx for API
        # network_cli for CLI/SSH
        # httpapi legacy
        # ansible_connection = "arubanetworks.aoscx.aoscx"
        ansible_connection = "arubanetworks.aoscx.aoscx"
        ansible_inventory.update({"ansible_connection": ansible_connection})

        # Only required for REST API modules) Must always be True as
        # AOS-CX uses port 443 for REST
        ansible_httpapi_use_ssl = True
        ansible_inventory.update({"ansible_httpapi_use_ssl": ansible_httpapi_use_ssl})

        # (Only required for REST API modules) Set True or False
        # depending on if Ansible should attempt to validate certificates
        ansible_httpapi_validate_certs = False
        ansible_inventory.update({"ansible_httpapi_validate_certs": ansible_httpapi_validate_certs})

        # Set to True or False depending if Ansible should bypass
        # environment proxies to connect to AOS-CX, required.
        ansible_acx_no_proxy = False
        ansible_inventory.update({"ansible_acx_no_proxy": ansible_acx_no_proxy})

        # Set to True or False depending if Ansible should bypass
        # validating certificates to connect to AOS-CX. Only required
        # when ansible_connection is set to arubanetworks.aoscx.aoscx
        ansible_aoscx_validate_certs = False
        ansible_inventory.update({"ansible_aoscx_validate_certs": ansible_aoscx_validate_certs})

        # Set to True or False depending if Ansible should bypass
        # environment proxies to connect to AOS-CX. Only required when
        # ansible_connection is set to arubanetworks.aoscx.aoscx.
        ansible_aoscx_use_proxy = False
        ansible_inventory.update({"ansible_aoscx_use_proxy": ansible_aoscx_use_proxy})
            
    # print the inventory
    click.echo(json.dumps(ansible_inventory, indent=2))

if __name__ == '__main__':
    ansible_inventory()
