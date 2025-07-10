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
"""parse aruba ip route output and return pass or fail."""
from ntc_templates.parse import parse_output


def run(result):
    """Test TFTP route.

    Args:
        result: show ip route all-vrfs output

    Returns:
        Pass or fail
    """
    routes = str(result)
    result_parsed = (
        parse_output(
            platform="aruba_aoscx",
            command="show ip route all-vrfs",
            data=routes,
        ),
    )
    for route in result_parsed:
        if route["ip"] == "10.92.100.60/32" and len(route["iface"]) > 1:
            return {
                "exception": "Multiple Routes to tftp server",
                "result": "FAIL",
                "success": False,
            }
