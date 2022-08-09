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
"""Test CANU generate switch config commands."""
import json
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Architecture_Golden_Config_Dellanox.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
custom_file_name = "dellanox_custom.yaml"
custom_file = path.join(test_file_directory, "data", custom_file_name)
architecture = "v1"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T30,J14,T34,J14,T28,J14,T27"
sls_file = "sls_file.json"
csm = "1.2"
switch_name = "sw-spine-001"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

canu_version_file = path.join(test_file_directory.resolve().parent, "canu", ".version")
with open(canu_version_file, "r") as file:
    canu_version = file.readline()
canu_version = canu_version.strip()
banner_motd = (
    'banner motd "\n'
    "###############################################################################\n"
    f"# CSM version:  {csm}\n"
    f"# CANU version: {canu_version}\n"
    "###############################################################################\n"
    '"\n'
)

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
        print(result.output)
        assert (
            "hostname sw-spine-001\n"
            + "no cli default prefix-modes enable\n"
            + "protocol mlag\n"
            + "protocol bgp\n"
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
            + "interface ethernet 1/31 speed 40G force\n"
            + "interface ethernet 1/32 speed 40G force\n"
            + "interface ethernet 1/1 speed 40G force\n"
            + "interface ethernet 1/2 speed 40G force\n"
            + "interface ethernet 1/3 speed 40G force\n"
            + "interface ethernet 1/4 speed 40G force\n"
            + "interface ethernet 1/5 speed 40G force\n"
            + "interface ethernet 1/6 speed 40G force\n"
            + "interface ethernet 1/7 speed 40G force\n"
            + "interface ethernet 1/8 speed 40G force\n"
            + "interface ethernet 1/9 speed 40G force\n"
            + "interface ethernet 1/13 speed 40G force\n"
            + "interface ethernet 1/26 speed 10G force\n"
            + "interface ethernet 1/29 speed 40G force\n"
            + "interface ethernet 1/30 speed 40G force\n"
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
            + 'interface ethernet 1/1 description "ncn-m001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/2 description "ncn-m002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/3 description "ncn-m003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/4 description "ncn-w001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/5 description "ncn-w002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/6 description "ncn-w003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/7 description "ncn-s001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/8 description "ncn-s002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/9 description "ncn-s003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/13 description "uan001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/26 description "sw-leaf-bmc-001:51<==sw-spine-001"\n'
            + 'interface ethernet 1/29 description "sw-cdu-001:27<==sw-spine-001"\n'
            + 'interface ethernet 1/30 description "sw-cdu-002:27<==sw-spine-001"\n'
            + 'interface ethernet 1/31 description "mlag-isl"\n'
            + 'interface ethernet 1/32 description "mlag-isl"\n'
            + 'interface mlag-port-channel 1 description "ncn-m001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 2 description "ncn-m002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 3 description "ncn-m003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 4 description "ncn-w001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 5 description "ncn-w002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 6 description "ncn-w003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 7 description "ncn-s001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 8 description "ncn-s002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 9 description "ncn-s003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 13 description "uan001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 151 description "sw-leaf-bmc-001:51<==sw-spine-001"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-001:27<==sw-spine-001"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-002:27<==sw-spine-001"\n'
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel 256\n"
            + "interface ethernet 1/31 channel-group 256 mode active\n"
            + "interface ethernet 1/32 channel-group 256 mode active\n"
            + 'interface port-channel 256 description "mlag-isl"\n'
            + "interface port-channel 256 dcb priority-flow-control mode on force\n"
        ) in str(result.output)
        print(result.output)
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
        print(result.output)
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
        ) in str(result.output)
        print(result.output)
        assert (
            "vlan 2\n"
            + "vlan 4\n"
            + "vlan 6\n"
            + "vlan 4000\n"
            + 'vlan 2 name "RVR_NMN"\n'
            + 'vlan 4 name "RVR_HMN"\n'
            + 'vlan 6 name "CMN"\n'
            + 'vlan 4000 name "MLAG"\n'
            + "vlan 7\n"
            + 'vlan 7 name "CAN"\n'
        ) in str(result.output)
        print(result.output)
        assert (
            "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 6\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "web vrf default enable\n"
            + "vrf definition Customer\n"
            + "vrf definition Customer rd 7:7\n"
            + "ip routing vrf Customer\n"
            + "ip routing vrf default\n"
            + "ip name-server vrf vrf-default 10.92.100.225\n"
            + "no ldap vrf mgmt enable\n"
            + "no radius-server vrf mgmt enable\n"
            + "no snmp-server vrf mgmt enable\n"
            + "no tacacs-server vrf mgmt enable\n"
            + "vrf definition mgmt\n"
            + "interface loopback 0\n"
            + "interface loopback 0 ip address 10.2.0.2/32 primary\n"
            + "interface vlan 7 vrf forwarding Customer\n"
            + "interface vlan 7 ip address 192.168.11.2/24 primary\n"
            + "no interface vlan 7 ip icmp redirect\n"
            + "interface vlan 7 mtu 9184\n"
            + "interface vlan 1\n"
            + "interface vlan 2\n"
            + "interface vlan 4\n"
            + "interface vlan 6 vrf forwarding Customer\n"
            + "interface vlan 10\n"
            + "interface vlan 4000\n"
            + "interface vlan 1 ip address 192.168.1.2/16 primary\n"
            + "interface vlan 2 ip address 192.168.3.2/17 primary\n"
            + "interface vlan 4 ip address 192.168.0.2/17 primary\n"
            + "interface vlan 6 ip address 192.168.12.2/24 primary\n"
            + "interface vlan 4000 ip address 192.168.255.253/30 primary\n"
            + "no interface vlan 1 ip icmp redirect\n"
            + "interface vlan 1 mtu 9184\n"
            + "no interface vlan 2 ip icmp redirect\n"
            + "interface vlan 2 mtu 9184\n"
            + "no interface vlan 4 ip icmp redirect\n"
            + "interface vlan 4 mtu 9184\n"
            + "no interface vlan 6 ip icmp redirect\n"
            + "interface vlan 6 mtu 9184\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "ip load-sharing source-ip-port\n"
            + "ip load-sharing type consistent\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree priority 4096\n"
            + "spanning-tree port type edge default\n"
            + "spanning-tree mst name cray\n"
            + "spanning-tree mst revision 2\n"
            + "interface mlag-port-channel 151 spanning-tree port type network\n"
            + "interface mlag-port-channel 151 spanning-tree guard root\n"
            + "interface mlag-port-channel 201 spanning-tree port type network\n"
            + "interface mlag-port-channel 201 spanning-tree guard root\n"
        ) in str(result.output)
        print(result.output)
        print(result.output)
        assert (
            "ipv4 access-list nmn-hmn\n"
            + "ipv4 access-list nmn-hmn bind-point rif\n"
            + "ipv4 access-list nmn-hmn seq-number 10 deny ip 192.168.3.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 20 deny ip 192.168.0.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 30 deny ip 192.168.3.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 40 deny ip 192.168.0.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 50 deny ip 192.168.100.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 60 deny ip 192.168.100.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 70 deny ip 192.168.200.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 80 deny ip 192.168.200.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 90 permit ip any any\n"
            + "ipv4 access-list cmn-can\n"
            + "ipv4 access-list cmn-can bind-point rif\n"
            + "ipv4 access-list cmn-can seq-number 10 deny ip 192.168.12.0 mask 255.255.255.0 192.168.11.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 20 deny ip 192.168.11.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 30 deny ip 192.168.12.0 mask 255.255.255.0 192.168.200.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 40 deny ip 192.168.200.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 50 permit ip any any\n"
            + "interface vlan 2 ipv4 port access-group nmn-hmn\n"
            + "interface vlan 4 ipv4 port access-group nmn-hmn\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "protocol ospf\n"
            + "router ospf 1 vrf default\n"
            + "router ospf 2 vrf Customer\n"
            + "router ospf 1 vrf default router-id 10.2.0.2\n"
            + "router ospf 2 vrf Customer router-id 10.2.0.2\n"
            + "router ospf 2 vrf Customer default-information originate\n"
            + "interface loopback 0 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf area 0.0.0.0\n"
            + "interface vlan 2 ip ospf area 0.0.0.0\n"
            + "interface vlan 4 ip ospf area 0.0.0.0\n"
            + "interface vlan 6 ip ospf area 0.0.0.0\n"
            + "interface vlan 7 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf passive-interface\n"
            + "interface vlan 4 ip ospf passive-interface\n"
            + "router ospf 1 vrf default redistribute bgp\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "ip dhcp relay instance 2 vrf default\n"
            + "ip dhcp relay instance 4 vrf default\n"
            + "ip dhcp relay instance 2 address 10.92.100.222\n"
            + "ip dhcp relay instance 4 address 10.94.100.222\n"
            + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "protocol magp\n"
            + "interface vlan 1 magp 1\n"
            + "interface vlan 2 magp 2\n"
            + "interface vlan 4 magp 3\n"
            + "interface vlan 6 magp 4\n"
            + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
            + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
            + "interface vlan 4 magp 3 ip virtual-router address 192.168.0.1\n"
            + "interface vlan 6 magp 4 ip virtual-router address 192.168.12.1\n"
            + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:02\n"
            + "interface vlan 4 magp 3 ip virtual-router mac-address 00:00:5E:00:01:03\n"
            + "interface vlan 6 magp 4 ip virtual-router mac-address 00:00:5E:00:01:04\n"
            + "interface vlan 7 magp 5\n"
            + "interface vlan 7 magp 5 ip virtual-router address 192.168.11.1\n"
            + "interface vlan 7 magp 5 ip virtual-router mac-address 00:00:5E:00:01:05\n"
            + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
            + "no mlag shutdown\n"
            + "mlag system-mac 00:00:5E:00:01:01\n"
            + "interface port-channel 256 ipl 1\n"
            + "interface vlan 4000 ipl 1 peer-address 192.168.255.254\n"
            + "no interface mgmt0 dhcp\n"
            + "interface mgmt0 ip address 192.168.255.241 /29\n"
            + "ip prefix-list pl-cmn\n"
            + "ip prefix-list pl-cmn bulk-mode\n"
            + "ip prefix-list pl-cmn seq 10 permit 192.168.12.0 /24 ge 24\n"
            + "ip prefix-list pl-cmn commit\n"
            + "ip prefix-list pl-can\n"
            + "ip prefix-list pl-can bulk-mode\n"
            + "ip prefix-list pl-can seq 10 permit 192.168.11.0 /24 ge 24\n"
            + "ip prefix-list pl-can commit\n"
            + "ip prefix-list pl-hmn\n"
            + "ip prefix-list pl-hmn bulk-mode\n"
            + "ip prefix-list pl-hmn seq 20 permit 10.94.100.0 /24 ge 24\n"
            + "ip prefix-list pl-hmn commit\n"
            + "ip prefix-list pl-nmn\n"
            + "ip prefix-list pl-nmn bulk-mode\n"
            + "ip prefix-list pl-nmn seq 30 permit 10.92.100.0 /24 ge 24\n"
            + "ip prefix-list pl-nmn commit\n"
            + "route-map ncn-w001-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w001-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w001-Customer permit 20 set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w001 permit 10 set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w001 permit 20 set ip next-hop 192.168.4.4\n"
            + "route-map ncn-w002-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w002-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w002-Customer permit 20 set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w002 permit 10 set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w002 permit 20 set ip next-hop 192.168.4.5\n"
            + "route-map ncn-w003-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w003-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w003-Customer permit 20 set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w003 permit 10 set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w003 permit 20 set ip next-hop 192.168.4.6\n"
            + "router bgp 65533 vrf Customer\n"
            + "router bgp 65533 vrf default\n"
            + "router bgp 65533 vrf Customer router-id 10.2.0.2 force\n"
            + "router bgp 65533 vrf default router-id 10.2.0.2 force\n"
            + "router bgp 65533 vrf Customer distance 20 70 20\n"
            + "router bgp 65533 vrf default distance 20 70 20\n"
            + "router bgp 65533 vrf Customer maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer maximum-paths 32\n"
            + "router bgp 65533 vrf default maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 remote-as 65532\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 route-map ncn-w001\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 route-map ncn-w002\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 route-map ncn-w003\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 route-map ncn-w001-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 route-map ncn-w002-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 route-map ncn-w003-Customer\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 transport connection-mode passive\n"
            + "no ntp server 192.168.4.4 disable\n"
            + "ntp server 192.168.4.4 keyID 0\n"
            + "no ntp server 192.168.4.4 trusted-enable\n"
            + "ntp server 192.168.4.4 version 4\n"
            + "no ntp server 192.168.4.5 disable\n"
            + "ntp server 192.168.4.5 keyID 0\n"
            + "no ntp server 192.168.4.5 trusted-enable\n"
            + "ntp server 192.168.4.5 version 4\n"
            + "no ntp server 192.168.4.6 disable\n"
            + "ntp server 192.168.4.6 keyID 0\n"
            + "no ntp server 192.168.4.6 trusted-enable\n"
            + "ntp server 192.168.4.6 version 4\n"
            + "ntp vrf default enable\n"
        ) in str(result.output)
        print(result.output)


def test_switch_config_spine_primary_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid primary spine config."""
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
                "--custom-config",
                custom_file,
            ],
        )
        assert result.exit_code == 0
        print(result.output)
        assert (
            "# interface ethernet 1/1 speed 10G force\n"
            + '# interface ethernet 1/1 description "sw-spine02-1/16"\n'
            + "# interface ethernet 1/1 no switchport force\n"
            + "# interface ethernet 1/1 ip address 10.102.255.14/30 primary\n"
            + "# interface ethernet 1/1 dcb priority-flow-control mode on force\n"
            + "# ip route vrf default 0.0.0.0/0 10.102.255.13\n"
        ) in str(result.output)
        assert (
            "hostname sw-spine-001\n"
            + "no cli default prefix-modes enable\n"
            + "protocol mlag\n"
            + "protocol bgp\n"
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
            + "interface ethernet 1/31 speed 40G force\n"
            + "interface ethernet 1/32 speed 40G force\n"
            + "interface ethernet 1/2 speed 40G force\n"
            + "interface ethernet 1/3 speed 40G force\n"
            + "interface ethernet 1/4 speed 40G force\n"
            + "interface ethernet 1/5 speed 40G force\n"
            + "interface ethernet 1/6 speed 40G force\n"
            + "interface ethernet 1/7 speed 40G force\n"
            + "interface ethernet 1/8 speed 40G force\n"
            + "interface ethernet 1/9 speed 40G force\n"
            + "interface ethernet 1/13 speed 40G force\n"
            + "interface ethernet 1/26 speed 10G force\n"
            + "interface ethernet 1/29 speed 40G force\n"
            + "interface ethernet 1/30 speed 40G force\n"
            + "interface ethernet 1/1 speed 10G force\n"
            + "interface ethernet 1/16 speed 10G force\n"
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
            + 'interface ethernet 1/1 description "sw-spine02-1/16"\n'
            + 'interface ethernet 1/2 description "ncn-m002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/3 description "ncn-m003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/4 description "ncn-w001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/5 description "ncn-w002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/6 description "ncn-w003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/7 description "ncn-s001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/8 description "ncn-s002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/9 description "ncn-s003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/13 description "uan001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface ethernet 1/16 description "sw-spine02-1/16"\n'
            + 'interface ethernet 1/26 description "sw-leaf-bmc-001:51<==sw-spine-001"\n'
            + 'interface ethernet 1/29 description "sw-cdu-001:27<==sw-spine-001"\n'
            + 'interface ethernet 1/30 description "sw-cdu-002:27<==sw-spine-001"\n'
            + 'interface ethernet 1/31 description "mlag-isl"\n'
            + 'interface ethernet 1/32 description "mlag-isl"\n'
            + 'interface mlag-port-channel 1 description "ncn-m001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 2 description "ncn-m002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 3 description "ncn-m003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 4 description "ncn-w001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 5 description "ncn-w002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 6 description "ncn-w003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 7 description "ncn-s001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 8 description "ncn-s002:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 9 description "ncn-s003:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 13 description "uan001:pcie-slot1:1<==sw-spine-001"\n'
            + 'interface mlag-port-channel 151 description "sw-leaf-bmc-001:51<==sw-spine-001"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-001:27<==sw-spine-001"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-002:27<==sw-spine-001"\n'
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel 256\n"
            + "interface ethernet 1/31 channel-group 256 mode active\n"
            + "interface ethernet 1/32 channel-group 256 mode active\n"
            + 'interface port-channel 256 description "mlag-isl"\n'
            + "interface port-channel 256 dcb priority-flow-control mode on force\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface ethernet 1/1 ip address 10.102.255.14/30 primary\n"
            + "interface ethernet 1/1 dcb priority-flow-control mode on force\n"
            + "interface ethernet 1/16 ip address 10.102.255.14/30 primary\n"
            + "interface ethernet 1/16 dcb priority-flow-control mode on force\n"
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
        print(result.output)
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
        ) in str(result.output)
        assert (
            "vlan 2\n"
            + "vlan 4\n"
            + "vlan 6\n"
            + "vlan 4000\n"
            + 'vlan 2 name "RVR_NMN"\n'
            + 'vlan 4 name "RVR_HMN"\n'
            + 'vlan 6 name "CMN"\n'
            + 'vlan 4000 name "MLAG"\n'
            + "vlan 7\n"
            + 'vlan 7 name "CAN"\n'
        ) in str(result.output)
        print(result.output)

        assert (
            "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 6\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "web vrf default enable\n"
            + "vrf definition Customer\n"
            + "vrf definition Customer rd 7:7\n"
            + "ip routing vrf Customer\n"
            + "ip routing vrf default\n"
            + "ip name-server vrf vrf-default 10.92.100.225\n"
            + "no ldap vrf mgmt enable\n"
            + "no radius-server vrf mgmt enable\n"
            + "no snmp-server vrf mgmt enable\n"
            + "no tacacs-server vrf mgmt enable\n"
            + "vrf definition mgmt\n"
            + "interface loopback 0\n"
            + "interface loopback 0 ip address 10.2.0.2/32 primary\n"
            + "interface vlan 7 vrf forwarding Customer\n"
            + "interface vlan 7 ip address 192.168.11.2/24 primary\n"
            + "no interface vlan 7 ip icmp redirect\n"
            + "interface vlan 7 mtu 9184\n"
            + "interface vlan 1\n"
            + "interface vlan 2\n"
            + "interface vlan 4\n"
            + "interface vlan 6 vrf forwarding Customer\n"
            + "interface vlan 10\n"
            + "interface vlan 4000\n"
            + "interface vlan 1 ip address 192.168.1.2/16 primary\n"
            + "interface vlan 2 ip address 192.168.3.2/17 primary\n"
            + "interface vlan 4 ip address 192.168.0.2/17 primary\n"
            + "interface vlan 6 ip address 192.168.12.2/24 primary\n"
            + "interface vlan 4000 ip address 192.168.255.253/30 primary\n"
            + "no interface vlan 1 ip icmp redirect\n"
            + "interface vlan 1 mtu 9184\n"
            + "no interface vlan 2 ip icmp redirect\n"
            + "interface vlan 2 mtu 9184\n"
            + "no interface vlan 4 ip icmp redirect\n"
            + "interface vlan 4 mtu 9184\n"
            + "no interface vlan 6 ip icmp redirect\n"
            + "interface vlan 6 mtu 9184\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface ethernet 1/1 no switchport force\n"
            + "interface ethernet 1/16 no switchport force\n"
            + "ip load-sharing source-ip-port\n"
            + "ip load-sharing type consistent\n"
            + "ip route vrf default 0.0.0.0/0 10.102.255.13\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree priority 4096\n"
            + "spanning-tree port type edge default\n"
            + "spanning-tree mst name cray\n"
            + "spanning-tree mst revision 2\n"
            + "interface mlag-port-channel 151 spanning-tree port type network\n"
            + "interface mlag-port-channel 151 spanning-tree guard root\n"
            + "interface mlag-port-channel 201 spanning-tree port type network\n"
            + "interface mlag-port-channel 201 spanning-tree guard root\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "ipv4 access-list nmn-hmn\n"
            + "ipv4 access-list nmn-hmn bind-point rif\n"
            + "ipv4 access-list nmn-hmn seq-number 10 deny ip 192.168.3.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 20 deny ip 192.168.0.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 30 deny ip 192.168.3.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 40 deny ip 192.168.0.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 50 deny ip 192.168.100.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 60 deny ip 192.168.100.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 70 deny ip 192.168.200.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 80 deny ip 192.168.200.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 90 permit ip any any\n"
            + "ipv4 access-list cmn-can\n"
            + "ipv4 access-list cmn-can bind-point rif\n"
            + "ipv4 access-list cmn-can seq-number 10 deny ip 192.168.12.0 mask 255.255.255.0 192.168.11.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 20 deny ip 192.168.11.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 30 deny ip 192.168.12.0 mask 255.255.255.0 192.168.200.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 40 deny ip 192.168.200.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 50 permit ip any any\n"
            + "interface vlan 2 ipv4 port access-group nmn-hmn\n"
            + "interface vlan 4 ipv4 port access-group nmn-hmn\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "protocol ospf\n"
            + "router ospf 1 vrf default\n"
            + "router ospf 2 vrf Customer\n"
            + "router ospf 1 vrf default router-id 10.2.0.2\n"
            + "router ospf 2 vrf Customer router-id 10.2.0.2\n"
            + "router ospf 2 vrf Customer default-information originate\n"
            + "interface loopback 0 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf area 0.0.0.0\n"
            + "interface vlan 2 ip ospf area 0.0.0.0\n"
            + "interface vlan 4 ip ospf area 0.0.0.0\n"
            + "interface vlan 6 ip ospf area 0.0.0.0\n"
            + "interface vlan 7 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf passive-interface\n"
            + "interface vlan 4 ip ospf passive-interface\n"
            + "router ospf 1 vrf default redistribute bgp\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "ip dhcp relay instance 2 vrf default\n"
            + "ip dhcp relay instance 4 vrf default\n"
            + "ip dhcp relay instance 2 address 10.92.100.222\n"
            + "ip dhcp relay instance 4 address 10.94.100.222\n"
            + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "protocol magp\n"
            + "interface vlan 1 magp 1\n"
            + "interface vlan 2 magp 2\n"
            + "interface vlan 4 magp 3\n"
            + "interface vlan 6 magp 4\n"
            + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
            + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
            + "interface vlan 4 magp 3 ip virtual-router address 192.168.0.1\n"
            + "interface vlan 6 magp 4 ip virtual-router address 192.168.12.1\n"
            + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:02\n"
            + "interface vlan 4 magp 3 ip virtual-router mac-address 00:00:5E:00:01:03\n"
            + "interface vlan 6 magp 4 ip virtual-router mac-address 00:00:5E:00:01:04\n"
            + "interface vlan 7 magp 5\n"
            + "interface vlan 7 magp 5 ip virtual-router address 192.168.11.1\n"
            + "interface vlan 7 magp 5 ip virtual-router mac-address 00:00:5E:00:01:05\n"
            + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
            + "no mlag shutdown\n"
            + "mlag system-mac 00:00:5E:00:01:01\n"
            + "interface port-channel 256 ipl 1\n"
            + "interface vlan 4000 ipl 1 peer-address 192.168.255.254\n"
            + "no interface mgmt0 dhcp\n"
            + "interface mgmt0 ip address 192.168.255.241 /29\n"
            + "ip prefix-list pl-cmn\n"
            + "ip prefix-list pl-cmn bulk-mode\n"
            + "ip prefix-list pl-cmn seq 10 permit 192.168.12.0 /24 ge 24\n"
            + "ip prefix-list pl-cmn commit\n"
            + "ip prefix-list pl-can\n"
            + "ip prefix-list pl-can bulk-mode\n"
            + "ip prefix-list pl-can seq 10 permit 192.168.11.0 /24 ge 24\n"
            + "ip prefix-list pl-can commit\n"
            + "ip prefix-list pl-hmn\n"
            + "ip prefix-list pl-hmn bulk-mode\n"
            + "ip prefix-list pl-hmn seq 20 permit 10.94.100.0 /24 ge 24\n"
            + "ip prefix-list pl-hmn commit\n"
            + "ip prefix-list pl-nmn\n"
            + "ip prefix-list pl-nmn bulk-mode\n"
            + "ip prefix-list pl-nmn seq 30 permit 10.92.100.0 /24 ge 24\n"
            + "ip prefix-list pl-nmn commit\n"
            + "route-map ncn-w001-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w001-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w001-Customer permit 20 set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w001 permit 10 set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w001 permit 20 set ip next-hop 192.168.4.4\n"
            + "route-map ncn-w002-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w002-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w002-Customer permit 20 set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w002 permit 10 set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w002 permit 20 set ip next-hop 192.168.4.5\n"
            + "route-map ncn-w003-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w003-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w003-Customer permit 20 set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w003 permit 10 set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w003 permit 20 set ip next-hop 192.168.4.6\n"
            + "router bgp 65533 vrf Customer\n"
            + "router bgp 65533 vrf default\n"
            + "router bgp 65533 vrf Customer router-id 10.2.0.2 force\n"
            + "router bgp 65533 vrf default router-id 10.2.0.2 force\n"
            + "router bgp 65533 vrf Customer distance 20 70 20\n"
            + "router bgp 65533 vrf default distance 20 70 20\n"
            + "router bgp 65533 vrf Customer maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer maximum-paths 32\n"
            + "router bgp 65533 vrf default maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 remote-as 65532\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 route-map ncn-w001\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 route-map ncn-w002\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 route-map ncn-w003\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 route-map ncn-w001-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 route-map ncn-w002-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 route-map ncn-w003-Customer\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 transport connection-mode passive\n"
            + "no ntp server 192.168.4.4 disable\n"
            + "ntp server 192.168.4.4 keyID 0\n"
            + "no ntp server 192.168.4.4 trusted-enable\n"
            + "ntp server 192.168.4.4 version 4\n"
            + "no ntp server 192.168.4.5 disable\n"
            + "ntp server 192.168.4.5 keyID 0\n"
            + "no ntp server 192.168.4.5 trusted-enable\n"
            + "ntp server 192.168.4.5 version 4\n"
            + "no ntp server 192.168.4.6 disable\n"
            + "ntp server 192.168.4.6 keyID 0\n"
            + "no ntp server 192.168.4.6 trusted-enable\n"
            + "ntp server 192.168.4.6 version 4\n"
            + "ntp vrf default enable\n"
        ) in str(result.output)
        print(result.output)


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
            + "protocol mlag\n"
            + "protocol bgp\n"
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
            + "interface ethernet 1/31 speed 40G force\n"
            + "interface ethernet 1/32 speed 40G force\n"
            + "interface ethernet 1/1 speed 40G force\n"
            + "interface ethernet 1/2 speed 40G force\n"
            + "interface ethernet 1/3 speed 40G force\n"
            + "interface ethernet 1/4 speed 40G force\n"
            + "interface ethernet 1/5 speed 40G force\n"
            + "interface ethernet 1/6 speed 40G force\n"
            + "interface ethernet 1/7 speed 40G force\n"
            + "interface ethernet 1/8 speed 40G force\n"
            + "interface ethernet 1/9 speed 40G force\n"
            + "interface ethernet 1/13 speed 40G force\n"
            + "interface ethernet 1/26 speed 10G force\n"
            + "interface ethernet 1/29 speed 40G force\n"
            + "interface ethernet 1/30 speed 40G force\n"
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
            + 'interface ethernet 1/1 description "ncn-m001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/2 description "ncn-m002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/3 description "ncn-m003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/4 description "ncn-w001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/5 description "ncn-w002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/6 description "ncn-w003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/7 description "ncn-s001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/8 description "ncn-s002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/9 description "ncn-s003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/13 description "uan001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface ethernet 1/26 description "sw-leaf-bmc-001:52<==sw-spine-002"\n'
            + 'interface ethernet 1/29 description "sw-cdu-001:28<==sw-spine-002"\n'
            + 'interface ethernet 1/30 description "sw-cdu-002:28<==sw-spine-002"\n'
            + 'interface ethernet 1/31 description "mlag-isl"\n'
            + 'interface ethernet 1/32 description "mlag-isl"\n'
            + 'interface mlag-port-channel 1 description "ncn-m001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 2 description "ncn-m002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 3 description "ncn-m003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 4 description "ncn-w001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 5 description "ncn-w002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 6 description "ncn-w003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 7 description "ncn-s001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 8 description "ncn-s002:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 9 description "ncn-s003:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 13 description "uan001:pcie-slot1:2<==sw-spine-002"\n'
            + 'interface mlag-port-channel 151 description "sw-leaf-bmc-001:52<==sw-spine-002"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-001:28<==sw-spine-002"\n'
            + 'interface mlag-port-channel 201 description "sw-cdu-002:28<==sw-spine-002"\n'
        ) in str(result.output)
        print(result.output)

        assert (
            "interface port-channel 256\n"
            + "interface ethernet 1/31 channel-group 256 mode active\n"
            + "interface ethernet 1/32 channel-group 256 mode active\n"
            + 'interface port-channel 256 description "mlag-isl"\n'
            + "interface port-channel 256 dcb priority-flow-control mode on force\n"
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
            "vlan 2\n"
            + "vlan 4\n"
            + "vlan 6\n"
            + "vlan 4000\n"
            + 'vlan 2 name "RVR_NMN"\n'
            + 'vlan 4 name "RVR_HMN"\n'
            + 'vlan 6 name "CMN"\n'
            + 'vlan 4000 name "MLAG"\n'
            + "vlan 7\n"
            + 'vlan 7 name "CAN"\n'
        ) in str(result.output)
        print(result.output)
        assert (
            "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 3 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 4 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 5 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 6 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 7 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 8 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 9 switchport hybrid allowed-vlan add 7\n"
            + "interface mlag-port-channel 13 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 6\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 151 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 2\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 4\n"
            + "interface mlag-port-channel 201 switchport hybrid allowed-vlan add 6\n"
        ) in str(result.output)
        assert (
            "web vrf default enable\n"
            + "vrf definition Customer\n"
            + "vrf definition Customer rd 7:7\n"
            + "ip routing vrf Customer\n"
            + "ip routing vrf default\n"
            + "ip name-server vrf vrf-default 10.92.100.225\n"
            + "no ldap vrf mgmt enable\n"
            + "no radius-server vrf mgmt enable\n"
            + "no snmp-server vrf mgmt enable\n"
            + "no tacacs-server vrf mgmt enable\n"
            + "vrf definition mgmt\n"
            + "interface loopback 0\n"
            + "interface loopback 0 ip address 10.2.0.3/32 primary\n"
            + "interface vlan 7 vrf forwarding Customer\n"
            + "interface vlan 7 ip address 192.168.11.3/24 primary\n"
            + "no interface vlan 7 ip icmp redirect\n"
            + "interface vlan 7 mtu 9184\n"
            + "interface vlan 1\n"
            + "interface vlan 2\n"
            + "interface vlan 4\n"
            + "interface vlan 6 vrf forwarding Customer\n"
            + "interface vlan 10\n"
            + "interface vlan 4000\n"
            + "interface vlan 1 ip address 192.168.1.3/16 primary\n"
            + "interface vlan 2 ip address 192.168.3.3/17 primary\n"
            + "interface vlan 4 ip address 192.168.0.3/17 primary\n"
            + "interface vlan 6 ip address 192.168.12.3/24 primary\n"
            + "interface vlan 4000 ip address 192.168.255.254/30 primary\n"
            + "no interface vlan 1 ip icmp redirect\n"
            + "interface vlan 1 mtu 9184\n"
            + "no interface vlan 2 ip icmp redirect\n"
            + "interface vlan 2 mtu 9184\n"
            + "no interface vlan 4 ip icmp redirect\n"
            + "interface vlan 4 mtu 9184\n"
            + "no interface vlan 6 ip icmp redirect\n"
            + "interface vlan 6 mtu 9184\n"
        ) in str(result.output)
        assert (
            "ip load-sharing source-ip-port\n"
            + "ip load-sharing type consistent\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree priority 4096\n"
            + "spanning-tree port type edge default\n"
            + "spanning-tree mst name cray\n"
            + "spanning-tree mst revision 2\n"
            + "interface mlag-port-channel 151 spanning-tree port type network\n"
            + "interface mlag-port-channel 151 spanning-tree guard root\n"
            + "interface mlag-port-channel 201 spanning-tree port type network\n"
            + "interface mlag-port-channel 201 spanning-tree guard root\n"
        ) in str(result.output)
        assert (
            "ipv4 access-list nmn-hmn\n"
            + "ipv4 access-list nmn-hmn bind-point rif\n"
            + "ipv4 access-list nmn-hmn seq-number 10 deny ip 192.168.3.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 20 deny ip 192.168.0.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 30 deny ip 192.168.3.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 40 deny ip 192.168.0.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 50 deny ip 192.168.100.0 mask 255.255.128.0 192.168.0.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 60 deny ip 192.168.100.0 mask 255.255.128.0 192.168.200.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 70 deny ip 192.168.200.0 mask 255.255.128.0 192.168.3.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 80 deny ip 192.168.200.0 mask 255.255.128.0 192.168.100.0 mask 255.255.128.0\n"
            + "ipv4 access-list nmn-hmn seq-number 90 permit ip any any\n"
            + "ipv4 access-list cmn-can\n"
            + "ipv4 access-list cmn-can bind-point rif\n"
            + "ipv4 access-list cmn-can seq-number 10 deny ip 192.168.12.0 mask 255.255.255.0 192.168.11.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 20 deny ip 192.168.11.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 30 deny ip 192.168.12.0 mask 255.255.255.0 192.168.200.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 40 deny ip 192.168.200.0 mask 255.255.255.0 192.168.12.0 mask 255.255.255.0\n"
            + "ipv4 access-list cmn-can seq-number 50 permit ip any any\n"
            + "interface vlan 2 ipv4 port access-group nmn-hmn\n"
            + "interface vlan 4 ipv4 port access-group nmn-hmn\n"
        ) in str(result.output)
        assert (
            "protocol ospf\n"
            + "router ospf 1 vrf default\n"
            + "router ospf 2 vrf Customer\n"
            + "router ospf 1 vrf default router-id 10.2.0.3\n"
            + "router ospf 2 vrf Customer router-id 10.2.0.3\n"
            + "router ospf 2 vrf Customer default-information originate\n"
            + "interface loopback 0 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf area 0.0.0.0\n"
            + "interface vlan 2 ip ospf area 0.0.0.0\n"
            + "interface vlan 4 ip ospf area 0.0.0.0\n"
            + "interface vlan 6 ip ospf area 0.0.0.0\n"
            + "interface vlan 7 ip ospf area 0.0.0.0\n"
            + "interface vlan 1 ip ospf passive-interface\n"
            + "interface vlan 4 ip ospf passive-interface\n"
            + "router ospf 1 vrf default redistribute bgp\n"
        ) in str(result.output)
        assert (
            "ip dhcp relay instance 2 vrf default\n"
            + "ip dhcp relay instance 4 vrf default\n"
            + "ip dhcp relay instance 2 address 10.92.100.222\n"
            + "ip dhcp relay instance 4 address 10.94.100.222\n"
            + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
            + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
        ) in str(result.output)
        assert (
            "protocol magp\n"
            + "interface vlan 1 magp 1\n"
            + "interface vlan 2 magp 2\n"
            + "interface vlan 4 magp 3\n"
            + "interface vlan 6 magp 4\n"
            + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
            + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
            + "interface vlan 4 magp 3 ip virtual-router address 192.168.0.1\n"
            + "interface vlan 6 magp 4 ip virtual-router address 192.168.12.1\n"
            + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
            + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:02\n"
            + "interface vlan 4 magp 3 ip virtual-router mac-address 00:00:5E:00:01:03\n"
            + "interface vlan 6 magp 4 ip virtual-router mac-address 00:00:5E:00:01:04\n"
            + "interface vlan 7 magp 5\n"
            + "interface vlan 7 magp 5 ip virtual-router address 192.168.11.1\n"
            + "interface vlan 7 magp 5 ip virtual-router mac-address 00:00:5E:00:01:05\n"
            + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
            + "no mlag shutdown\n"
            + "mlag system-mac 00:00:5E:00:01:01\n"
            + "interface port-channel 256 ipl 1\n"
            + "interface vlan 4000 ipl 1 peer-address 192.168.255.253\n"
            + "no interface mgmt0 dhcp\n"
            + "interface mgmt0 ip address 192.168.255.243 /29\n"
            + "ip prefix-list pl-cmn\n"
            + "ip prefix-list pl-cmn bulk-mode\n"
            + "ip prefix-list pl-cmn seq 10 permit 192.168.12.0 /24 ge 24\n"
            + "ip prefix-list pl-cmn commit\n"
            + "ip prefix-list pl-can\n"
            + "ip prefix-list pl-can bulk-mode\n"
            + "ip prefix-list pl-can seq 10 permit 192.168.11.0 /24 ge 24\n"
            + "ip prefix-list pl-can commit\n"
            + "ip prefix-list pl-hmn\n"
            + "ip prefix-list pl-hmn bulk-mode\n"
            + "ip prefix-list pl-hmn seq 20 permit 10.94.100.0 /24 ge 24\n"
            + "ip prefix-list pl-hmn commit\n"
            + "ip prefix-list pl-nmn\n"
            + "ip prefix-list pl-nmn bulk-mode\n"
            + "ip prefix-list pl-nmn seq 30 permit 10.92.100.0 /24 ge 24\n"
            + "ip prefix-list pl-nmn commit\n"
            + "route-map ncn-w001-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w001-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w001-Customer permit 20 set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w001 permit 10 set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w001 permit 20 set ip next-hop 192.168.4.4\n"
            + "route-map ncn-w002-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w002-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w002-Customer permit 20 set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w002 permit 10 set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w002 permit 20 set ip next-hop 192.168.4.5\n"
            + "route-map ncn-w003-Customer permit 10 match ip address pl-cmn\n"
            + "route-map ncn-w003-Customer permit 20 match ip address pl-can\n"
            + "route-map ncn-w003-Customer permit 20 set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003 permit 10 match ip address pl-hmn\n"
            + "route-map ncn-w003 permit 10 set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit 20 match ip address pl-nmn\n"
            + "route-map ncn-w003 permit 20 set ip next-hop 192.168.4.6\n"
            + "router bgp 65533 vrf Customer\n"
            + "router bgp 65533 vrf default\n"
            + "router bgp 65533 vrf Customer router-id 10.2.0.3 force\n"
            + "router bgp 65533 vrf default router-id 10.2.0.3 force\n"
            + "router bgp 65533 vrf Customer distance 20 70 20\n"
            + "router bgp 65533 vrf default distance 20 70 20\n"
            + "router bgp 65533 vrf Customer maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer maximum-paths 32\n"
            + "router bgp 65533 vrf default maximum-paths ibgp 32\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 remote-as 65532\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 remote-as 65532\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 route-map ncn-w001\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 route-map ncn-w002\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 remote-as 65531\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 route-map ncn-w003\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 timers 1 3\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 timers 1 3\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.4 route-map ncn-w001-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.5 route-map ncn-w002-Customer\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 transport connection-mode passive\n"
            + "router bgp 65533 vrf Customer neighbor 192.168.12.6 route-map ncn-w003-Customer\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.4 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.5 transport connection-mode passive\n"
            + "router bgp 65533 vrf default neighbor 192.168.4.6 transport connection-mode passive\n"
            + "no ntp server 192.168.4.4 disable\n"
            + "ntp server 192.168.4.4 keyID 0\n"
            + "no ntp server 192.168.4.4 trusted-enable\n"
            + "ntp server 192.168.4.4 version 4\n"
            + "no ntp server 192.168.4.5 disable\n"
            + "ntp server 192.168.4.5 keyID 0\n"
            + "no ntp server 192.168.4.5 trusted-enable\n"
            + "ntp server 192.168.4.5 version 4\n"
            + "no ntp server 192.168.4.6 disable\n"
            + "ntp server 192.168.4.6 keyID 0\n"
            + "no ntp server 192.168.4.6 trusted-enable\n"
            + "ntp server 192.168.4.6 version 4\n"
            + "ntp vrf default enable\n"
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
        print(result.output)
        assert (
            "ip vrf Customer\n"
            + "ip name-server 10.92.100.225\n"
            + "hostname sw-leaf-bmc-001\n"
            + "rest api restconf\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface vlan1\n"
            + "  description MTL\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.1.12/16\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "interface vlan2\n"
            + "  description RIVER_NMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.3.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface vlan4\n"
            + "  description RIVER_HMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.0.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "interface vlan6\n"
            + "  description CMN\n"
            + "  no shutdown\n"
            + "  ip vrf forwarding Customer\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.12.4/24\n"
            + "  ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)
        assert (
            "interface port-channel101\n"
            + "  description sw-spine-001:26<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4,6\n"
            + "  mtu 9216\n"
        ) in str(result.output)
        assert (
            "interface loopback0\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 10.2.0.12/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  shutdown\n"
            + "  ip address dhcp\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/51\n"
            + "  no shutdown\n"
            + "  channel-group 101 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/52\n"
            + "  no shutdown\n"
            + "  channel-group 101 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/1\n"
            + "  description ncn-m001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/2\n"
            + "  description ncn-m002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/3\n"
            + "  description ncn-m003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/4\n"
            + "  description ncn-w001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/5\n"
            + "  description ncn-w002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/6\n"
            + "  description ncn-w003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/7\n"
            + "  description ncn-s001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/8\n"
            + "  description ncn-s002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/9\n"
            + "  description ncn-s003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/10\n"
            + "  description uan001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
        ) in str(result.output)
        print(result.output)
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
            + "ip access-list cmn-can\n"
            + "  seq 10 deny ip 192.168.12.0/24 192.168.11.0/24\n"
            + "  seq 20 deny ip 192.168.11.0/24 192.168.12.0/24\n"
            + "  seq 30 deny ip 192.168.12.0/24 192.168.200.0/24\n"
            + "  seq 40 deny ip 192.168.200.0/24 192.168.12.0/24\n"
            + "  seq 50 permit ip any any\n"
        ) in str(result.output)
        assert (
            "load-balancing ingress-port enable\n"
            + "no load-balancing mac-selection destination-mac\n"
            + "no load-balancing mac-selection ethertype\n"
            + "no load-balancing mac-selection source-mac\n"
            + "no load-balancing mac-selection vlan-id\n"
            + "no load-balancing tcp-udp-selection l4-destination-port\n"
            + "no load-balancing tcp-udp-selection l4-source-port\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.12\n"
            + "router ospf 2 vrf Customer\n"
            + "  router-id 10.2.0.12\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  name cray\n"
            + "  revision 2\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)


def test_switch_config_leaf_bmc_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid leaf-bmc config."""
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
                "--custom-config",
                custom_file,
            ],
        )
        assert result.exit_code == 0
        print(result.output)
        assert (
            "# interface ethernet1/1/12\n"
            + "#   description cn003:2<==sw-leaf-bmc-001\n"
            + "#   switchport access vlan 2\n"
            + "# interface vlan6\n"
            + "#   ip address 10.102.4.100/25\n"
        ) in str(result.output)
        assert (
            "ip vrf Customer\n"
            + "ip name-server 10.92.100.225\n"
            + "hostname sw-leaf-bmc-001\n"
            + "rest api restconf\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface vlan1\n"
            + "  description MTL\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.1.12/16\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "interface vlan2\n"
            + "  description RIVER_NMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.3.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface vlan4\n"
            + "  description RIVER_HMN\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.0.12/17\n"
            + "  ip access-group nmn-hmn in\n"
            + "  ip access-group nmn-hmn out\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
            + "interface vlan6\n"
            + "  description CMN\n"
            + "  no shutdown\n"
            + "  ip vrf forwarding Customer\n"
            + "  mtu 9216\n"
            + "  ip address 10.102.4.100/25\n"
            + "  ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel101\n"
            + "  description sw-spine-001:26<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4,6\n"
            + "  mtu 9216\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface loopback0\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 10.2.0.12/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  shutdown\n"
            + "  ip address dhcp\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/51\n"
            + "  no shutdown\n"
            + "  channel-group 101 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/52\n"
            + "  no shutdown\n"
            + "  channel-group 101 mode active\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  speed 10000\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/1\n"
            + "  description ncn-m001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/2\n"
            + "  description ncn-m002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/3\n"
            + "  description ncn-m003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/4\n"
            + "  description ncn-w001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/5\n"
            + "  description ncn-w002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/6\n"
            + "  description ncn-w003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/7\n"
            + "  description ncn-s001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/8\n"
            + "  description ncn-s002:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/9\n"
            + "  description ncn-s003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/10\n"
            + "  description uan001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/11\n"
            + "  description cn001:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/13\n"
            + "  description cn003:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/14\n"
            + "  description cn004:bmc:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 4\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/24\n"
            + "  description cn001:onboard:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 2\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/25\n"
            + "  description cn002:onboard:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 2\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/26\n"
            + "  description cn003:onboard:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 2\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/27\n"
            + "  description cn004:onboard:1<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 2\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
        ) in str(result.output)
        assert (
            "interface ethernet1/1/15\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/16\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/17\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/18\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/19\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/20\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/21\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/22\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/23\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/28\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/29\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/30\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/31\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/32\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/33\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/34\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/35\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/36\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/37\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/38\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/39\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/40\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/41\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/42\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/43\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/44\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/45\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/46\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/47\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/48\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/49\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/50\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
        ) in str(result.output)

        assert (
            "interface ethernet1/1/12\n"
            + "  description cn003:2<==sw-leaf-bmc-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 2\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
        ) in str(result.output)
        print(result.output)
        print(result.output)
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
            + "ip access-list cmn-can\n"
            + "  seq 10 deny ip 192.168.12.0/24 192.168.11.0/24\n"
            + "  seq 20 deny ip 192.168.11.0/24 192.168.12.0/24\n"
            + "  seq 30 deny ip 192.168.12.0/24 192.168.200.0/24\n"
            + "  seq 40 deny ip 192.168.200.0/24 192.168.12.0/24\n"
            + "  seq 50 permit ip any any\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.12\n"
            + "router ospf 2 vrf Customer\n"
            + "  router-id 10.2.0.12\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  name cray\n"
            + "  revision 2\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
        ) in str(result.output)
        print(result.output)


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
        print(result.output)
        assert (
            "ip vrf Customer\n"
            + "ip name-server 10.92.100.225\n"
            + "hostname sw-cdu-001\n"
            + "rest api restconf\n"
        ) in str(result.output)
        print(result.output)
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
        print(result.output)
        assert (
            "interface vlan1\n"
            + "  description MTL\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.1.16/16\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
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
            + "  ip ospf passive\n"
            + "interface vlan6\n"
            + "  description CMN\n"
            + "  no shutdown\n"
            + "  ip vrf forwarding Customer\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.12.5/24\n"
            + "  ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel2\n"
            + "  description cmm-x3002-000:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 2\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel3\n"
            + "  description cmm-x3002-001:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 3\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel4\n"
            + "  description cmm-x3002-002:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 4\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel5\n"
            + "  description cmm-x3002-003:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 5\n"
            + "  spanning-tree guard root\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel255\n"
            + "  description sw-spine-001:29<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4,6\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 255\n"
            + "interface loopback0\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 10.2.0.16/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  no shutdown\n"
            + "  dhcp\n"
            + "  ip address 192.168.255.242/29\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/2\n"
            + "  description cmm-x3002-000:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  channel-group 2\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/3\n"
            + "  description cmm-x3002-001:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  channel-group 3\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/4\n"
            + "  description cmm-x3002-002:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  channel-group 4\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/5\n"
            + "  description cmm-x3002-003:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  channel-group 5\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/1\n"
            + "  description cec-x3002-000:1<==sw-cdu-001\n"
            + "  no shutdown\n"
            + "  switchport access vlan 3000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "  spanning-tree bpduguard enable\n"
            + "  spanning-tree port type edge\n"
            + "interface ethernet1/1/27\n"
            + "  no shutdown\n"
            + "  channel-group 255 mode active\n"
            + "  no switchport\n"
            + "  speed 40000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/28\n"
            + "  no shutdown\n"
            + "  channel-group 255 mode active\n"
            + "  no switchport\n"
            + "  speed 40000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/6\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/7\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/8\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/9\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/10\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/11\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/12\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/13\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/14\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/15\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/16\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/17\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/18\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/19\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/21\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/22\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/23\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/24\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/29\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/30\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/31\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/32\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/33\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/34\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/35\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/36\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/37\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/38\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/39\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/40\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/41\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/42\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/43\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/44\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/45\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/46\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/47\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/48\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/49\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/50\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/51\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/52\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/53\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/54\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface ethernet1/1/25\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/26\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
        ) in str(result.output)
        print(result.output)
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
            + "ip access-list cmn-can\n"
            + "  seq 10 deny ip 192.168.12.0/24 192.168.11.0/24\n"
            + "  seq 20 deny ip 192.168.11.0/24 192.168.12.0/24\n"
            + "  seq 30 deny ip 192.168.12.0/24 192.168.200.0/24\n"
            + "  seq 40 deny ip 192.168.200.0/24 192.168.12.0/24\n"
            + "  seq 50 permit ip any any\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "load-balancing ingress-port enable\n"
            + "no load-balancing mac-selection destination-mac\n"
            + "no load-balancing mac-selection ethertype\n"
            + "no load-balancing mac-selection source-mac\n"
            + "no load-balancing mac-selection vlan-id\n"
            + "no load-balancing tcp-udp-selection l4-destination-port\n"
            + "no load-balancing tcp-udp-selection l4-source-port\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.16\n"
            + "router ospf 2 vrf Customer\n"
            + "  router-id 10.2.0.16\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  name cray\n"
            + "  revision 2\n"
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
        print(result.output)


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
            "ip vrf Customer\n"
            + "ip name-server 10.92.100.225\n"
            + "hostname sw-cdu-002\n"
            + "rest api restconf\n"
        ) in str(result.output)
        print(result.output)
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
        print(result.output)
        assert (
            "interface vlan1\n"
            + "  description MTL\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.1.17/16\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "  ip ospf passive\n"
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
            + "  ip ospf passive\n"
            + "interface vlan6\n"
            + "  description CMN\n"
            + "  no shutdown\n"
            + "  ip vrf forwarding Customer\n"
            + "  mtu 9216\n"
            + "  ip address 192.168.12.6/24\n"
            + "  ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "interface port-channel2\n"
            + "  description cmm-x3002-000:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 2\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel3\n"
            + "  description cmm-x3002-001:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 3\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel4\n"
            + "  description cmm-x3002-002:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 4\n"
            + "  spanning-tree guard root\n"
            + "interface port-channel5\n"
            + "  description cmm-x3002-003:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 2000\n"
            + "  switchport trunk allowed vlan 3000\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 5\n"
            + "  spanning-tree guard root\n"
        ) in str(result.output)
        print(result.output)
        print(result.output)
        assert (
            "interface port-channel255\n"
            + "  description sw-spine-001:30<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  switchport mode trunk\n"
            + "  switchport access vlan 1\n"
            + "  switchport trunk allowed vlan 2,4,6\n"
            + "  mtu 9216\n"
            + "  vlt-port-channel 255\n"
            + "interface loopback0\n"
            + "  no shutdown\n"
            + "  mtu 9216\n"
            + "  ip address 10.2.0.17/32\n"
            + "  ip ospf 1 area 0.0.0.0\n"
            + "interface mgmt1/1/1\n"
            + "  no shutdown\n"
            + "  dhcp\n"
            + "  ip address 192.168.255.243/29\n"
            + "  ipv6 address autoconfig\n"
            + "interface ethernet1/1/2\n"
            + "  description cmm-x3002-000:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  channel-group 2\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/3\n"
            + "  description cmm-x3002-001:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  channel-group 3\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/4\n"
            + "  description cmm-x3002-002:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  channel-group 4\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/5\n"
            + "  description cmm-x3002-003:2<==sw-cdu-002\n"
            + "  no shutdown\n"
            + "  channel-group 5\n"
            + "  no switchport\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive on\n"
            + "  flowcontrol transmit on\n"
            + "interface ethernet1/1/27\n"
            + "  no shutdown\n"
            + "  channel-group 255 mode active\n"
            + "  no switchport\n"
            + "  speed 40000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/28\n"
            + "  no shutdown\n"
            + "  channel-group 255 mode active\n"
            + "  no switchport\n"
            + "  speed 40000\n"
            + "  mtu 9216\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/1\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/6\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/7\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/8\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/9\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/10\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/11\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/12\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/13\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/14\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/15\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/16\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/17\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/18\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/19\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/21\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/22\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/23\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/24\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/29\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/30\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/31\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/32\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/33\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/34\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/35\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/36\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/37\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/38\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/39\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/40\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/41\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/42\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/43\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/44\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/45\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/46\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/47\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/48\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/49\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/50\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/51\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/52\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/53\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/54\n"
            + "  shutdown\n"
            + "  switchport access vlan 1\n"
            + "  flowcontrol receive on\n"
            + "interface ethernet1/1/25\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
            + "interface ethernet1/1/26\n"
            + "  no shutdown\n"
            + "  no switchport\n"
            + "  flowcontrol receive off\n"
            + "  flowcontrol transmit off\n"
        ) in str(result.output)
        print(result.output)
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
            + "ip access-list cmn-can\n"
            + "  seq 10 deny ip 192.168.12.0/24 192.168.11.0/24\n"
            + "  seq 20 deny ip 192.168.11.0/24 192.168.12.0/24\n"
            + "  seq 30 deny ip 192.168.12.0/24 192.168.200.0/24\n"
            + "  seq 40 deny ip 192.168.200.0/24 192.168.12.0/24\n"
            + "  seq 50 permit ip any any\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "load-balancing ingress-port enable\n"
            + "no load-balancing mac-selection destination-mac\n"
            + "no load-balancing mac-selection ethertype\n"
            + "no load-balancing mac-selection source-mac\n"
            + "no load-balancing mac-selection vlan-id\n"
            + "no load-balancing tcp-udp-selection l4-destination-port\n"
            + "no load-balancing tcp-udp-selection l4-source-port\n"
        ) in str(result.output)
        print(result.output)
        assert (
            "router ospf 1\n"
            + "  router-id 10.2.0.17\n"
            + "router ospf 2 vrf Customer\n"
            + "  router-id 10.2.0.17\n"
            + "spanning-tree mode mst\n"
            + "spanning-tree mst configuration\n"
            + "  name cray\n"
            + "  revision 2\n"
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
        print(result.output)


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
                    {
                        "FullName": "CAN Bootstrap DHCP Subnet",
                        "CIDR": "192.168.11.0/24",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.11.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.11.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.11.6"},
                        ],
                        "Name": "bootstrap_dhcp",
                        "VlanID": 7,
                        "Gateway": "192.168.11.1",
                    },
                ],
            },
        },
        "CHN": {
            "Name": "CHN",
            "ExtraProperties": {
                "CIDR": "192.168.200.0/24",
                "MyASN": 65530,
                "PeerASN": 65533,
                "Subnets": [
                    {
                        "Name": "bootstrap_dhcp",
                        "CIDR": "192.168.200.0/24",
                        "IPReservations": [
                            {"Name": "chn-switch-1", "IPAddress": "192.168.200.2"},
                            {"Name": "chn-switch-2", "IPAddress": "192.168.200.3"},
                        ],
                        "VlanID": 5,
                        "Gateway": "192.168.200.1",
                    },
                    {
                        "FullName": "CHN Bootstrap DHCP Subnet",
                        "CIDR": "192.168.200.0/24",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.200.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.200.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.200.6"},
                        ],
                        "Name": "bootstrap_dhcp",
                        "VlanID": 5,
                        "Gateway": "192.168.200.1",
                    },
                ],
            },
        },
        "CMN": {
            "Name": "CMN",
            "ExtraProperties": {
                "CIDR": "192.168.12.0/24",
                "MyASN": 65532,
                "PeerASN": 65533,
                "Subnets": [
                    {
                        "Name": "network_hardware",
                        "CIDR": "192.168.12.0/24",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.12.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.12.3"},
                            {"Name": "sw-leaf-bmc-001", "IPAddress": "192.168.12.4"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.12.5"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.12.6"},
                        ],
                        "VlanID": 6,
                        "Gateway": "192.168.12.1",
                    },
                    {
                        "Name": "bootstrap_dhcp",
                        "CIDR": "192.168.12.0/24",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.12.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.12.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.12.6"},
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
                    {
                        "FullName": "HMN Bootstrap DHCP Subnet",
                        "CIDR": "192.168.0.0/17",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.0.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.0.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.0.6"},
                        ],
                        "Name": "bootstrap_dhcp",
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
                "MyASN": 65531,
                "PeerASN": 65533,
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
        "HMNLB": {
            "Name": "HMNLB",
            "ExtraProperties": {
                "CIDR": "10.94.100.0/24",
                "Subnets": [
                    {
                        "FullName": "NMN MetalLB",
                        "CIDR": "10.94.100.0/24",
                        "IPReservations": [
                            {"Name": "cray-tftp", "IPAddress": "10.94.100.60"},
                            {"Name": "unbound", "IPAddress": "10.94.100.225"},
                        ],
                        "Name": "hmn_metallb_address_pool",
                        "Gateway": "10.94.100.1",
                    },
                ],
            },
        },
        "NMNLB": {
            "Name": "NMNLB",
            "ExtraProperties": {
                "CIDR": "10.92.100.0/24",
                "Subnets": [
                    {
                        "FullName": "HMN MetalLB",
                        "CIDR": "10.92.100.0/24",
                        "IPReservations": [
                            {"Name": "cray-tftp", "IPAddress": "10.92.100.60"},
                            {"Name": "unbound", "IPAddress": "10.92.100.225"},
                        ],
                        "Name": "nmn_metallb_address_pool",
                        "Gateway": "10.92.100.1",
                    },
                ],
            },
        },
    },
}
sls_networks = [
    network[x] for network in [sls_input.get("Networks", {})] for x in network
]
