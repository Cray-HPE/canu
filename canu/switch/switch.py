"""CANU commands for an individual switch."""
import click
from click_help_colors import HelpColorsGroup

from .cabling import cabling
from .config import config
from .firmware import firmware


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def switch(ctx):  # pylint: disable=unused-argument
    """Troubleshoot, update, or validate an individual switch."""
    pass


switch.add_command(cabling.cabling)
switch.add_command(config.config)
switch.add_command(firmware.firmware)
