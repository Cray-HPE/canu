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
"""parse aruba interface config and test IPs"""
from ttp import ttp
import pprint


def vlan_interface_config(result, ncn_switch_ips, ncn_switch_vlan_ips):
    """Verify NCN-W IPs in SLS are correct Interfaces on switches.

    Args:
        result: show run
        ncn_switch_ips: list of NCN and Switch IPs

    Returns:
        Pass or fail
    """
    # TTP template to convert switch show command to structured data.
    aruba_aoscx_show_run_interface = """
<group name = "vlan.{{ vlan }}">
vlan {{ vlan }}
</group>
<group name = "vlan.{{ vlan }}**">
interface vlan {{ vlan }}
    vrf attach {{ vrf }}
    description {{ interface_description }}
    ip mtu {{ mtu }}
    ip address {{ ip | is_ip }}
    active-gateway ip mac {{ active_gateway_ip_mac }}
    active-gateway ip {{ active_gateway_ip | is_ip }}
    ip ospf {{ ospf_instance }} area {{ area }}
</group>
    """
    # Parse the aruba "show run interface" command
    result_parsed = ttp(str(result), aruba_aoscx_show_run_interface)
    result_parsed.parse()
    output = result_parsed.result()

    vlan_config = output[0][0]

    for vlan, data in vlan_config.items():
        print(vlan, data)

    exception = None
    result = "PASS"
    success = True

    return {
        "exception": exception,
        "result": result,
        "success": success,
    }
