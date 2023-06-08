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
"""parse aruba interface config and verify IPs are correct."""
from ttp import ttp


def vlan_interface_config(result, vlan_ips):
    """Verify the switch VLAN IPs match SLS.

    Args:
        result: show run
        vlan_ips: list of NCN and Switch IPs

    Returns:
        Pass or fail
    """
    aruba_aoscx_show_run_interface = """
<group name = "config">
hostname {{ hostname }}
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
</group>
    """
    # Parse the aruba "show run"
    result_parsed = ttp(str(result), aruba_aoscx_show_run_interface)
    result_parsed.parse()
    output = result_parsed.result()

    # Get the vlan config and hostname
    vlan_config = output[0][0]["config"]["vlan"]
    hostname = output[0][0]["config"]["hostname"]

    exception = []
    result = "PASS"
    success = True

    # Verify that the IP addresses from SLS match the IPs that are on the switch.

    for net, net_data in vlan_ips.items():
        vlan = str(net_data["vlan"])
        for data in net_data.get("ips", []):
            try:
                ip = data["ipv4_address"]
                name = data["name"]
                if hostname in name:
                    if vlan in vlan_config and ip in vlan_config[vlan]["ip"]:
                        continue
                    else:
                        exception.append(
                            f"VLAN IP Incorrect for network: {net} VLAN {vlan}",
                        )
                        result = "FAIL"
                        success = False
            except KeyError:
                exception.append(
                    f"Missing IP address on VLAN interface for network: {net}",
                )
                result = "FAIL"
                success = False

    # Check if there are any incorrect/missing IP addresses from the switches
    if exception:
        exception = "\n".join(exception)
        exception += "\nVerify IPs in SLS matches the switch config"
    else:
        exception = None

    # return the results of the test
    return {
        "exception": exception,
        "result": result,
        "success": success,
    }
