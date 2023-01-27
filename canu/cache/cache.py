# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
"""CANU Commands that configure switches on the network."""
from os import path, remove
import sys

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from ruamel.yaml import YAML

from canu.utils.cache import cache_directory


yaml = YAML()


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def cache(ctx):
    """Commands that configure switches on the network."""


@cache.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def location(ctx):
    """Print the directory where the canu_cache.yaml file is located."""
    click.echo(cache_directory())


@cache.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def delete(ctx):
    """Delete the canu_cache.yaml file."""
    cache_file = f"{cache_directory()}/canu_cache.yaml"
    if path.exists(cache_file):
        remove(cache_file)


@cache.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def print(ctx):
    """Print the canu_cache.yaml file."""
    canu_cache_file = f"{cache_directory()}/canu_cache.yaml"

    file_exists = path.isfile(canu_cache_file)

    if file_exists:
        with open(canu_cache_file, "r+") as canu_exist_f:
            canu_cache = yaml.load(canu_exist_f)

        click.echo(yaml.dump(canu_cache, sys.stdout, transform=color_transform))
    else:
        click.secho("No canu_cache.yaml file found.", fg="red")


def color_transform(s):
    """Transform the yaml in the canu_cache.yaml file to add color."""
    return (
        s.replace("switches:", click.style("switches:", fg="blue"))
        .replace("cabling:", click.style("cabling:", fg="blue"))
        .replace("vendor:", click.style("vendor:", fg="blue"))
        .replace("updated_at:", click.style("updated_at:", fg="blue"))
        .replace("hostname:", click.style("hostname:", fg="blue"))
        .replace("platform_name:", click.style("platform_name:", fg="blue"))
        .replace("- ip_address:", click.style("- ip_address:", fg="blue"))
        .replace("firmware:", click.style("firmware:", fg="blue"))
        .replace("status:", click.style("status:", fg="blue"))
        .replace("current_version:", click.style("current_version:", fg="blue"))
        .replace("primary_version:", click.style("primary_version:", fg="blue"))
        .replace("secondary_version:", click.style("secondary_version:", fg="blue"))
        .replace("version:", click.style("version:", fg="blue"))
        .replace("default_image:", click.style("default_image:", fg="blue"))
        .replace("booted_image:", click.style("booted_image:", fg="blue"))
        .replace("- neighbor:", click.style("- neighbor:", fg="green"))
        .replace(
            "neighbor_description:",
            click.style("neighbor_description:", fg="green"),
        )
        .replace("neighbor_port:", click.style("neighbor_port:", fg="green"))
        .replace(
            "neighbor_port_description:",
            click.style("neighbor_port_description:", fg="green"),
        )
        .replace(
            "neighbor_chassis_id:",
            click.style("neighbor_chassis_id:", fg="green"),
        )
    )
