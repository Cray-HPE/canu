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
"""Create Nornir Inventory from SLS."""
import json

import click

from canu.utils.sls import pull_sls_hardware, pull_sls_networks


def inventory(username, password, network, sls_json=None, sls_inventory=None):
    """Build Nornir inventory from sls_input."""
    inventory = {"groups": {}, "hosts": {}}
    if sls_json:
        try:
            input_json = json.load(sls_json)
        except (json.JSONDecodeError, UnicodeDecodeError):
            click.secho(
                f"The file {sls_json.name} is not valid JSON.",
                fg="red",
            )
            return
        sls_variables = pull_sls_networks(input_json)
        sls_hardware = pull_sls_hardware(input_json)
    else:
        sls_variables = pull_sls_networks()
        sls_hardware = pull_sls_hardware()

    for k in sls_variables[network + "_IPs"]:
        if "sw" in k:
            inventory["hosts"].update(
                {
                    k: {
                        "hostname": str(sls_variables[network + "_IPs"][k]),
                        "username": username,
                        "password": password,
                        "data": {"type": ""},
                    },
                },
            )
    # pull in the platform type from sls hardware data
    for x in sls_hardware:
        if (
            x["Type"] == "comptype_hl_switch"
            or x["Type"] == "comptype_mgmt_switch"
            or x["Type"] == "comptype_cdu_mgmt_switch"
        ):
            for host in inventory["hosts"]:
                if host == x["ExtraProperties"]["Aliases"][0]:
                    if x["ExtraProperties"]["Brand"] == "Aruba":
                        inventory["hosts"][host]["groups"] = ["aruba"]
                    elif x["ExtraProperties"]["Brand"] == "Dell":
                        inventory["hosts"][host]["groups"] = "dell"
                    elif x["ExtraProperties"]["Brand"] == "Mellanox":
                        inventory["hosts"][host]["groups"] = "mellanox"
                    else:
                        inventory["hosts"][host]["platform"] = "generic"
                if "sw-leaf-bmc" in host:
                    inventory["hosts"][host]["data"]["type"] = "leaf-bmc"
                elif "sw-leaf" in host:
                    inventory["hosts"][host]["data"]["type"] = "leaf"
                elif "sw-spine" in host:
                    inventory["hosts"][host]["data"]["type"] = "spine"
                elif "sw-cdu" in host:
                    inventory["hosts"][host]["data"]["type"] = "cdu"
        

    nornir_inventory = {
        "plugin": "DictInventory",
        "options": {
            "hosts": inventory["hosts"],
            "groups": inventory["groups"],
            "defaults": {},
        },
    }

    nornir_inventory["options"]["groups"] = {"aruba": {"platform": "aruba_aoscx", "connection_options": { "scrapli": {"extras": {"auth_strict_key": False}}}}, "dell": {"platform": "dellos10"}, "mellanox": {"platform": "mellanox"}}

    if sls_inventory:
        return nornir_inventory, sls_variables
    else:
        return nornir_inventory