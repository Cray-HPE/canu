"""CANU Commands that validate the Shasta switch network."""
import click
from click_help_colors import HelpColorsGroup

from canu.validate.network import network
from canu.validate.shcd import shcd
from canu.validate.shcd_cabling import shcd_cabling
from canu.validate.switch import switch


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def validate(ctx):
    """CANU validate commands."""


validate.add_command(network.network)
validate.add_command(shcd.shcd)
validate.add_command(shcd_cabling.shcd_cabling)
validate.add_command(switch.switch)
