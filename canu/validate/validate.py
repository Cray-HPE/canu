"""CANU Commands that validate the Shasta switch network."""
import click
from click_help_colors import HelpColorsGroup

from .network import network
from .shcd import shcd
from .shcd_cabling import shcd_cabling
from .switch import switch


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def validate(ctx):
    """CANU validate commands."""
    pass


validate.add_command(network.network)
validate.add_command(shcd.shcd)
validate.add_command(shcd_cabling.shcd_cabling)
validate.add_command(switch.switch)
