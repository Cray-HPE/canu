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
cabling_data = yamale.make_data(cabling_file)
yamale.validate(
    schema,
    cabling_data,
)

# Load cabling standards
with open(cabling_file) as f:
    cabling = yaml.load(f, Loader=yaml.FullLoader)

if "nodes" not in cabling:
    sys.exit(1)


for node in cabling["nodes"]:
    subtype = node["subtype"]
    if subtype == "master":
        node_config = {
            "description": "ncn-m001 port mgmt0",
            "lag_number": "1",
            "PORT": "1/1/1",
        }
    if subtype == "worker":
        node_config = {
            "description": "ncn-w001 port mgmt0",
            "lag_number": "2",
            "PORT": "1/1/2",
        }
    if subtype == "storage":
        node_config = {
            "description": "ncn-s001 port mgmt0",
            "lag_number": "3",
            "PORT": "1/1/3",
        }
    if subtype == "uan":
        node_config = {
            "description": "uan",
            "lag_number": "4",
            "PORT": "1/1/4",
            "interface_nmn": "1/1/5",
        }
    if subtype == "login":
        node_config = {
            "description": "login node",
            "lag_number": "5",
            "PORT": "1/1/6",
        }
    if subtype == "cec":
        node_config = {
            "description": "cec",
            "PORT": "1/1/7",
        }
    if subtype == "cmm":
        node_config = {
            "description": "cmm",
            "PORT": "1/1/8",
            "lag_number": "6",
        }
    if subtype == "bmc":
        node_config = {
            "description": "bmc",
            "interface": "1/1/9",
        }

    node["config"] = node_config

pprint.pprint(cabling["nodes"])  # noqa:WPS421
# Load template and process

file_loader = FileSystemLoader("templates")
env = Environment(
    loader=file_loader,
    trim_blocks=True,
)  # Trim blocks removes trailing newline
template = env.get_template(template_file)  # Defaults to templates/<file>
output = template.render(cabling=cabling)
print(output)  # noqa:WPS421

# print(output, file=open("../models/output.md", "a"))
with open("port_configs.md", "w") as file_output:
    file_output.write(output)
