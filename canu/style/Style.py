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
"""Style to keep styling in one place."""

from click_help_colors import HelpColorsCommand, HelpColorsGroup


class CanuHelpColorsCommand(HelpColorsCommand):
    """A class for customizing the help colors in a command.

    Attributes
    ----------
    help_headers_color : string
        A color for the help headers.
    help_options_color : string
        A color for the help options.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Set the header and option colors."""
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"


class CanuHelpColorsGroup(HelpColorsGroup):
    """A class for customizing the help colors in a group.

    Attributes
    ----------
    help_headers_color : string
        A color for the help headers.
    help_options_color : string
        A color for the help options.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Set the header and option colors."""
        super().__init__(*args, **kwargs)
        self.help_headers_color = "blue"
        self.help_options_color = "yellow"
