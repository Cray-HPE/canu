# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
"""Test CANU generate switch config commands."""
import json
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Architecture_Golden_Config_Dellanox.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
override_file_name = "override.yaml"
override_file = path.join(test_file_directory, "data", override_file_name)
architecture = "v1"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T30,J14,T34,J14,T28,J14,T27"
sls_file = "sls_file.json"
csm = "1.2"
switch_name = "sw-spine-001"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

runner = testing.CliRunner()


def test_switch_config_spine_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary spine config."""
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
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert (
            "hostname sw-spine-001\n"
            + "no cli default prefix-modes enable\n"
            + "  protocol mlag\n"
            + "  protocol bgp\n"
            + "lacp\n"
            + "interface mlag-port-channel 1\n"
            + "interface mlag-port-channel 2\n"
            + "interface mlag-port-channel 3\n"
            + "interface mlag-port-channel 4\n"
            + "interface mlag-port-channel 5\n"
            + "interface mlag-port-channel 6\n"
            + "interface mlag-port-channel 7\n"
            + "interface mlag-port-channel 8\n"
            + "interface mlag-port-channel 9\n"
            + "interface mlag-port-channel 13\n"
            + "interface mlag-port-channel 151\n"
            + "interface mlag-port-channel 201\n"
            + "interface ethernet 1/1 mtu 9216 force\n"
            + "interface ethernet 1/2 mtu 9216 force\n"
            + "interface ethernet 1/3 mtu 9216 force\n"
            + "interface ethernet 1/4 mtu 9216 force\n"
            + "interface ethernet 1/5 mtu 9216 force\n"
            + "interface ethernet 1/6 mtu 9216 force\n"
            + "interface ethernet 1/7 mtu 9216 force\n"
            + "interface ethernet 1/8 mtu 9216 force\n"
            + "interface ethernet 1/9 mtu 9216 force\n"
            + "interface ethernet 1/13 mtu 9216 force\n"
            + "interface ethernet 1/26 mtu 9216 force\n"
            + "interface ethernet 1/29 mtu 9216 force\n"
            + "interface ethernet 1/30 mtu 9216 force\n"
            + "interface mlag-port-channel 1 mtu 9216 force\n"
            + "interface mlag-port-channel 2 mtu 9216 force\n"
            + "interface mlag-port-channel 3 mtu 9216 force\n"
            + "interface mlag-port-channel 4 mtu 9216 force\n"
            + "interface mlag-port-channel 5 mtu 9216 force\n"
            + "interface mlag-port-channel 6 mtu 9216 force\n"
            + "interface mlag-port-channel 7 mtu 9216 force\n"
            + "interface mlag-port-channel 8 mtu 9216 force\n"
            + "interface mlag-port-channel 9 mtu 9216 force\n"
            + "interface mlag-port-channel 13 mtu 9216 force\n"
            + "interface mlag-port-channel 151 mtu 9216 force\n"
            + "interface mlag-port-channel 201 mtu 9216 force\n"
            + "interface ethernet 1/1 mlag-channel-group 1 mode active\n"
            + "interface ethernet 1/2 mlag-channel-group 2 mode active\n"
            + "interface ethernet 1/3 mlag-channel-group 3 mode active\n"
            + "interface ethernet 1/4 mlag-channel-group 4 mode active\n"
            + "interface ethernet 1/5 mlag-channel-group 5 mode active\n"
            + "interface ethernet 1/6 mlag-channel-group 6 mode active\n"
            + "interface ethernet 1/7 mlag-channel-group 7 mode active\n"
            + "interface ethernet 1/8 mlag-channel-group 8 mode active\n"
            + "interface ethernet 1/9 mlag-channel-group 9 mode active\n"
            + "interface ethernet 1/13 mlag-channel-group 13 mode active\n"
            + "interface ethernet 1/26 mlag-channel-group 151 mode active\n"
            + "interface ethernet 1/29 mlag-channel-group 201 mode active\n"
            + "interface ethernet 1/30 mlag-channel-group 201 mode active\n"
            + "interface mlag-port-channel 1 switchport mode hybrid\n"
            + "interface mlag-port-channel 2 switchport mode hybrid\n"
            + "interface mlag-port-channel 3 switchport mode hybrid\n"
            + "interface mlag-port-channel 4 switchport mode hybrid\n"
            + "interface mlag-port-channel 5 switchport mode hybrid\n"
            + "interface mlag-port-channel 6 switchport mode hybrid\n"
            + "interface mlag-port-channel 7 switchport mode hybrid\n"
            + "interface mlag-port-channel 8 switchport mode hybrid\n"
            + "interface mlag-port-channel 9 switchport mode hybrid\n"
            + "interface mlag-port-channel 13 switchport mode hybrid\n"
            + "interface mlag-port-channel 151 switchport mode hybrid\n"
            + "interface mlag-port-channel 201 switchport mode hybrid\n"
            + "interface ethernet 1/1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
            + "interface ethernet 1/2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
            + "interface ethernet 1/3 description sw-spine-001:3==>ncn-m003:pcie-slot1:1\n"
            + "interface ethernet 1/4 description sw-spine-001:4==>ncn-w001:pcie-slot1:1\n"
            + "interface ethernet 1/5 description sw-spine-001:5==>ncn-w002:pcie-slot1:1\n"
            + "interface ethernet 1/6 description sw-spine-001:6==>ncn-w003:pcie-slot1:1\n"
            + "interface ethernet 1/7 description sw-spine-001:7==>ncn-s001:pcie-slot1:1\n"
            + "interface ethernet 1/8 description sw-spine-001:8==>ncn-s002:pcie-slot1:1\n"
            + "interface ethernet 1/9 description sw-spine-001:9==>ncn-s003:pcie-slot1:1\n"
            + "interface ethernet 1/13 description sw-spine-001:13==>uan001:pcie-slot1:1\n"
            + "interface ethernet 1/26 description sw-spine-001:26==>sw-leaf-bmc-001:51\n"
            + "interface ethernet 1/29 description sw-spine-001:29==>sw-cdu-001:27\n"
            + "interface ethernet 1/30 description sw-spine-001:30==>sw-cdu-002:27\n"
            + "interface ethernet 1/31 description mlag-isl\n"
            + "interface ethernet 1/32 description mlag-isl\n"
            + "interface mlag-port-channel 1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
            + "interface mlag-port-channel 2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
            + "interface mlag-port-channel 3 description sw-spine-001:3==>ncn-m003:pcie-slot1:1\n"
            + "interface mlag-port-channel 4 description sw-spine-001:4==>ncn-w001:pcie-slot1:1\n"
            + "interface mlag-port-channel 5 description sw-spine-001:5==>ncn-w002:pcie-slot1:1\n"
            + "interface mlag-port-channel 6 description sw-spine-001:6==>ncn-w003:pcie-slot1:1\n"
            + "interface mlag-port-channel 7 description sw-spine-001:7==>ncn-s001:pcie-slot1:1\n"
            + "interface mlag-port-channel 8 description sw-spine-001:8==>ncn-s002:pcie-slot1:1\n"
            + "interface mlag-port-channel 9 description sw-spine-001:9==>ncn-s003:pcie-slot1:1\n"
            + "interface mlag-port-channel 13 description sw-spine-001:13==>uan001:pcie-slot1:1\n"
            + "interface mlag-port-channel 151 description sw-spine-001:26==>sw-leaf-bmc-001:51\n"
            + "interface mlag-port-channel 201 description sw-spine-001:29==>sw-cdu-001:27\n"
            + "interface mlag-port-channel 201 description sw-spine-001:30==>sw-cdu-002:27\n"
        ) in str(result.output)
        assert (
            "interface port-channel 100\n"
            + "interface ethernet 1/31 channel-group 100 mode active\n"
            + "interface ethernet 1/32 channel-group 100 mode active\n"
            + "interface port-channel 100 description mlag-isl\n"
            + "port-channel load-balance ethernet source-destination-ip ingress-port\n"
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 no shutdown\n"
            + "interface mlag-port-channel 2 no shutdown\n"
            + "interface mlag-port-channel 3 no shutdown\n"
            + "interface mlag-port-channel 4 no shutdown\n"
            + "interface mlag-port-channel 5 no shutdown\n"
            + "interface mlag-port-channel 6 no shutdown\n"
            + "interface mlag-port-channel 7 no shutdown\n"
            + "interface mlag-port-channel 8 no shutdown\n"
            + "interface mlag-port-channel 9 no shutdown\n"
            + "interface mlag-port-channel 13 no shutdown\n"
            + "interface mlag-port-channel 151 no shutdown\n"
            + "interface mlag-port-channel 201 no shutdown\n"
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 lacp-individual enable force\n"
            + "interface mlag-port-channel 2 lacp-individual enable force\n"
            + "interface mlag-port-channel 3 lacp-individual enable force\n"
            + "interface mlag-port-channel 4 lacp-individual enable force\n"
            + "interface mlag-port-channel 5 lacp-individual enable force\n"
            + "interface mlag-port-channel 6 lacp-individual enable force\n"
            + "interface mlag-port-channel 7 lacp-individual enable force\n"
            + "interface mlag-port-channel 8 lacp-individual enable force\n"
            + "interface mlag-port-channel 9 lacp-individual enable force\n"
            + "interface mlag-port-channel 13 lacp-individual enable force\n"
        ) in str(result.output)
        assert (
            'vlan 2 name "RVR_NMN"\n'
            + 'vlan 4 name "RVR_HMN"\n'
            + 'vlan 6 name "CMN"\n'
            + 'vlan 7 name "CAN"\n'
            + 'vlan 4000 name "MLAG"\n'
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 4\n"
        ) in str(result.output)
        assert (
            "interface vlan 1\n"
            + "interface vlan 2\n"
            + "interface vlan 4\n"
            + "interface vlan 6\n"
            + "interface vlan 7\n"
            + "interface vlan 10\n"
            + "interface vlan 4000\n"
            + "interface vlan 1 mtu 9216\n"
            + "interface vlan 2 mtu 9216\n"
            + "interface vlan 4 mtu 9216\n"
            + "interface vlan 6 mtu 9216\n"
            + "interface vlan 7 mtu 9216\n"
            + "interface vlan 4000 mtu 9216\n"
            + "interface vlan 1 ip address 192.168.1.2/16 primary\n"
            + "interface vlan 2 ip address 192.168.3.2/17 primary\n"
            + "interface vlan 4 ip address 192.168.0.2/17 primary\n"
            + "interface vlan 6 ip address 192.168.12.2/24 primary\n"
            + "interface vlan 7 ip address 192.168.11.2/24 primary\n"
            + "interface vlan 4000 ip address 192.168.255.253/30 primary\n"
        ) in str(result.output)
        assert (
            "ip load-sharing source-ip-port\n"
            + "ip load-sharing type consistent\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree port type edge default\n"
            + "spanning-tree priority 4096\n"
            + "spanning-tree mst 1 vlan 1\n"
            + "spanning-tree mst 1 vlan 4\n"
            + "spanning-tree mst 1 vlan 6\n"
            + "spanning-tree mst 1 vlan 7\n"
            + "interface mlag-port-channel 151 spanning-tree port type network\n"
            + "interface mlag-port-channel 151 spanning-tree guard root\n"
            + "interface mlag-port-channel 201 spanning-tree port type network\n"
            + "interface mlag-port-channel 201 spanning-tree guard root\n"
        ) in str(result.output)
        assert (
            "ipv4 access-list nmn-hmn\n"
            + "ipv4 access-list nmn-hmn bind-point rif\n"
            + "  ipv4 access-list nmn-hmn seq 10 deny ip 192.168.3.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 20 deny ip 192.168.0.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 30 deny ip 192.168.3.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 40 deny ip 192.168.0.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 50 deny ip 192.168.100.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 60 deny ip 192.168.100.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 70 deny ip 192.168.200.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 80 deny ip 192.168.200.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 90 permit ip any any\n"
        ) in str(result.output)
        assert (
            "protocol ospf\n"
            + "router ospf 1 vrf default\n"
            + "router ospf 1 vrf default router-id 10.2.0.2\n"
            + "interface vlan 2 ip ospf area 0.0.0.0\n"
            + "interface vlan 4 ip ospf area 0.0.0.0\n"
            + "router ospf 1 vrf default redistribute ibgp\n"
        ) in str(result.output)
        assert (
            "ip dhcp relay instance 2 vrf default\n"
            + "ip dhcp relay instance 4 vrf default\n"
            + "ip dhcp relay instance 2 address 10.92.100.222\n"
            + "ip dhcp relay instance 4 address 10.94.100.222\n"
            + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
            + "interface vlan 7 ip dhcp relay instance 2 downstream\n"
        ) in str(result.output)
        assert (
            "protocol magp\n"
            + "interface vlan 1 magp 1\n"
            + "interface vlan 2 magp 2\n"
            + "interface vlan 4 magp 4\n"
            + "interface vlan 6 magp 6\n"
            + "interface vlan 7 magp 7\n"
            + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
            + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
            + "interface vlan 4 magp 4 ip virtual-router address 192.168.0.1\n"
            + "interface vlan 6 magp 6 ip virtual-router address 192.168.12.1\n"
            + "interface vlan 7 magp 7 ip virtual-router address 192.168.11.1\n"
            + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 4 magp 4 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 6 magp 6 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 7 magp 7 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
            + "no mlag shutdown\n"
            + "mlag system-mac 00:00:5E:00:01:01\n"
            + "interface port-channel 100 ipl 1\n"
            + "interface vlan 4000 ipl 1 peer-address 192.168.255.254\n"
            + "no interface mgmt0 dhcp\n"
            + "interface mgmt0 ip address 192.168.255.241 /29\n"
            + "ntp enable\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


def test_switch_config_spine_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary spine config."""
    spine_secondary = "sw-spine-002"
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
                spine_secondary,
            ],
        )
        assert result.exit_code == 0
        assert (
            "hostname sw-spine-002\n"
            + "no cli default prefix-modes enable\n"
            + "  protocol mlag\n"
            + "  protocol bgp\n"
            + "lacp\n"
            + "interface mlag-port-channel 1\n"
            + "interface mlag-port-channel 2\n"
            + "interface mlag-port-channel 3\n"
            + "interface mlag-port-channel 4\n"
            + "interface mlag-port-channel 5\n"
            + "interface mlag-port-channel 6\n"
            + "interface mlag-port-channel 7\n"
            + "interface mlag-port-channel 8\n"
            + "interface mlag-port-channel 9\n"
            + "interface mlag-port-channel 13\n"
            + "interface mlag-port-channel 151\n"
            + "interface mlag-port-channel 201\n"
            + "interface ethernet 1/1 mtu 9216 force\n"
            + "interface ethernet 1/2 mtu 9216 force\n"
            + "interface ethernet 1/3 mtu 9216 force\n"
            + "interface ethernet 1/4 mtu 9216 force\n"
            + "interface ethernet 1/5 mtu 9216 force\n"
            + "interface ethernet 1/6 mtu 9216 force\n"
            + "interface ethernet 1/7 mtu 9216 force\n"
            + "interface ethernet 1/8 mtu 9216 force\n"
            + "interface ethernet 1/9 mtu 9216 force\n"
            + "interface ethernet 1/13 mtu 9216 force\n"
            + "interface ethernet 1/26 mtu 9216 force\n"
            + "interface ethernet 1/29 mtu 9216 force\n"
            + "interface ethernet 1/30 mtu 9216 force\n"
            + "interface mlag-port-channel 1 mtu 9216 force\n"
            + "interface mlag-port-channel 2 mtu 9216 force\n"
            + "interface mlag-port-channel 3 mtu 9216 force\n"
            + "interface mlag-port-channel 4 mtu 9216 force\n"
            + "interface mlag-port-channel 5 mtu 9216 force\n"
            + "interface mlag-port-channel 6 mtu 9216 force\n"
            + "interface mlag-port-channel 7 mtu 9216 force\n"
            + "interface mlag-port-channel 8 mtu 9216 force\n"
            + "interface mlag-port-channel 9 mtu 9216 force\n"
            + "interface mlag-port-channel 13 mtu 9216 force\n"
            + "interface mlag-port-channel 151 mtu 9216 force\n"
            + "interface mlag-port-channel 201 mtu 9216 force\n"
            + "interface ethernet 1/1 mlag-channel-group 1 mode active\n"
            + "interface ethernet 1/2 mlag-channel-group 2 mode active\n"
            + "interface ethernet 1/3 mlag-channel-group 3 mode active\n"
            + "interface ethernet 1/4 mlag-channel-group 4 mode active\n"
            + "interface ethernet 1/5 mlag-channel-group 5 mode active\n"
            + "interface ethernet 1/6 mlag-channel-group 6 mode active\n"
            + "interface ethernet 1/7 mlag-channel-group 7 mode active\n"
            + "interface ethernet 1/8 mlag-channel-group 8 mode active\n"
            + "interface ethernet 1/9 mlag-channel-group 9 mode active\n"
            + "interface ethernet 1/13 mlag-channel-group 13 mode active\n"
            + "interface ethernet 1/26 mlag-channel-group 151 mode active\n"
            + "interface ethernet 1/29 mlag-channel-group 201 mode active\n"
            + "interface ethernet 1/30 mlag-channel-group 201 mode active\n"
            + "interface mlag-port-channel 1 switchport mode hybrid\n"
            + "interface mlag-port-channel 2 switchport mode hybrid\n"
            + "interface mlag-port-channel 3 switchport mode hybrid\n"
            + "interface mlag-port-channel 4 switchport mode hybrid\n"
            + "interface mlag-port-channel 5 switchport mode hybrid\n"
            + "interface mlag-port-channel 6 switchport mode hybrid\n"
            + "interface mlag-port-channel 7 switchport mode hybrid\n"
            + "interface mlag-port-channel 8 switchport mode hybrid\n"
            + "interface mlag-port-channel 9 switchport mode hybrid\n"
            + "interface mlag-port-channel 13 switchport mode hybrid\n"
            + "interface mlag-port-channel 151 switchport mode hybrid\n"
            + "interface mlag-port-channel 201 switchport mode hybrid\n"
            + "interface ethernet 1/1 description sw-spine-002:1==>ncn-m001:pcie-slot1:2\n"
            + "interface ethernet 1/2 description sw-spine-002:2==>ncn-m002:pcie-slot1:2\n"
            + "interface ethernet 1/3 description sw-spine-002:3==>ncn-m003:pcie-slot1:2\n"
            + "interface ethernet 1/4 description sw-spine-002:4==>ncn-w001:pcie-slot1:2\n"
            + "interface ethernet 1/5 description sw-spine-002:5==>ncn-w002:pcie-slot1:2\n"
            + "interface ethernet 1/6 description sw-spine-002:6==>ncn-w003:pcie-slot1:2\n"
            + "interface ethernet 1/7 description sw-spine-002:7==>ncn-s001:pcie-slot1:2\n"
            + "interface ethernet 1/8 description sw-spine-002:8==>ncn-s002:pcie-slot1:2\n"
            + "interface ethernet 1/9 description sw-spine-002:9==>ncn-s003:pcie-slot1:2\n"
            + "interface ethernet 1/13 description sw-spine-002:13==>uan001:pcie-slot1:2\n"
            + "interface ethernet 1/26 description sw-spine-002:26==>sw-leaf-bmc-001:52\n"
            + "interface ethernet 1/29 description sw-spine-002:29==>sw-cdu-001:28\n"
            + "interface ethernet 1/30 description sw-spine-002:30==>sw-cdu-002:28\n"
            + "interface ethernet 1/31 description mlag-isl\n"
            + "interface ethernet 1/32 description mlag-isl\n"
            + "interface mlag-port-channel 1 description sw-spine-002:1==>ncn-m001:pcie-slot1:2\n"
            + "interface mlag-port-channel 2 description sw-spine-002:2==>ncn-m002:pcie-slot1:2\n"
            + "interface mlag-port-channel 3 description sw-spine-002:3==>ncn-m003:pcie-slot1:2\n"
            + "interface mlag-port-channel 4 description sw-spine-002:4==>ncn-w001:pcie-slot1:2\n"
            + "interface mlag-port-channel 5 description sw-spine-002:5==>ncn-w002:pcie-slot1:2\n"
            + "interface mlag-port-channel 6 description sw-spine-002:6==>ncn-w003:pcie-slot1:2\n"
            + "interface mlag-port-channel 7 description sw-spine-002:7==>ncn-s001:pcie-slot1:2\n"
            + "interface mlag-port-channel 8 description sw-spine-002:8==>ncn-s002:pcie-slot1:2\n"
            + "interface mlag-port-channel 9 description sw-spine-002:9==>ncn-s003:pcie-slot1:2\n"
            + "interface mlag-port-channel 13 description sw-spine-002:13==>uan001:pcie-slot1:2\n"
            + "interface mlag-port-channel 151 description sw-spine-002:26==>sw-leaf-bmc-001:52\n"
            + "interface mlag-port-channel 201 description sw-spine-002:29==>sw-cdu-001:28\n"
            + "interface mlag-port-channel 201 description sw-spine-002:30==>sw-cdu-002:28\n"
        ) in str(result.output)
        assert (
            "interface port-channel 100\n"
            + "interface ethernet 1/31 channel-group 100 mode active\n"
            + "interface ethernet 1/32 channel-group 100 mode active\n"
            + "interface port-channel 100 description mlag-isl\n"
            + "port-channel load-balance ethernet source-destination-ip ingress-port\n"
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 no shutdown\n"
            + "interface mlag-port-channel 2 no shutdown\n"
            + "interface mlag-port-channel 3 no shutdown\n"
            + "interface mlag-port-channel 4 no shutdown\n"
            + "interface mlag-port-channel 5 no shutdown\n"
            + "interface mlag-port-channel 6 no shutdown\n"
            + "interface mlag-port-channel 7 no shutdown\n"
            + "interface mlag-port-channel 8 no shutdown\n"
            + "interface mlag-port-channel 9 no shutdown\n"
            + "interface mlag-port-channel 13 no shutdown\n"
            + "interface mlag-port-channel 151 no shutdown\n"
            + "interface mlag-port-channel 201 no shutdown\n"
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 lacp-individual enable force\n"
            + "interface mlag-port-channel 2 lacp-individual enable force\n"
            + "interface mlag-port-channel 3 lacp-individual enable force\n"
            + "interface mlag-port-channel 4 lacp-individual enable force\n"
            + "interface mlag-port-channel 5 lacp-individual enable force\n"
            + "interface mlag-port-channel 6 lacp-individual enable force\n"
            + "interface mlag-port-channel 7 lacp-individual enable force\n"
            + "interface mlag-port-channel 8 lacp-individual enable force\n"
            + "interface mlag-port-channel 9 lacp-individual enable force\n"
            + "interface mlag-port-channel 13 lacp-individual enable force\n"
        ) in str(result.output)
        assert (
            'vlan 2 name "RVR_NMN"\n'
            + 'vlan 4 name "RVR_HMN"\n'
            + 'vlan 6 name "CMN"\n'
            + 'vlan 7 name "CAN"\n'
            + 'vlan 4000 name "MLAG"\n'
        ) in str(result.output)
        assert (
            "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 4\n"
        ) in str(result.output)
        assert (
            "interface vlan 1\n"
            + "interface vlan 2\n"
            + "interface vlan 4\n"
            + "interface vlan 6\n"
            + "interface vlan 7\n"
            + "interface vlan 10\n"
            + "interface vlan 4000\n"
            + "interface vlan 1 mtu 9216\n"
            + "interface vlan 2 mtu 9216\n"
            + "interface vlan 4 mtu 9216\n"
            + "interface vlan 6 mtu 9216\n"
            + "interface vlan 7 mtu 9216\n"
            + "interface vlan 4000 mtu 9216\n"
            + "interface vlan 1 ip address 192.168.1.3/16 primary\n"
            + "interface vlan 2 ip address 192.168.3.3/17 primary\n"
            + "interface vlan 4 ip address 192.168.0.3/17 primary\n"
            + "interface vlan 6 ip address 192.168.12.3/24 primary\n"
            + "interface vlan 7 ip address 192.168.11.3/24 primary\n"
            + "interface vlan 4000 ip address 192.168.255.254/30 primary\n"
        ) in str(result.output)
        assert (
            "ip load-sharing source-ip-port\n"
            + "ip load-sharing type consistent\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree port type edge default\n"
            + "spanning-tree priority 4096\n"
            + "spanning-tree mst 1 vlan 1\n"
            + "spanning-tree mst 1 vlan 4\n"
            + "spanning-tree mst 1 vlan 6\n"
            + "spanning-tree mst 1 vlan 7\n"
            + "interface mlag-port-channel 151 spanning-tree port type network\n"
            + "interface mlag-port-channel 151 spanning-tree guard root\n"
            + "interface mlag-port-channel 201 spanning-tree port type network\n"
            + "interface mlag-port-channel 201 spanning-tree guard root\n"
        ) in str(result.output)
        assert (
            "ipv4 access-list nmn-hmn\n"
            + "ipv4 access-list nmn-hmn bind-point rif\n"
            + "  ipv4 access-list nmn-hmn seq 10 deny ip 192.168.3.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 20 deny ip 192.168.0.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 30 deny ip 192.168.3.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 40 deny ip 192.168.0.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 50 deny ip 192.168.100.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 60 deny ip 192.168.100.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 70 deny ip 192.168.200.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 80 deny ip 192.168.200.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "  ipv4 access-list nmn-hmn seq 90 permit ip any any\n"
        ) in str(result.output)
        assert (
            "protocol ospf\n"
            + "router ospf 1 vrf default\n"
            + "router ospf 1 vrf default router-id 10.2.0.3\n"
            + "interface vlan 2 ip ospf area 0.0.0.0\n"
            + "interface vlan 4 ip ospf area 0.0.0.0\n"
            + "router ospf 1 vrf default redistribute ibgp\n"
        ) in str(result.output)
        assert (
            "ip dhcp relay instance 2 vrf default\n"
            + "ip dhcp relay instance 4 vrf default\n"
            + "ip dhcp relay instance 2 address 10.92.100.222\n"
            + "ip dhcp relay instance 4 address 10.94.100.222\n"
            + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
            + "interface vlan 7 ip dhcp relay instance 2 downstream\n"
        ) in str(result.output)
        assert (
            "protocol magp\n"
            + "interface vlan 1 magp 1\n"
            + "interface vlan 2 magp 2\n"
            + "interface vlan 4 magp 4\n"
            + "interface vlan 6 magp 6\n"
            + "interface vlan 7 magp 7\n"
            + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
            + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
            + "interface vlan 4 magp 4 ip virtual-router address 192.168.0.1\n"
            + "interface vlan 6 magp 6 ip virtual-router address 192.168.12.1\n"
            + "interface vlan 7 magp 7 ip virtual-router address 192.168.11.1\n"
            + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 4 magp 4 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 6 magp 6 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 7 magp 7 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
            + "no mlag shutdown\n"
            + "mlag system-mac 00:00:5E:00:01:01\n"
            + "interface port-channel 100 ipl 1\n"
            + "interface vlan 4000 ipl 1 peer-address 192.168.255.253\n"
            + "no interface mgmt0 dhcp\n"
            + "interface mgmt0 ip address 192.168.255.243 /29\n"
            + "ntp enable\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


def test_switch_config_leaf_bmc():
    """Test that the `canu generate switch config` command runs and returns valid leaf-bmc config."""
    leaf_bmc = "sw-leaf-bmc-001"

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
                leaf_bmc,
            ],
        )
        assert result.exit_code == 0
        assert (
            "ip name-server 10.92.100.225\n"
            + "hostname sw-leaf-bmc-001\n"
            + "rest api restconf\n"
        ) in str(result.output)
        assert (
            "interface vlan1\n"
            + "  Description MTL\n"
            + "  no shutdown\n"
            + "  ip address 192.168.1.12/16\n"
            + "interface vlan2\n"
            + "  description RIVER_NMN\n"
            + "  no shutdown\n"
            + "  ip address 192.168.3.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface vlan4\n"
            + "  description RIVER_HMN\n"
            + "  no shutdown\n"
            + "  ip address 192.168.0.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
        ) in str(result.output)
        assert (
            "interface port-channel100\n"
            + "  description sw-leaf-bmc-001:51==>sw-spine-001:26\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4\n"
            + "  mtu 9216\n"
        ) in str(result.output)
        assert (
            "interface loopback 0\n"
            + "  ip address 10.2.0.12/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  shutdown\n"
            + "  ip address dhcp\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet 1/1/51\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/52\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/1\n"
            + "  description sw-leaf-bmc-001:1==>ncn-m001:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/2\n"
            + "  description sw-leaf-bmc-001:2==>ncn-m002:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/3\n"
            + "  description sw-leaf-bmc-001:3==>ncn-m003:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/4\n"
            + "  description sw-leaf-bmc-001:4==>ncn-w001:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/5\n"
            + "  description sw-leaf-bmc-001:5==>ncn-w002:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/6\n"
            + "  description sw-leaf-bmc-001:6==>ncn-w003:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/7\n"
            + "  description sw-leaf-bmc-001:7==>ncn-s001:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/8\n"
            + "  description sw-leaf-bmc-001:8==>ncn-s002:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/9\n"
            + "  description sw-leaf-bmc-001:9==>ncn-s003:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet 1/1/10\n"
            + "  description sw-leaf-bmc-001:10==>uan001:bmc:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
        ) in str(result.output)

        assert (
            "ip access-list nmn-hmn\n"
            + "  seq 10 deny ip 192.168.3.0/17 192.168.0.0/17\n"
            + "  seq 20 deny ip 192.168.0.0/17 192.168.3.0/17\n"
            + "  seq 30 deny ip 192.168.3.0/17 192.168.200.0/17\n"
            + "  seq 40 deny ip 192.168.0.0/17 192.168.100.0/17\n"
            + "  seq 50 deny ip 192.168.100.0/17 192.168.0.0/17\n"
            + "  seq 60 deny ip 192.168.100.0/17 192.168.200.0/17\n"
            + "  seq 70 deny ip 192.168.200.0/17 192.168.3.0/17\n"
            + "  seq 80 deny ip 192.168.200.0/17 192.168.100.0/17\n"
            + "  seq 90 permit ip any any\n"
        ) in str(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.12\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  instance 1 vlan 1-4093\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


def test_switch_config_cdu_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary cdu config."""
    cdu_primary = "sw-cdu-001"

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
                cdu_primary,
            ],
        )
        assert result.exit_code == 0
        assert (
            "ip name-server 10.92.100.225\n"
            + "hostname sw-cdu-001\n"
            + "rest api restconf\n"
        ) in str(result.output)
        assert (
            "interface vlan3000\n"
            + "  mode L3\n"
            + "  description cabinet_3002\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.104.2/22\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "  ip helper-address 10.94.100.222\n"
            + "  vrrp-group 30\n"
            + "    virtual-address 192.168.104.1\n"
            + "    priority 110\n"
            + "interface vlan2000\n"
            + "  mode L3\n"
            + "  description cabinet_3002\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.100.2/22\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "  ip helper-address 10.92.100.222\n"
            + "  vrrp-group 20\n"
            + "    virtual-address 192.168.100.1\n"
            + "    priority 110\n"
        ) in str(result.output)
        assert (
            "interface vlan1\n"
            + "  Description MTL\n"
            + "  no shutdown\n"
            + "  ip address 192.168.1.16/16\n"
            + "interface vlan2\n"
            + "  description RIVER_NMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.3.16/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface vlan4\n"
            + "  description RIVER_HMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.0.16/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
        ) in str(result.output)
        assert (
            "interface port-channel2\n"
            + "  description sw-cdu-001:2==>cmm-x3002-000:1\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 2\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel3\n"
            + "  description sw-cdu-001:3==>cmm-x3002-001:1\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 3\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel4\n"
            + "  description sw-cdu-001:4==>cmm-x3002-002:1\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 4\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel5\n"
            + "  description sw-cdu-001:5==>cmm-x3002-003:1\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 5\n"
            + "  spanning-tree guard root\n"
        ) in str(result.output)
        assert (
            "interface port-channel100\n"
            + "  description sw-cdu-001:27==>sw-spine-001:29\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 100\n"
            + "interface loopback 0\n"
            + "  ip address 10.2.0.16/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  no shutdown\n"
            + "  dhcp\n"
            + "  ip address 192.168.255.242/29\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/2\n"
            + "  description sw-cdu-001:2==>cmm-x3002-000:1\n"
            + "  no shutdown\n"
            + "  channel-group 2\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/3\n"
            + "  description sw-cdu-001:3==>cmm-x3002-001:1\n"
            + "  no shutdown\n"
            + "  channel-group 3\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/4\n"
            + "  description sw-cdu-001:4==>cmm-x3002-002:1\n"
            + "  no shutdown\n"
            + "  channel-group 4\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/5\n"
            + "  description sw-cdu-001:5==>cmm-x3002-003:1\n"
            + "  no shutdown\n"
            + "  channel-group 5\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/1\n"
            + "  description sw-cdu-001:1==>cec-x3002-000:1\n"
            + "  no shutdown\n"
            + "  switchport access vlan 3000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/27\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/28\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/25\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/26\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
        ) in str(result.output)
        assert (
            "ip access-list nmn-hmn\n"
            + "  seq 10 deny ip 192.168.3.0/17 192.168.0.0/17\n"
            + "  seq 20 deny ip 192.168.0.0/17 192.168.3.0/17\n"
            + "  seq 30 deny ip 192.168.3.0/17 192.168.200.0/17\n"
            + "  seq 40 deny ip 192.168.0.0/17 192.168.100.0/17\n"
            + "  seq 50 deny ip 192.168.100.0/17 192.168.0.0/17\n"
            + "  seq 60 deny ip 192.168.100.0/17 192.168.200.0/17\n"
            + "  seq 70 deny ip 192.168.200.0/17 192.168.3.0/17\n"
            + "  seq 80 deny ip 192.168.200.0/17 192.168.100.0/17\n"
            + "  seq 90 permit ip any any\n"
        ) in str(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.16\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  instance 1 vlan 1-4093\n"
            + "vlt-domain 1\n"
            + "  backup destination 192.168.255.243\n"
            + "  discovery-interface ethernet1/1/25,1/1/26\n"
            + "  peer-routing\n"
            + "  primary-priority 4096\n"
            + "  vlt-mac 00:11:22:aa:bb:cc\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


def test_switch_config_cdu_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary cdu config."""
    cdu_secondary = "sw-cdu-002"

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
                cdu_secondary,
            ],
        )
        assert result.exit_code == 0
        assert (
            "ip name-server 10.92.100.225\n"
            + "hostname sw-cdu-002\n"
            + "rest api restconf\n"
        ) in str(result.output)
        assert (
            "interface vlan3000\n"
            + "  mode L3\n"
            + "  description cabinet_3002\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.104.3/22\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "  ip helper-address 10.94.100.222\n"
            + "  vrrp-group 30\n"
            + "    virtual-address 192.168.104.1\n"
            + "    priority 90\n"
            + "interface vlan2000\n"
            + "  mode L3\n"
            + "  description cabinet_3002\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.100.3/22\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "  ip helper-address 10.92.100.222\n"
            + "  vrrp-group 20\n"
            + "    virtual-address 192.168.100.1\n"
            + "    priority 90\n"
        ) in str(result.output)
        assert (
            "interface vlan1\n"
            + "  Description MTL\n"
            + "  no shutdown\n"
            + "  ip address 192.168.1.17/16\n"
            + "interface vlan2\n"
            + "  description RIVER_NMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.3.17/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface vlan4\n"
            + "  description RIVER_HMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.0.17/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
        ) in str(result.output)
        assert (
            "interface port-channel2\n"
            + "  description sw-cdu-002:2==>cmm-x3002-000:2\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 2\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel3\n"
            + "  description sw-cdu-002:3==>cmm-x3002-001:2\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 3\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel4\n"
            + "  description sw-cdu-002:4==>cmm-x3002-002:2\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 4\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel5\n"
            + "  description sw-cdu-002:5==>cmm-x3002-003:2\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 5\n"
            + "  spanning-tree guard root\n"
        ) in str(result.output)
        assert (
            "interface port-channel100\n"
            + "  description sw-cdu-002:27==>sw-spine-001:30\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 100\n"
            + "interface loopback 0\n"
            + "  ip address 10.2.0.17/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  no shutdown\n"
            + "  dhcp\n"
            + "  ip address 192.168.255.243/29\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/2\n"
            + "  description sw-cdu-002:2==>cmm-x3002-000:2\n"
            + "  no shutdown\n"
            + "  channel-group 2\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/3\n"
            + "  description sw-cdu-002:3==>cmm-x3002-001:2\n"
            + "  no shutdown\n"
            + "  channel-group 3\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/4\n"
            + "  description sw-cdu-002:4==>cmm-x3002-002:2\n"
            + "  no shutdown\n"
            + "  channel-group 4\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/5\n"
            + "  description sw-cdu-002:5==>cmm-x3002-003:2\n"
            + "  no shutdown\n"
            + "  channel-group 5\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/27\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/28\n"
            + "  no shutdown\n"
            + "  channel-group 100 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/25\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet 1/1/26\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
        ) in str(result.output)
        assert (
            "ip access-list nmn-hmn\n"
            + "  seq 10 deny ip 192.168.3.0/17 192.168.0.0/17\n"
            + "  seq 20 deny ip 192.168.0.0/17 192.168.3.0/17\n"
            + "  seq 30 deny ip 192.168.3.0/17 192.168.200.0/17\n"
            + "  seq 40 deny ip 192.168.0.0/17 192.168.100.0/17\n"
            + "  seq 50 deny ip 192.168.100.0/17 192.168.0.0/17\n"
            + "  seq 60 deny ip 192.168.100.0/17 192.168.200.0/17\n"
            + "  seq 70 deny ip 192.168.200.0/17 192.168.3.0/17\n"
            + "  seq 80 deny ip 192.168.200.0/17 192.168.100.0/17\n"
            + "  seq 90 permit ip any any\n"
        ) in str(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.17\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  instance 1 vlan 1-4093\n"
            + "vlt-domain 1\n"
            + "  backup destination 192.168.255.242\n"
            + "  discovery-interface ethernet1/1/25,1/1/26\n"
            + "  peer-routing\n"
            + "  primary-priority 8192\n"
            + "  vlt-mac 00:11:22:aa:bb:cc\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


sls_input = {
    "Networks": {
        "CAN": {
            "Name": "CAN",
            "ExtraProperties": {
                "CIDR": "192.168.11.0/24",
                "Subnets": [
                    {
                        "Name": "bootstrap_dhcp",
                        "CIDR": "192.168.11.0/24",
                        "IPReservations": [
                            {"Name": "can-switch-1", "IPAddress": "192.168.11.2"},
                            {"Name": "can-switch-2", "IPAddress": "192.168.11.3"},
                        ],
                        "VlanID": 7,
                        "Gateway": "192.168.11.1",
                    },
                ],
            },
        },
        "CMN": {
            "Name": "CMN",
            "ExtraProperties": {
                "CIDR": "192.168.12.0/24",
                "Subnets": [
                    {
                        "Name": "bootstrap_dhcp",
                        "CIDR": "192.168.12.0/24",
                        "IPReservations": [
                            {"Name": "cmn-switch-1", "IPAddress": "192.168.12.2"},
                            {"Name": "cmn-switch-2", "IPAddress": "192.168.12.3"},
                        ],
                        "VlanID": 6,
                        "Gateway": "192.168.12.1",
                    },
                ],
            },
        },
        "HMN": {
            "Name": "HMN",
            "ExtraProperties": {
                "CIDR": "192.168.0.0/17",
                "Subnets": [
                    {
                        "Name": "network_hardware",
                        "CIDR": "192.168.0.0/17",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.0.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.0.3"},
                            {"Name": "sw-leaf-bmc-001", "IPAddress": "192.168.0.12"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.0.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.0.17"},
                        ],
                        "VlanID": 4,
                        "Gateway": "192.168.0.1",
                    },
                ],
            },
        },
        "MTL": {
            "Name": "MTL",
            "ExtraProperties": {
                "CIDR": "192.168.1.0/16",
                "Subnets": [
                    {
                        "Name": "network_hardware",
                        "CIDR": "192.168.1.0/16",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.1.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.1.3"},
                            {"Name": "sw-leaf-bmc-001", "IPAddress": "192.168.1.12"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.1.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.1.17"},
                        ],
                        "VlanID": 0,
                        "Gateway": "192.168.1.1",
                    },
                ],
            },
        },
        "NMN": {
            "Name": "NMN",
            "FullName": "Node Management Network",
            "ExtraProperties": {
                "CIDR": "192.168.3.0/17",
                "Subnets": [
                    {
                        "FullName": "NMN Management Network Infrastructure",
                        "CIDR": "192.168.3.0/17",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.3.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.3.3"},
                            {"Name": "sw-leaf-bmc-001", "IPAddress": "192.168.3.12"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.3.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.3.17"},
                        ],
                        "Name": "network_hardware",
                        "VlanID": 2,
                        "Gateway": "192.168.3.1",
                    },
                    {
                        "FullName": "NMN Bootstrap DHCP Subnet",
                        "CIDR": "192.168.4.0/17",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.4.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.4.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.4.6"},
                        ],
                        "Name": "bootstrap_dhcp",
                        "VlanID": 2,
                        "Gateway": "192.168.3.1",
                    },
                ],
            },
        },
        "NMN_MTN": {
            "Name": "NMN_MTN",
            "ExtraProperties": {
                "CIDR": "192.168.100.0/17",
                "Subnets": [
                    {
                        "FullName": "",
                        "CIDR": "192.168.100.0/22",
                        "Name": "cabinet_3002",
                        "VlanID": 2000,
                        "Gateway": "192.168.100.1",
                        "DHCPStart": "192.168.100.10",
                        "DHCPEnd": "192.168.3.254",
                    },
                ],
            },
        },
        "HMN_MTN": {
            "Name": "HMN_MTN",
            "ExtraProperties": {
                "CIDR": "192.168.200.0/17",
                "Subnets": [
                    {
                        "FullName": "",
                        "CIDR": "192.168.104.0/22",
                        "Name": "cabinet_3002",
                        "VlanID": 3000,
                        "Gateway": "192.168.104.1",
                        "DHCPStart": "192.168.104.10",
                        "DHCPEnd": "192.168.104.254",
                    },
                ],
            },
        },
    },
}
sls_networks = [
    network[x] for network in [sls_input.get("Networks", {})] for x in network
]
