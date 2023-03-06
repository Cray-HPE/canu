# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""CANU command to upgrade in .venv."""
import os
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent


@click.option(
    "--editable",
    is_flag=True,
    help="enable dev mode.",
    required=False,
)
@click.command(cls=HelpColorsCommand)
@click.pass_context
def upgrade(
    upgrade,
    editable,
):
    """Upgrade Canu running in virtual environment.
    
    Note: Requires internet connection to be able to reach git.=
    In Air gapped system you will have to export the latest canu image from github.
        Github address: https://github.com/Cray-HPE/canu.git
    
        --------
    \f
    # noqa:  D301, B950
    
    Args:
        upgrade: Upgrade CANU
        editable: CANU dev mode.
    """
    if editable:
        os.system("python -m pip install --editable .")
    if not editable:
        os.system("python -m pip install git+https://github.com/Cray-HPE/canu.git@main")
