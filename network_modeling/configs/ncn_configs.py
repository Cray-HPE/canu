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
"""Generate the port_configs.md file."""
# !/usr/bin/env python3

import pprint
import sys

from jinja2 import Environment, FileSystemLoader
import yamale
import yaml


cabling_file = "../cabling/standards/cabling.yaml"
yamale_schema = "../cabling/standards/cabling_schema.yaml"
template_file = "edge_port_config.j2"

schema = yamale.make_schema(yamale_schema)
data = yamale.make_data(cabling_file)
yamale.validate(
    schema,
    data,
)

#
# Load cabling standards
#
with open(cabling_file) as file:
    cabling = yaml.load(file, Loader=yaml.FullLoader)

if "nodes" not in cabling:
    sys.exit(1)


for node in cabling["nodes"]:
    if node["subtype"] == "master":
        node["config"] = {
            "description": "ncn-m001 port mgmt0",
            "lag_number": "1",
            "PORT": "1/1/1",
        }
    if node["subtype"] == "worker":
        node["config"] = {
            "description": "ncn-w001 port mgmt0",
            "lag_number": "2",
            "PORT": "1/1/2",
        }
    if node["subtype"] == "storage":
        node["config"] = {
            "description": "ncn-s001 port mgmt0",
            "lag_number": "3",
            "PORT": "1/1/3",
        }
    if node["subtype"] == "uan":
        node["config"] = {
            "description": "uan",
            "lag_number": "4",
            "PORT": "1/1/4",
            "interface_nmn": "1/1/5",
        }
    if node["subtype"] == "login":
        node["config"] = {
            "description": "login node",
            "lag_number": "5",
            "PORT": "1/1/6",
        }
    if node["subtype"] == "cec":
        node["config"] = {
            "description": "cec",
            "PORT": "1/1/7",
        }
    if node["subtype"] == "cmm":
        node["config"] = {
            "description": "cmm",
            "PORT": "1/1/8",
            "lag_number": "6",
        }
    if node["subtype"] == "bmc":
        node["config"] = {
            "description": "bmc",
            "interface": "1/1/9",
        }

pprint.pprint(cabling["nodes"])
# Load template and process

file_loader = FileSystemLoader("templates")
env = Environment(
    loader=file_loader, trim_blocks=True
)  # Trim blocks removes trailing newline
template = env.get_template(template_file)  # Defaults to templates/<file>
output = template.render(cabling=cabling)
print(output)

# print(output, file=open("../models/output.md", "a"))
with open("port_configs.md", "w") as file:
    file.write(output)
