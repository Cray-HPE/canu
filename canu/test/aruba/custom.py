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
"""parse aruba lacp interfaces and return blocked ports."""
from ttp import ttp


def lacp_test(result):
    """Test LACP ports.

    Args:
        result: show lacp interfaces

    Returns:
        Pass or fail
    """
    # TTP template to convert switch show command to structured data.
    aruba_aoscx_show_lacp_interfaces = """
<group name = "interfaces.{{interface}}">
{{ interface }}      lag{{ lag }}   {{ port_id }}     {{ port_pri }}     {{ state }}  {{ system-id }} {{ system_pri }}  {{ aggr_key }}    {{ forwarding_state }}
</group>
    """

    result_parsed = ttp(str(result), aruba_aoscx_show_lacp_interfaces)
    result_parsed.parse()
    output = result_parsed.result()
    lacp_blocked_ports = ""
    exception = None
    result = "PASS"
    success = True
    for interface, data in output[0][0]["interfaces"].items():
        if data["forwarding_state"] == "lacp-block":
            lacp_blocked_ports += (interface) + "\n"
            result = "FAIL"
            success = False
            exception = f"LACP port blocks \n{lacp_blocked_ports}"
    return {
        "exception": exception,
        "result": result,
        "success": success,
    }
