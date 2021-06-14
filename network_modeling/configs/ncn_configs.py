#!/usr/bin/env python3

import sys
import pprint
import yaml
from jinja2 import Environment, FileSystemLoader
import yamale


cabling_file = "../cabling/standards/cabling.yaml"
yamale_schema = "../cabling/standards/cabling_schema.yaml"
template_file = "ncn_port_config.j2"

schema = yamale.make_schema(yamale_schema)
data = yamale.make_data(cabling_file)
yamale.validate(
    schema, data,
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
            "interface": "1/1/1",
        }
    if node["subtype"] == "worker":
        node["config"] = {
            "description": "ncn-w001 port mgmt0",
            "lag_number": "2",
            "interface": "1/1/2",
        }
    if node["subtype"] == "storage":
        node["config"] = {
            "description": "ncn-s001 port mgmt0",
            "lag_number": "3",
            "interface": "1/1/3",
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

