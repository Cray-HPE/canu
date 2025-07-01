# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Functions for testing CANU commands."""
import difflib

import pkg_resources

canu_version = pkg_resources.get_distribution("canu").version

banner_version = f"# CANU version: {canu_version}\n"


def diff_config_files(golden_file_name, test_file_name):
    """Compare a test config file with a golden config file."""
    with open(golden_file_name, "r") as file:
        golden_config = file.readlines()
    with open(test_file_name, "r") as file:
        test_config = file.readlines()

    d = difflib.Differ()
    full_diff = list(d.compare(golden_config, test_config))
    # Clean up - remove same lines " ", diff description lines "?", and CANU version
    # lines (tested elsewhere) so that a real diff size can be obtained. The CANU version
    # banner actual number will often be different between golden and testing so we don't
    # test this.
    real_diff = [
        x for x in full_diff
        if x[0] != " "
        if x[0] != "?"
        if banner_version[:14] not in x
    ]

    # If there's a real diff then print out the verbose diff (in stdout)
    # for debugging.
    if len(real_diff) != 0:
        for myline in full_diff:
            print(myline, end="")

    return len(real_diff)
