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
"""CANU Commands that validate the Shasta switch network."""
import click

from canu.style import Style
from canu.validate.network import network
from canu.validate.paddle import paddle
from canu.validate.paddle_cabling import paddle_cabling
from canu.validate.shcd import shcd
from canu.validate.shcd_cabling import shcd_cabling
from canu.validate.switch import switch


@click.group(
    cls=Style.CanuHelpColorsGroup,
)
@click.pass_context
def validate(ctx):
    """CANU validate commands."""


validate.add_command(network.network)
validate.add_command(paddle.paddle)
validate.add_command(paddle_cabling.paddle_cabling)
validate.add_command(shcd.shcd)
validate.add_command(shcd_cabling.shcd_cabling)
validate.add_command(switch.switch)
