import click

from canu.style import Style
from canu.config.pvlan import pvlan


@click.group(cls=Style.CanuHelpColorsGroup)
def config():
    """CANU config commands."""


config.add_command(pvlan) 