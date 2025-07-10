# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Load yaml file."""
import os
import sys

import click
import yaml


def load_yaml(file):
    """Load yaml file and return dictionary.

    Args:
        file: yaml file.

    Returns:
        loaded yaml file.
    """
    try:
        with open(os.path.join(file), "r") as f:
            yaml_file = yaml.safe_load(f)
    except FileNotFoundError:
        click.secho(
            f"The {file} file was not found, check that you entered the right file name and path",
            fg="red",
        )
        sys.exit(1)
    except yaml.YAMLError as e:
        click.secho(f"{str(e)}, YAML error parsing {file}", fg="red")
        sys.exit(1)
    return yaml_file
