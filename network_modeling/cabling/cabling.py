#!/usr/bin/env python3

import sys
import pprint
import yaml
from jinja2 import Environment, FileSystemLoader
import yamale


cabling_file = "./standards/cabling.yaml"
yamale_schema = "./standards/cabling_schema.yaml"
template_file = "cabling.md.j2"

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

pprint.pprint(cabling)


# Load template and process

file_loader = FileSystemLoader("templates")
env = Environment(
    loader=file_loader, trim_blocks=True
)  # Trim blocks removes trailing newline
template = env.get_template(template_file)  # Defaults to templates/<file>
output = template.render(cabling=cabling)

# print(output, file=open("../models/output.md", "a"))
with open("output.md", "w") as file:
    file.write(output)

