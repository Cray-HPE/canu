"""CANU report switch commands."""
import click
from click_help_colors import HelpColorsGroup

from .cabling import cabling
from .firmware import firmware


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def switch(ctx):
    """Report switch commands."""
    pass


switch.add_command(cabling.cabling)
switch.add_command(firmware.firmware)
