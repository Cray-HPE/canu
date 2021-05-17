"""CANU Commands that configure switches on the network."""
import click
from click_help_colors import HelpColorsGroup

from .bgp import bgp


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def config(ctx):
    """Commands that configure switches on the network."""
    pass


config.add_command(bgp.bgp)
