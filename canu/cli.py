import os.path
import sys

import click
from click_help_colors import HelpColorsGroup
import ruamel.yaml

from canu.network import network
from canu.switch import switch

yaml = ruamel.yaml.YAML()


# To get the canu.yaml file in the parrent directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    parent_directory = sys._MEIPASS
else:
    prog = __file__
    current_directory = os.path.dirname(os.path.abspath(prog))
    parent_directory = os.path.split(current_directory)[0]

canu_config_file = os.path.join(parent_directory, "canu.yaml")


with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

CONTEXT_SETTING = dict(
    obj={
        "shasta": "",
        "config": canu_config,
    }
)


@click.group(
    context_settings=CONTEXT_SETTING,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--shasta",
    "-s",
    type=click.Choice(["1.4", "1.5"]),
    help="Shasta network version",
    required=True,
)
@click.pass_context
def cli(ctx, shasta):
    """The CSM Automatic Network Utility will float through a new Shasta network and make setup a breeze."""
    ctx.ensure_object(dict)

    ctx.obj["shasta"] = shasta


cli.add_command(switch.switch)
cli.add_command(network.network)

if __name__ == "__main__":
    cli()
