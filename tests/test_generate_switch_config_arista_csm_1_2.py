# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""Test CHNU generate switch config commands."""
import json
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli
from canu.tests.test_generate_switch_config_aruba_csm_1_2 import sls_input

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_1.1.5.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
custom_file_name = "aruba_custom.yaml"
custom_file = path.join(test_file_directory, "data", custom_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T53,J14,T34,J14,T27"
sls_file = "sls_file.json"
csm = "1.2"
switch_name = "sw-spine-001"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

test_file_name_tds = "TDS_Architecture_Golden_Config_1.1.5.xlsx"
test_file_tds = path.join(test_file_directory, "data", test_file_name_tds)
architecture_tds = "TDS"
tabs_tds = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners_tds = "J14,T30,J14,T53,J14,T32,J14,T27"

canu_version_file = path.join(test_file_directory.resolve().parent, "canu", ".version")
with open(canu_version_file, "r") as file:
    canu_version = file.readline()

runner = testing.CliRunner()


def test_switch_config_sw_edge_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary edge switch config."""
    sw_edge = "sw-edge-001"

    with runner.isolated_filesystem():
        with open(sls_file, "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                sw_edge,
            ],
        )
        assert result.exit_code == 0

        print(result.output)
        assert (
            "interface loopback 0\n"
            + "    ip address 10.2.1.2/32\n"
            + "   \n"
            + "vlan 4091\n"
            + " name mlag-ibgp\n"
            + " trunk group mlag-peer\n"
            + "!\n"
            + "int vlan 4091\n"
            + " ip address 10.2.3.2/31\n"
            + " mtu 9214\n"
            + "!\n"
            + " no spanning-tree vlan-id 4091\n"
            + "\n"
            + "interface Vlan5\n"
            + "   ip address 192.168.200.2/24\n"
            + "   ip virtual-router address 192.168.200.1\n"
            + "ip routing\n"
            + "\n"
            + "ip prefix-list HSN seq 10 permit 192.168.200.0/24 ge 24\n"
            + "!\n"
            + "route-map HSN permit 5\n"
            + "   match ip address prefix-list HSN\n"
            + "\n"
            + "router bgp 65533\n"
            + "   distance bgp 20 200 200\n"
            + "   router-id 10.2.1.2\n"
            + "   maximum-paths 32\n"
            + "   neighbor 10.2.3.3 remote-as 65533\n"
            + "   neighbor 10.2.3.3 next-hop-self\n"
            + "   neighbor 192.168.200.4 remote-as 65530\n"
            + "   neighbor 192.168.200.4 passive\n"
            + "   neighbor 192.168.200.4 route-map HSN in\n"
            + "   neighbor 192.168.200.5 remote-as 65530\n"
            + "   neighbor 192.168.200.5 passive\n"
            + "   neighbor 192.168.200.5 route-map HSN in\n"
            + "   neighbor 192.168.200.6 remote-as 65530\n"
            + "   neighbor 192.168.200.6 passive\n"
            + "   neighbor 192.168.200.6 route-map HSN in\n"
        ) in str(result.output)


def test_switch_config_sw_edge_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary edge switch config."""
    sw_edge = "sw-edge-002"

    with runner.isolated_filesystem():
        with open(sls_file, "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                sw_edge,
            ],
        )
        assert result.exit_code == 0

        print(result.output)
        assert (
            "interface loopback 0\n"
            + "    ip address 10.2.1.3/32\n"
            + "   \n"
            + "vlan 4091\n"
            + " name mlag-ibgp\n"
            + " trunk group mlag-peer\n"
            + "!\n"
            + "int vlan 4091\n"
            + " ip address 10.2.3.3/31\n"
            + " mtu 9214\n"
            + "!\n"
            + " no spanning-tree vlan-id 4091\n"
            + "\n"
            + "interface Vlan5\n"
            + "   ip address 192.168.200.3/24\n"
            + "   ip virtual-router address 192.168.200.1\n"
            + "ip routing\n"
            + "\n"
            + "ip prefix-list HSN seq 10 permit 192.168.200.0/24 ge 24\n"
            + "!\n"
            + "route-map HSN permit 5\n"
            + "   match ip address prefix-list HSN\n"
            + "\n"
            + "router bgp 65533\n"
            + "   distance bgp 20 200 200\n"
            + "   router-id 10.2.1.3\n"
            + "   maximum-paths 32\n"
            + "   neighbor 10.2.3.2 remote-as 65533\n"
            + "   neighbor 10.2.3.2 next-hop-self\n"
            + "   neighbor 192.168.200.4 remote-as 65530\n"
            + "   neighbor 192.168.200.4 passive\n"
            + "   neighbor 192.168.200.4 route-map HSN in\n"
            + "   neighbor 192.168.200.5 remote-as 65530\n"
            + "   neighbor 192.168.200.5 passive\n"
            + "   neighbor 192.168.200.5 route-map HSN in\n"
            + "   neighbor 192.168.200.6 remote-as 65530\n"
            + "   neighbor 192.168.200.6 passive\n"
            + "   neighbor 192.168.200.6 route-map HSN in\n"
        ) in str(result.output)
