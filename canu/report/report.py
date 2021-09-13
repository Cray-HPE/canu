"""CANU report commands."""
import click
from click_help_colors import HelpColorsGroup

from .network import network
from .switch import switch


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def report(ctx):
    """Canu report commands."""
    pass


report.add_command(network.network)
report.add_command(switch.switch)
