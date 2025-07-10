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
"""parse aruba bgp config and test for missing neighbors."""
from ttp import ttp


def bgp_config(result, vlan_ips, vrf, mtn_acls=None):
    """Verify NCN-W IPs in SLS are BGP neighbors on the switch.

    Args:
        result: show run bgp
        vlan_ips: list of NCN and Switch IPs
        vrf: Named VRF used for CSM networks
        mtn_acls: Mountain Cabinet ACLs

    Returns:
        Pass or fail
    """
    # TTP template to convert switch show command to structured data.
    aruba_aoscx_show_run_bgp = """
<group name="bgp_cfg.vrfs.default">
router bgp {{ asn }}
    <group name="peers.{{ neighbor }}**">
    neighbor {{ neighbor | _start_ }} remote-as {{ remote_asn }}
    neighbor {{ neighbor }} {{ passive | macro("is_passive") }}
    </group>
        <group name="peers.{{ neighbor }}**">
        neighbor {{ neighbor }} {{ activate | exclude("passive") | macro("is_active") }}
        </group>
        <group name="peers.{{ neighbor }}**.route-map">
        neighbor {{ neighbor }} route-map {{ route-map-in }} in
        </group>
        <group name="peers.{{ neighbor }}**.route-map**">
        neighbor {{ neighbor }} route-map {{ route-map-out }} out
        </group>
</group>
<group name="bgp_cfg.vrfs.{{ vrf }}">
    vrf {{ vrf }}
        bgp router-id {{ bgp_rid }}
        maximum-paths {{ max_paths }}
        timers bgp {{ keepalive_timer }} {{ hold_timer }}
        distance bgp {{ ebgp_distance }} {{ ibgp_distance }}
        <group name="peers.{{ neighbor }}**">
        neighbor {{ neighbor | _start_ }} remote-as {{ remote_asn }}
        neighbor {{ neighbor }} {{ passive | macro("is_passive") }}
        </group>
            <group name="peers.{{ neighbor }}**">
            neighbor {{ neighbor }} {{ activate | macro("is_active") }}
            </group>
            <group name="peers.{{ neighbor }}**">
            neighbor {{ neighbor }} route-map {{ route-map-in }} in
            </group>
            <group name="peers.{{ neighbor }}**">
            neighbor {{ neighbor }} route-map {{ route-map-out }} out
            </group>
</group>
    """
    # Parse the aruba "show run bgp" command
    result_parsed = ttp(str(result), aruba_aoscx_show_run_bgp)
    result_parsed.parse()
    output = result_parsed.result()

    exception = None
    result = "PASS"
    success = True

    # Get BGP peers from switch config
    bgp_peers = {}
    bgp_peers.update(output[0][0]["bgp_cfg"]["vrfs"][vrf]["peers"])
    bgp_peers.update(output[0][0]["bgp_cfg"]["vrfs"]["default"]["peers"])

    # Get the worker nodes CMN and NMN IPs
    # If those are not in the BGP config on the switch add them to the list.

    missing_neighbors = [
        data["name"]
        for data in (
            entry
            for net, vlan_data in vlan_ips.items()
            for entry in vlan_data.get("ips", [])
            if "ncn-w" in entry["name"]
            and any(s in entry["name"] for s in ["cmn", "nmn"])
            and entry["ipv4_address"] not in bgp_peers
        )
    ]

    # Add missing neighbors to test exception message.
    if missing_neighbors:
        missing_neighbors_string = ", ".join(missing_neighbors)
        exception = (
            f"Missing BGP Neighbors: {missing_neighbors_string}\n"
            "This is usually caused by changing networks used by CSM or adding worker nodes"
        )
        result = "FAIL"

    return {
        "exception": exception,
        "result": result,
        "success": success,
    }
