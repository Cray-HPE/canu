"""CANU Commands that validate a switch."""
import click
from click_help_colors import HelpColorsGroup

from canu.validate.switch.config import config


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def switch(ctx):
    """Commands that validate a switch."""


switch.add_command(config.config)
