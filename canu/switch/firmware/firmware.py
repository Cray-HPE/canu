"""CANU commands for an individual switch."""
import click
from click_default_group import DefaultGroup

# from click_help_colors import HelpColorsGroup

from .status import status
from .update import update


@click.group(
    cls=DefaultGroup,
    default="status",
    default_if_no_args=True
    # cls=HelpColorsGroup,
    # help_headers_color="yellow",
    # help_options_color="blue",
)
@click.pass_context
def firmware(ctx):  # pylint: disable=unused-argument
    """Troubleshoot, update, or validate an individual switch."""
    pass


firmware.add_command(status.status)
firmware.add_command(update.update)
