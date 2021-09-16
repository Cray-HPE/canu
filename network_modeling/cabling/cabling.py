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
