#!/usr/bin/env python3

import sys
import pprint
import yaml
from jinja2 import Environment, FileSystemLoader
import yamale

template_file = "ncn_port_config.j2"

devices = {}
master = [
    {"description": "ncn-m001 port mgmt0", "lag_number": "1", "interface": "1/1/1"}
]
devices["master"] = master

worker = [
    {"description": "ncn-w001 port mgmt0", "lag_number": "2", "interface": "1/1/2"}
]
devices["worker"] = worker

storage = [
    {"description": "ncn-s001 port mgmt0", "lag_number": "3", "interface": "1/1/3"}
]
devices["storage"] = storage


file_loader = FileSystemLoader("templates")
env = Environment(
    loader=file_loader, trim_blocks=True
)  # Trim blocks removes trailing newline
template = env.get_template(template_file)  # Defaults to templates/<file>
output = template.render(devices=devices)

print(output)

print(output, file=open("../models/output.md", "a"))
with open("switch_config_output.md", "w") as file:
    file.write(output)

