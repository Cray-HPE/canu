"""CANU generate switch commands."""
import click
from click_help_colors import HelpColorsGroup

from canu.generate.switch.config import config


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def switch(ctx):
    """Canu generate switch commands."""
    pass


switch.add_command(config.config)
