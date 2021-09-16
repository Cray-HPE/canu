"""CANU Commands that validate the network."""
import click
from click_help_colors import HelpColorsGroup

from canu.validate.network.bgp import bgp
from canu.validate.network.cabling import cabling
from canu.validate.network.config import config


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def network(ctx):
    """Commands that validate the network."""


network.add_command(bgp.bgp)
network.add_command(cabling.cabling)
network.add_command(config.config)
