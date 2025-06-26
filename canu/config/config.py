"""CANU config commands module."""

import click

from canu.config.pvlan import pvlan
from canu.style import Style


@click.group(cls=Style.CanuHelpColorsGroup)
def config():
    """CANU config commands."""


config.add_command(pvlan)
