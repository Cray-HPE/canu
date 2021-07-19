"""CANU Commands that validate the Shasta switch network."""
import click
from click_help_colors import HelpColorsGroup

from .bgp import bgp
from .cabling import cabling
from .config import config
from .shcd import shcd
from .shcd_cabling import shcd_cabling


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def validate(ctx):
    """Commands that validate the network."""
    pass


validate.add_command(bgp.bgp)
validate.add_command(cabling.cabling)
validate.add_command(config.config)
validate.add_command(shcd.shcd)
validate.add_command(shcd_cabling.shcd_cabling)
