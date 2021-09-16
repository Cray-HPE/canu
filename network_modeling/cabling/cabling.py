#!/usr/bin/env python3
"""Generate the cabling_output.md file."""

import pprint
import sys

from jinja2 import Environment, FileSystemLoader
import yamale
import yaml


cabling_file = "./standards/cabling.yaml"
yamale_schema = "./standards/cabling_schema.yaml"
template_file = "cabling.md.j2"

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

pprint.pprint(cabling)  # noqa:WPS421


# Load template and process

file_loader = FileSystemLoader("templates")
env = Environment(
    loader=file_loader,
    trim_blocks=True,
)  # Trim blocks removes trailing newline
template = env.get_template(template_file)  # Defaults to templates/<file>
output = template.render(cabling=cabling)

# print(output, file=open("../models/output.md", "a"))
with open("./generated/sample.md", "w") as file_output:
    file_output.write(output)
