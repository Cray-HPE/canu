"""CANU report commands."""
import click
from click_help_colors import HelpColorsGroup

from canu.report.network import network
from canu.report.switch import switch


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def report(ctx):
    """Canu report commands."""


report.add_command(network.network)
report.add_command(switch.switch)
