"""CANU generate commands."""
import click
from click_help_colors import HelpColorsGroup

from canu.generate.network import network
from canu.generate.switch import switch


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def generate(ctx):
    """Canu generate commands."""


generate.add_command(network.network)
generate.add_command(switch.switch)
