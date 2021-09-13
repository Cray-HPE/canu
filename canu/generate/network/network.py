"""CANU generate network commands."""
import click
from click_help_colors import HelpColorsGroup

from .config import config


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.pass_context
def network(ctx):
    """Canu generate network commands."""
    pass


network.add_command(config.config)
