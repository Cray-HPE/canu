"""CANU commands report on the switch network."""
import click
from click_help_colors import HelpColorsGroup

from canu.report.network.cabling import cabling
from canu.report.network.firmware import firmware


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def network(ctx):
    """Commands that report on the entire network."""


network.add_command(cabling.cabling)
network.add_command(firmware.firmware)
