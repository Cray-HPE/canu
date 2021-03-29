"""CANU Commands that work with the entire Shasta switch network."""
import click
from click_help_colors import HelpColorsGroup

from .firmware import firmware


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def network(ctx):
    """Commands that work on the entire network."""
    pass


network.add_command(firmware.firmware)
