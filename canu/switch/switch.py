import click
from click_help_colors import HelpColorsGroup

from .firmware import firmware


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def switch(ctx):  # pylint: disable=unused-argument
    """The SWITCH command will help troubleshoot, update, or validate an individual switch"""
    pass


switch.add_command(firmware.firmware)
