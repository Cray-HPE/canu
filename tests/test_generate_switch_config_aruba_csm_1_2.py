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
"""Test CANU generate switch config commands."""
import json
from os import path
from pathlib import Path

import pkg_resources
import requests
import responses
from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_1.1.5.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
custom_file_name = "aruba_custom.yaml"
custom_file = path.join(test_file_directory, "data", custom_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T53,J14,T34,J14,T27"
sls_file_name = "sls_input_file_csm_1.2.json"
sls_file = path.join(test_file_directory, "data", sls_file_name)

csm = "1.2"
switch_name = "sw-spine-001"
sls_address = "api-gw-service-nmn.local"

test_file_name_tds = "TDS_Architecture_Golden_Config_1.1.5.xlsx"
test_file_tds = path.join(test_file_directory, "data", test_file_name_tds)
architecture_tds = "TDS"
tabs_tds = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners_tds = "J14,T30,J14,T53,J14,T32,J14,T27"

canu_version = pkg_resources.get_distribution("canu").version
banner_motd = (
    "banner exec !\n"
    "###############################################################################\n"
    f"# CSM version:  {csm}\n"
    f"# CANU version: {canu_version}\n"
    "###############################################################################\n"
    "!\n"
)

runner = testing.CliRunner()


def test_switch_config_spine_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary spine config."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
        assert "hostname sw-spine-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        sw_spine_to_leaf = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-001:53<==sw-spine-001\n"
            + "    lag 101\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-002:53<==sw-spine-001\n"
            + "    lag 101\n"
            + "\n"
            + "interface lag 103 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-003:53<==sw-spine-001\n"
            + "    lag 103\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-004:53<==sw-spine-001\n"
            + "    lag 103\n"
        )
        assert sw_spine_to_leaf in str(result.output)

        spine_to_cdu = (
            "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    lag 201\n"
            + "\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:50<==sw-spine-001\n"
            + "    lag 201\n"
        )
        assert spine_to_cdu in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/30\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.0/31\n"
            + "interface 1/1/31\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/32\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role primary\n"
            + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.2/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.2/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "ip dns server-address 10.92.100.225\n"
        ) in str(result.output)

        assert (
            "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
        ) in str(result.output)

        assert (
            "route-map ncn-w001 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.4\n"
            + "\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.5\n"
            + "\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.6\n"
            + "\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.2\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.2\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.2\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.3 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "        neighbor 192.168.3.3 activate\n"
            + "        neighbor 192.168.4.4 activate\n"
            + "        neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "        neighbor 192.168.4.5 activate\n"
            + "        neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "        neighbor 192.168.4.6 activate\n"
            + "        neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "        bgp router-id 10.2.0.2\n"
            + "        maximum-paths 8\n"
            + "        timers bgp 1 3\n"
            + "        distance bgp 20 70\n"
            + "        neighbor 192.168.12.3 remote-as 65533\n"
            + "        neighbor 192.168.12.4 remote-as 65532\n"
            + "        neighbor 192.168.12.4 passive\n"
            + "        neighbor 192.168.12.5 remote-as 65532\n"
            + "        neighbor 192.168.12.5 passive\n"
            + "        neighbor 192.168.12.6 remote-as 65532\n"
            + "        neighbor 192.168.12.6 passive\n"
            + "        address-family ipv4 unicast\n"
            + "            neighbor 192.168.12.3 activate\n"
            + "            neighbor 192.168.12.4 activate\n"
            + "            neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "            neighbor 192.168.12.5 activate\n"
            + "            neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "            neighbor 192.168.12.6 activate\n"
            + "            neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "        exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_spine_primary_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid primary spine config."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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

        assert banner_motd in str(result.output)

        assert (
            "# ip route 0.0.0.0/0 10.103.15.185\n"
            + "# interface 1/1/36\n"
            + "#   no shutdown\n"
            + "#   ip address 10.103.15.186/30\n"
            + "#   exit\n"
            + "# interface 1/1/1\n"
            + "#   ip address 10.103.15.10/30\n"
            + "#   exit\n"
            + "# system interface-group 3 speed 10g\n"
            + "# interface 1/1/20\n"
            + "#   no shutdown\n"
            + "#   mtu 9198\n"
            + "#   description ion-node<==sw-spine-001\n"
            + "#   no routing\n"
            + "#   vlan access 7\n"
            + "#   spanning-tree bpdu-guard\n"
            + "#   spanning-tree port-type admin-edge\n"
        ) in str(result.output)

        assert (
            "hostname sw-spine-001\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        sw_spine_to_leaf = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 103 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
        )
        assert sw_spine_to_leaf in str(result.output)

        output = (
            "ip dns server-address 10.92.100.225\n"
            + "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
            + "ip route 0.0.0.0/0 10.103.15.185\n"
            + "route-map ncn-w001 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.4\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.5\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.6\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
        )
        assert output in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "system interface-group 3 speed 10g\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.2/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.2/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role primary\n"
            + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-002:53<==sw-spine-001\n"
            + "    lag 101\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-003:53<==sw-spine-001\n"
            + "    lag 103\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-004:53<==sw-spine-001\n"
            + "    lag 103\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    lag 201\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:50<==sw-spine-001\n"
            + "    lag 201\n"
            + "interface 1/1/30\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.0/31\n"
            + "interface 1/1/31\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/32\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/36\n"
            + "    no shutdown\n"
            + "    ip address 10.103.15.186/30\n"
            + "    exit\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    ip address 10.103.15.10/30\n"
            + "    exit\n"
            + "interface 1/1/20\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ion-node<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan access 7\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.2\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.2\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.2\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.3 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "      neighbor 192.168.3.3 activate\n"
            + "      neighbor 192.168.4.4 activate\n"
            + "      neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "      neighbor 192.168.4.5 activate\n"
            + "      neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "      neighbor 192.168.4.6 activate\n"
            + "      neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "      bgp router-id 10.2.0.2\n"
            + "      maximum-paths 8\n"
            + "      timers bgp 1 3\n"
            + "      distance bgp 20 70\n"
            + "      neighbor 192.168.12.3 remote-as 65533\n"
            + "      neighbor 192.168.12.4 remote-as 65532\n"
            + "      neighbor 192.168.12.4 passive\n"
            + "      neighbor 192.168.12.5 remote-as 65532\n"
            + "      neighbor 192.168.12.5 passive\n"
            + "      neighbor 192.168.12.6 remote-as 65532\n"
            + "      neighbor 192.168.12.6 passive\n"
            + "      address-family ipv4 unicast\n"
            + "        neighbor 192.168.12.3 activate\n"
            + "        neighbor 192.168.12.4 activate\n"
            + "        neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "        neighbor 192.168.12.5 activate\n"
            + "        neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "        neighbor 192.168.12.6 activate\n"
            + "        neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "      exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_spine_secondary_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid primary spine config."""
    with runner.isolated_filesystem():
        spine_secondary = "sw-spine-002"
        result = runner.invoke(
            cli,
            [
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
                "--custom-config",
                custom_file,
            ],
        )
        assert result.exit_code == 0
        assert banner_motd in str(result.output)

        assert (
            "# ip route 0.0.0.0/0 10.103.15.189\n"
            + "# interface 1/1/36\n"
            + "#   no shutdown\n"
            + "#   ip address 10.103.15.190/30\n"
            + "#   exit\n"
            + "# system interface-group 3 speed 10g\n"
            + "# interface 1/1/20\n"
            + "#   no shutdown\n"
            + "#   mtu 9198\n"
            + "#   description ion-node<==sw-spine-002\n"
            + "#   no routing\n"
            + "#   vlan access 7\n"
            + "#   spanning-tree bpdu-guard\n"
            + "#   spanning-tree port-type admin-edge\n"
        ) in str(result.output)

        assert (
            "hostname sw-spine-002\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        sw_spine_to_leaf = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 103 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
        )
        assert sw_spine_to_leaf in str(result.output)

        output = (
            "ip dns server-address 10.92.100.225\n"
            + "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
            + "ip route 0.0.0.0/0 10.103.15.189\n"
            + "route-map ncn-w001 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.4\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.5\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.4\n"
            + "    set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.5\n"
            + "    set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "    match ip address prefix-list tftp\n"
            + "    match ip next-hop 192.168.4.6\n"
            + "    set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "    match ip address prefix-list pl-hmn\n"
            + "    set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "    match ip address prefix-list pl-nmn\n"
            + "    set ip next-hop 192.168.4.6\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "    match ip address prefix-list pl-can\n"
            + "    set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "    match ip address prefix-list pl-cmn\n"
        )
        assert output in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "system interface-group 3 speed 10g\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.3/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.3/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role secondary\n"
            + "    keepalive peer 192.168.255.0 source 192.168.255.1 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-001:52<==sw-spine-002\n"
            + "    lag 101\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-002:52<==sw-spine-002\n"
            + "    lag 101\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-003:52<==sw-spine-002\n"
            + "    lag 103\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-004:52<==sw-spine-002\n"
            + "    lag 103\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    lag 201\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:49<==sw-spine-002\n"
            + "    lag 201\n"
            + "interface 1/1/30\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.1/31\n"
            + "interface 1/1/31\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/32\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/36\n"
            + "    no shutdown\n"
            + "    ip address 10.103.15.190/30\n"
            + "    exit\n"
            + "interface 1/1/20\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ion-node<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan access 7\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.3\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.3\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.3\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.2 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "      neighbor 192.168.3.2 activate\n"
            + "      neighbor 192.168.4.4 activate\n"
            + "      neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "      neighbor 192.168.4.5 activate\n"
            + "      neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "      neighbor 192.168.4.6 activate\n"
            + "      neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "      bgp router-id 10.2.0.3\n"
            + "      maximum-paths 8\n"
            + "      timers bgp 1 3\n"
            + "      distance bgp 20 70\n"
            + "      neighbor 192.168.12.2 remote-as 65533\n"
            + "      neighbor 192.168.12.4 remote-as 65532\n"
            + "      neighbor 192.168.12.4 passive\n"
            + "      neighbor 192.168.12.5 remote-as 65532\n"
            + "      neighbor 192.168.12.5 passive\n"
            + "      neighbor 192.168.12.6 remote-as 65532\n"
            + "      neighbor 192.168.12.6 passive\n"
            + "      address-family ipv4 unicast\n"
            + "        neighbor 192.168.12.2 activate\n"
            + "        neighbor 192.168.12.4 activate\n"
            + "        neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "        neighbor 192.168.12.5 activate\n"
            + "        neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "        neighbor 192.168.12.6 activate\n"
            + "        neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "      exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_spine_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary spine config."""
    spine_secondary = "sw-spine-002"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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

        assert "hostname sw-spine-002\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        sw_spine_to_leaf = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-001:52<==sw-spine-002\n"
            + "    lag 101\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-002:52<==sw-spine-002\n"
            + "    lag 101\n"
            + "\n"
            + "interface lag 103 multi-chassis\n"
            + "    no shutdown\n"
            + "    description spine_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-003:52<==sw-spine-002\n"
            + "    lag 103\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-004:52<==sw-spine-002\n"
            + "    lag 103\n"
        )
        assert sw_spine_to_leaf in str(result.output)

        spine_to_cdu = (
            "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    lag 201\n"
            + "\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:49<==sw-spine-002\n"
            + "    lag 201\n"
        )
        assert spine_to_cdu in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/30\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.1/31\n"
            + "interface 1/1/31\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/32\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role secondary\n"
            + "    keepalive peer 192.168.255.0 source 192.168.255.1 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.3/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.3/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "ip dns server-address 10.92.100.225\n"
        ) in str(result.output)

        assert (
            "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
        ) in str(result.output)

        assert (
            "route-map ncn-w001 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.4\n"
            + "\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.5\n"
            + "\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.6\n"
            + "\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.3\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.3\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.3\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.2 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "        neighbor 192.168.3.2 activate\n"
            + "        neighbor 192.168.4.4 activate\n"
            + "        neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "        neighbor 192.168.4.5 activate\n"
            + "        neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "        neighbor 192.168.4.6 activate\n"
            + "        neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "        bgp router-id 10.2.0.3\n"
            + "        maximum-paths 8\n"
            + "        timers bgp 1 3\n"
            + "        distance bgp 20 70\n"
            + "        neighbor 192.168.12.2 remote-as 65533\n"
            + "        neighbor 192.168.12.4 remote-as 65532\n"
            + "        neighbor 192.168.12.4 passive\n"
            + "        neighbor 192.168.12.5 remote-as 65532\n"
            + "        neighbor 192.168.12.5 passive\n"
            + "        neighbor 192.168.12.6 remote-as 65532\n"
            + "        neighbor 192.168.12.6 passive\n"
            + "        address-family ipv4 unicast\n"
            + "            neighbor 192.168.12.2 activate\n"
            + "            neighbor 192.168.12.4 activate\n"
            + "            neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "            neighbor 192.168.12.5 activate\n"
            + "            neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "            neighbor 192.168.12.6 activate\n"
            + "            neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "        exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_leaf_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary leaf config."""
    leaf_primary = "sw-leaf-001"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                leaf_primary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-leaf-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "ssh server vrf Customer\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        ncn_m = (
            "interface lag 1 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m001:ocp:1<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:ocp:1<==sw-leaf-001\n"
            + "    lag 1\n"
            + "\n"
            + "interface lag 3 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m002:ocp:1<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:ocp:1<==sw-leaf-001\n"
            + "    lag 3\n"
        )
        assert ncn_m in str(result.output)

        ncn_w = (
            "interface lag 5 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w001:ocp:1<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:ocp:1<==sw-leaf-001\n"
            + "    lag 5\n"
        )
        assert ncn_w in str(result.output)

        ncn_s = (
            "interface lag 7 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:ocp:1<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:ocp:1<==sw-leaf-001\n"
            + "    lag 7\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:ocp:2<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:ocp:2<==sw-leaf-001\n"
            + "    lag 8\n"
            + "\n"
            + "interface lag 9 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:ocp:1<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:ocp:1<==sw-leaf-001\n"
            + "    lag 9\n"
            + "\n"
            + "interface lag 10 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:ocp:2<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:ocp:2<==sw-leaf-001\n"
            + "    lag 10\n"
        )
        assert ncn_s in str(result.output)

        leaf_to_leaf_bmc = (
            "interface lag 151 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-leaf-bmc-001:48<==sw-leaf-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-bmc-001:48<==sw-leaf-001\n"
            + "    lag 151\n"
        )
        assert leaf_to_leaf_bmc in str(result.output)

        leaf_to_spine = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description leaf_to_spines_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/52\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-002:1<==sw-leaf-001\n"
            + "    lag 101\n"
            + "\n"
            + "interface 1/1/53\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-001:1<==sw-leaf-001\n"
            + "    lag 101\n"
        )
        assert leaf_to_spine in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/54\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.0/31\n"
            + "interface 1/1/55\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/56\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:01:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role primary\n"
            + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.4/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.4/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.4/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
        ) in str(result.output)

        assert (
            "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.4/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.4/24\n"
            + "    ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.4\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.4\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_leaf_primary_to_uan():
    """Test that the `canu generate switch config` command runs and returns valid primary leaf config."""
    leaf_primary_3 = "sw-leaf-003"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                leaf_primary_3,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-leaf-003\n" in str(result.output)

        uan = (
            "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:ocp:1<==sw-leaf-003\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    description uan001:ocp:2<==sw-leaf-003\n"
            + "    no routing\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "    no shutdown\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 6\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:ocp:2<==sw-leaf-003\n"
            + "    lag 8\n"
        )
        assert uan in str(result.output)


def test_switch_config_leaf_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary leaf config."""
    leaf_secondary = "sw-leaf-002"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                leaf_secondary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-leaf-002\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "ssh server vrf Customer\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        ncn_m = (
            "interface lag 1 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m001:pcie-slot1:1<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:pcie-slot1:1<==sw-leaf-002\n"
            + "    lag 1\n"
            + "\n"
            + "interface lag 3 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m002:pcie-slot1:1<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:pcie-slot1:1<==sw-leaf-002\n"
            + "    lag 3\n"
        )
        assert ncn_m in str(result.output)

        ncn_w = (
            "interface lag 5 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w001:ocp:2<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:ocp:2<==sw-leaf-002\n"
            + "    lag 5\n"
        )
        assert ncn_w in str(result.output)

        ncn_s = (
            "interface lag 7 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:pcie-slot1:1<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:pcie-slot1:1<==sw-leaf-002\n"
            + "    lag 7\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:pcie-slot1:2<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:pcie-slot1:2<==sw-leaf-002\n"
            + "    lag 8\n"
            + "\n"
            + "interface lag 9 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:pcie-slot1:1<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:pcie-slot1:1<==sw-leaf-002\n"
            + "    lag 9\n"
            + "\n"
            + "interface lag 10 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:pcie-slot1:2<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:pcie-slot1:2<==sw-leaf-002\n"
            + "    lag 10\n"
        )
        assert ncn_s in str(result.output)

        leaf_to_leaf_bmc = (
            "interface lag 151 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-leaf-bmc-001:47<==sw-leaf-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-bmc-001:47<==sw-leaf-002\n"
            + "    lag 151\n"
        )
        assert leaf_to_leaf_bmc in str(result.output)

        leaf_to_spine = (
            "interface lag 101 multi-chassis\n"
            + "    no shutdown\n"
            + "    description leaf_to_spines_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/52\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-002:2<==sw-leaf-002\n"
            + "    lag 101\n"
            + "\n"
            + "interface 1/1/53\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-001:2<==sw-leaf-002\n"
            + "    lag 101\n"
        )
        assert leaf_to_spine in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/54\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.1/31\n"
            + "interface 1/1/55\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/56\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:01:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role secondary\n"
            + "    keepalive peer 192.168.255.0 source 192.168.255.1 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.5/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.5/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.5/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.5/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.5/24\n"
            + "    ip ospf 2 area 0.0.0.0\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.5\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.5\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_leaf_secondary_to_uan():
    """Test that the `canu generate switch config` command runs and returns valid secondary leaf config."""
    leaf_secondary_3 = "sw-leaf-004"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                leaf_secondary_3,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-leaf-004\n" in str(result.output)

        uan = (
            "interface 1/1/7\n"
            + "    mtu 9198\n"
            + "    description uan001:pcie-slot1:1<==sw-leaf-004\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    description uan001:pcie-slot1:2<==sw-leaf-004\n"
            + "    no routing\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "    no shutdown\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 6\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:pcie-slot1:2<==sw-leaf-004\n"
            + "    lag 8\n"
        )
        assert uan in str(result.output)


def test_switch_config_cdu_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary cdu config."""
    cdu_primary = "sw-cdu-001"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
        assert "hostname sw-cdu-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf keepalive\n"
            + "vrf Customer\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        cmm = (
            "interface lag 2 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-000:1<==sw-cdu-001\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-000:1<==sw-cdu-001\n"
            + "    lag 2\n"
            + "interface lag 3 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-001:1<==sw-cdu-001\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-001:1<==sw-cdu-001\n"
            + "    lag 3\n"
            + "interface lag 4 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-002:1<==sw-cdu-001\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-002:1<==sw-cdu-001\n"
            + "    lag 4\n"
            + "interface lag 5 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-003:1<==sw-cdu-001\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-003:1<==sw-cdu-001\n"
            + "    lag 5\n"
        )
        assert cmm in str(result.output)

        cec = (
            "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cec-x3002-000:1<==sw-cdu-001\n"
            + "    no routing\n"
            + "    vlan access 3000\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        )
        assert cec in str(result.output)

        cdu_to_spine = (
            "interface lag 255 multi-chassis\n"
            + "    no shutdown\n"
            + "    description cdu_to_spines_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/49\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-002:5<==sw-cdu-001\n"
            + "    lag 255\n"
            + "\n"
            + "interface 1/1/50\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-001:5<==sw-cdu-001\n"
            + "    lag 255\n"
        )
        assert cdu_to_spine in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/48\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.0/31\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/52\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:02:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role primary\n"
            + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.16/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.16/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
        ) in str(result.output)

        mtn_hmn_vlan = (
            "vlan 3000\n"
            + "    name cabinet_3002_hmn\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "\n"
            + "interface vlan 3000\n"
            + "    description cabinet_3002_hmn\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.104.2/22\n"
            + "    active-gateway ip mac 12:00:00:00:73:00\n"
            + "    active-gateway ip 192.168.104.1\n"
            + "    ipv6 address autoconfig\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
        )
        assert mtn_hmn_vlan in str(result.output)

        mtn_nmn_vlan = (
            "vlan 2000\n"
            + "    name cabinet_3002_nmn\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "\n"
            + "interface vlan 2000\n"
            + "    description cabinet_3002_nmn\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.100.2/22\n"
            + "    active-gateway ip mac 12:00:00:00:73:00\n"
            + "    active-gateway ip 192.168.100.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
        )
        assert mtn_nmn_vlan in str(result.output)

        assert (
            "ip dns server-address 10.92.100.225\n"
            + "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.16\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.16\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_cdu_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary cdu config."""
    cdu_secondary = "sw-cdu-002"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
        assert "hostname sw-cdu-002\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf keepalive\n"
            + "vrf Customer\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        cmm = (
            "interface lag 2 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-000:2<==sw-cdu-002\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-000:2<==sw-cdu-002\n"
            + "    lag 2\n"
            + "interface lag 3 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-001:2<==sw-cdu-002\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-001:2<==sw-cdu-002\n"
            + "    lag 3\n"
            + "interface lag 4 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-002:2<==sw-cdu-002\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-002:2<==sw-cdu-002\n"
            + "    lag 4\n"
            + "interface lag 5 multi-chassis static\n"
            + "    no shutdown\n"
            + "    description cmm-x3002-003:2<==sw-cdu-002\n"
            + "    no routing\n"
            + "    vlan trunk native 2000\n"
            + "    vlan trunk allowed 2000,3000\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cmm-x3002-003:2<==sw-cdu-002\n"
            + "    lag 5\n"
        )
        assert cmm in str(result.output)

        cdu_to_spine = (
            "interface lag 255 multi-chassis\n"
            + "    no shutdown\n"
            + "    description cdu_to_spines_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/49\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-002:6<==sw-cdu-002\n"
            + "    lag 255\n"
            + "\n"
            + "interface 1/1/50\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-001:6<==sw-cdu-002\n"
            + "    lag 255\n"
        )
        assert cdu_to_spine in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/48\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.1/31\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/52\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:02:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role secondary\n"
            + "    keepalive peer 192.168.255.0 source 192.168.255.1 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.17/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.17/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
        ) in str(result.output)

        mtn_hmn_vlan = (
            "vlan 3000\n"
            + "    name cabinet_3002_hmn\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "\n"
            + "interface vlan 3000\n"
            + "    description cabinet_3002_hmn\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.104.3/22\n"
            + "    active-gateway ip mac 12:00:00:00:73:00\n"
            + "    active-gateway ip 192.168.104.1\n"
            + "    ipv6 address autoconfig\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
        )
        assert mtn_hmn_vlan in str(result.output)

        mtn_nmn_vlan = (
            "vlan 2000\n"
            + "    name cabinet_3002_nmn\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "\n"
            + "interface vlan 2000\n"
            + "    description cabinet_3002_nmn\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.100.3/22\n"
            + "    active-gateway ip mac 12:00:00:00:73:00\n"
            + "    active-gateway ip 192.168.100.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
        )
        assert mtn_nmn_vlan in str(result.output)

        assert (
            "ip dns server-address 10.92.100.225\n"
            + "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.17\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.17\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_leaf_bmc():
    """Test that the `canu generate switch config` command runs and returns valid leaf-bmc config."""
    leaf_bmc = "sw-leaf-bmc-001"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
        assert "hostname sw-leaf-bmc-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf default\n"
            + "ssh server vrf mgmt\n"
            + "ssh server vrf Customer\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        compute_leaf_bmc = (
            "interface 1/1/24\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn001:onboard:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/25\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn002:onboard:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/26\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn003:onboard:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/27\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn004:onboard:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        )
        assert compute_leaf_bmc in str(result.output)
        bmc = (
            "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        )
        assert bmc in str(result.output)
        leaf_bmc_to_leaf = (
            "interface lag 255\n"
            + "    no shutdown\n"
            + "    description leaf_bmc_to_leaf_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/47\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-002:51<==sw-leaf-bmc-001\n"
            + "    lag 255\n"
            + "\n"
            + "interface 1/1/48\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-001:51<==sw-leaf-bmc-001\n"
            + "    lag 255\n"
        )
        assert leaf_bmc_to_leaf in str(result.output)

        assert (
            "interface loopback 0\n"
            + "    ip address 10.2.0.12/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.12/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.12/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.12/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.12/24\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "snmp-server vrf default\n"
            + "ip dns server-address 10.92.100.225\n"
            + "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.12\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.12\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_csi_file_missing():
    """Test that the `canu generate switch config` command errors on sls_file.json file missing."""
    bad_sls_file = "/bad_file.json"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
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
                bad_sls_file,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 2
        assert "No such file or directory" in str(result.output)


def test_switch_config_missing_file():
    """Test that the `canu generate switch config` command fails on missing file."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
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
        assert result.exit_code == 2

        assert (
            "Error: Missing one of the required mutually exclusive options from 'Network input source' option group:\n"
            "  '--ccj'\n"
            "  '--shcd'\n"
        ) in str(result.output)


def test_switch_config_bad_file():
    """Test that the `canu generate switch config` command fails on bad file."""
    bad_file = "does_not_exist.xlsx"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--shcd",
                bad_file,
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
        assert result.exit_code == 2
        assert "Error: Invalid value for '--shcd':" in str(result.output)


def test_switch_config_missing_tabs():
    """Test that the `canu generate switch config` command prompts for missing tabs."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
            ],
            input="SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES\n",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)


def test_switch_config_bad_tab():
    """Test that the `canu generate switch config` command fails on bad tab name."""
    bad_tab = "BAD_TAB_NAME"
    bad_tab_corners = "I14,S48"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                bad_tab,
                "--corners",
                bad_tab_corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 1
        assert f"Tab BAD_TAB_NAME not found in {test_file}" in str(result.output)


def test_switch_config_switch_name_prompt():
    """Test that the `canu generate switch config` command prompts for missing switch name."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
            ],
            input="sw-spine-001\n",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)
        assert "ntp server 192.168.4.4" in str(result.output)
        assert "ntp server 192.168.4.5" in str(result.output)
        assert "ntp server 192.168.4.6" in str(result.output)
        assert "deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0" in str(
            result.output,
        )
        assert "interface 1/1/30" in str(result.output)
        assert "interface 1/1/31" in str(result.output)
        assert "interface 1/1/32" in str(result.output)


def test_switch_config_corner_prompt():
    """Test that the `canu generate switch config` command prompts for corner input and runs."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
            ],
            input="J14\nT42\nJ14\nT48\nJ14\nT24\nJ14\nT23",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)
        assert "ntp server 192.168.4.4" in str(result.output)
        assert "ntp server 192.168.4.5" in str(result.output)
        assert "ntp server 192.168.4.6" in str(result.output)
        assert "deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0" in str(
            result.output,
        )
        assert "interface 1/1/30" in str(result.output)
        assert "interface 1/1/31" in str(result.output)
        assert "interface 1/1/32" in str(result.output)


def test_switch_config_not_enough_corners():
    """Test that the `canu generate switch config` command fails on not enough corners."""
    not_enough_corners = "H16"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
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
                not_enough_corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert "There were 1 corners entered, but there should be 8." in str(
            result.output,
        )


def test_switch_config_bad_switch_name_1():
    """Test that the `canu generate switch config` command fails on bad switch name."""
    bad_name_1 = "sw-bad"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                bad_name_1,
            ],
        )
        assert result.exit_code == 1

        assert (
            f"For switch {bad_name_1}, the type cannot be determined. Please check the switch name and try again."
            in str(result.output)
        )


def test_switch_config_bad_switch_name_2():
    """Test that the `canu generate switch config` command fails on bad switch name."""
    bad_name_2 = "sw-spine-999"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                bad_name_2,
            ],
        )
        assert result.exit_code == 1

        assert (
            f"For switch {bad_name_2}, the type cannot be determined. Please check the switch name and try again."
            in str(result.output)
        )


def test_switch_config_non_switch():
    """Test that the `canu generate switch config` command fails on non switch."""
    non_switch = "ncn-w001"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
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
                non_switch,
            ],
        )
        assert result.exit_code == 1

        assert f"{non_switch} is not a switch. Only switch config can be generated." in str(result.output)


@responses.activate
def test_switch_config_sls():
    """Test that the `canu generate switch config` command runs with SLS."""
    with runner.isolated_filesystem():

        with open(sls_file, "r") as read_file:
            sls_data = json.load(read_file)

        sls_networks = [network[x] for network in [sls_data.get("Networks", {})] for x in network]

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        result = runner.invoke(
            cli,
            [
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
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)
        assert "ntp server 192.168.4.4" in str(result.output)
        assert "ntp server 192.168.4.5" in str(result.output)
        assert "ntp server 192.168.4.6" in str(result.output)
        assert "deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0" in str(
            result.output,
        )
        assert "interface 1/1/30" in str(result.output)
        assert "interface 1/1/31" in str(result.output)
        assert "interface 1/1/32" in str(result.output)


@responses.activate
def test_switch_config_sls_token_bad():
    """Test that the `canu generate switch config` command errors on bad token file."""
    bad_token = "bad_token.token"
    with runner.isolated_filesystem():
        with open(bad_token, "w") as f:
            f.write('{"access_token": "123"}')

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            body=requests.exceptions.HTTPError(
                "503 Server Error: Service Unavailable for url",
            ),
        )

        result = runner.invoke(
            cli,
            [
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
                "--name",
                switch_name,
                "--auth-token",
                bad_token,
            ],
        )
        assert result.exit_code == 0

        assert (
            "Error connecting SLS api-gw-service-nmn.local, check that the token is valid, or generate a new one"
            in str(result.output)
        )


@responses.activate
def test_switch_config_sls_token_missing():
    """Test that the `canu generate switch config` command errors on no token file."""
    bad_token = "no_token.token"

    result = runner.invoke(
        cli,
        [
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
            "--name",
            switch_name,
            "--auth-token",
            bad_token,
        ],
    )
    assert result.exit_code == 0
    assert "Invalid token file, generate another token or try again." in str(
        result.output,
    )


@responses.activate
def test_switch_config_sls_address_bad():
    """Test that the `canu generate switch config` command errors with bad SLS address."""
    bad_sls_address = "192.168.254.254"

    responses.add(
        responses.GET,
        f"https://{bad_sls_address}/apis/sls/v1/networks",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 51] Network is unreachable",
        ),
    )

    result = runner.invoke(
        cli,
        [
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
            "--name",
            switch_name,
            "--sls-address",
            bad_sls_address,
        ],
    )
    assert result.exit_code == 0
    assert (
        "Error connecting to SLS 192.168.254.254, check the address or pass in a new address using --sls-address."
        in str(result.output)
    )


# TDS Tests


def test_switch_config_tds_spine_primary():
    """Test that the `canu generate switch config` command runs and returns valid TDS primary spine config."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture_tds,
                "--shcd",
                test_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        ncn_m = (
            "interface lag 1 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m001:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:ocp:1<==sw-spine-001\n"
            + "    lag 1\n"
            + "\n"
            + "interface lag 2 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m002:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:ocp:1<==sw-spine-001\n"
            + "    lag 2\n"
            + "\n"
            + "interface lag 3 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m003:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m003:ocp:1<==sw-spine-001\n"
            + "    lag 3\n"
        )

        assert ncn_m in str(result.output)

        ncn_w = (
            "interface lag 4 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w001:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:ocp:1<==sw-spine-001\n"
            + "    lag 4\n"
            + "\n"
            + "interface lag 5 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w002:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w002:ocp:1<==sw-spine-001\n"
            + "    lag 5\n"
            + "\n"
            + "interface lag 6 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w003:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w003:ocp:1<==sw-spine-001\n"
            + "    lag 6\n"
        )

        assert ncn_w in str(result.output)

        ncn_s = (
            "interface lag 7 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:ocp:1<==sw-spine-001\n"
            + "    lag 7\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:ocp:2<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:ocp:2<==sw-spine-001\n"
            + "    lag 8\n"
            + "\n"
            + "interface lag 9 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:ocp:1<==sw-spine-001\n"
            + "    lag 9\n"
            + "\n"
            + "interface lag 10 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:ocp:2<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:ocp:2<==sw-spine-001\n"
            + "    lag 10\n"
            + "\n"
            + "interface lag 11 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s003:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/11\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:ocp:1<==sw-spine-001\n"
            + "    lag 11\n"
            + "\n"
            + "interface lag 12 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s003:ocp:2<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/12\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:ocp:2<==sw-spine-001\n"
            + "    lag 12\n"
        )

        assert ncn_s in str(result.output)

        uan = (
            "interface 1/1/13\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:ocp:1<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface lag 14 multi-chassis\n"
            + "    description uan001:ocp:2<==sw-spine-001\n"
            + "    no routing\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "    no shutdown\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 6\n"
            + "\n"
            + "interface 1/1/14\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:ocp:2<==sw-spine-001\n"
            + "    lag 14\n"
        )
        assert uan in str(result.output)

        sw_spine_to_leaf_bmc = (
            "interface lag 151 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-leaf-bmc-001:48<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-bmc-001:48<==sw-spine-001\n"
            + "    lag 151\n"
        )
        assert sw_spine_to_leaf_bmc in str(result.output)

        spine_to_cdu = (
            "interface 1/1/49\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:50<==sw-spine-001\n"
            + "    lag 201\n"
            + "\n"
            + "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/50\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:50<==sw-spine-001\n"
            + "    lag 201\n"
        )
        assert spine_to_cdu in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/54\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.0/31\n"
            + "interface 1/1/55\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/56\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role primary\n"
            + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.2/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.2/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.2/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.2/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "ip dns server-address 10.92.100.225\n"
        ) in str(result.output)

        assert (
            "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
        ) in str(result.output)

        assert (
            "route-map ncn-w001 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.4\n"
            + "\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.5\n"
            + "\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.6\n"
            + "\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.2\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.2\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.2\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.3 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "        neighbor 192.168.3.3 activate\n"
            + "        neighbor 192.168.4.4 activate\n"
            + "        neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "        neighbor 192.168.4.5 activate\n"
            + "        neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "        neighbor 192.168.4.6 activate\n"
            + "        neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "        bgp router-id 10.2.0.2\n"
            + "        maximum-paths 8\n"
            + "        timers bgp 1 3\n"
            + "        distance bgp 20 70\n"
            + "        neighbor 192.168.12.3 remote-as 65533\n"
            + "        neighbor 192.168.12.4 remote-as 65532\n"
            + "        neighbor 192.168.12.4 passive\n"
            + "        neighbor 192.168.12.5 remote-as 65532\n"
            + "        neighbor 192.168.12.5 passive\n"
            + "        neighbor 192.168.12.6 remote-as 65532\n"
            + "        neighbor 192.168.12.6 passive\n"
            + "        address-family ipv4 unicast\n"
            + "            neighbor 192.168.12.3 activate\n"
            + "            neighbor 192.168.12.4 activate\n"
            + "            neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "            neighbor 192.168.12.5 activate\n"
            + "            neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "            neighbor 192.168.12.6 activate\n"
            + "            neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "        exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_tds_spine_secondary():
    """Test that the `canu generate switch config` command runs and returns valid TDS secondary spine config."""
    spine_secondary = "sw-spine-002"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture_tds,
                "--shcd",
                test_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                spine_secondary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-002\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "vrf keepalive\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert (
            "ssh server vrf Customer\n"
            + "ssh server vrf default\n"
            + "ssh server vrf keepalive\n"
            + "ssh server vrf mgmt\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "vlan 7\n"
            + "    name CAN\n"
            + "vlan 10\n"
            + "    name SUN\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree priority 0\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)

        ncn_m = (
            "interface lag 1 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m001:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 1\n"
            + "\n"
            + "interface lag 2 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m002:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 2\n"
            + "\n"
            + "interface lag 3 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-m003:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m003:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 3\n"
        )

        assert ncn_m in str(result.output)

        ncn_w = (
            "interface lag 4 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w001:ocp:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:ocp:2<==sw-spine-002\n"
            + "    lag 4\n"
            + "\n"
            + "interface lag 5 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w002:ocp:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w002:ocp:2<==sw-spine-002\n"
            + "    lag 5\n"
            + "\n"
            + "interface lag 6 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-w003:ocp:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w003:ocp:2<==sw-spine-002\n"
            + "    lag 6\n"
        )

        assert ncn_w in str(result.output)

        ncn_s = (
            "interface lag 7 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 7\n"
            + "\n"
            + "interface lag 8 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s001:pcie-slot1:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:pcie-slot1:2<==sw-spine-002\n"
            + "    lag 8\n"
            + "\n"
            + "interface lag 9 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 9\n"
            + "\n"
            + "interface lag 10 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s002:pcie-slot1:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:pcie-slot1:2<==sw-spine-002\n"
            + "    lag 10\n"
            + "\n"
            + "interface lag 11 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s003:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6-7\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/11\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:pcie-slot1:1<==sw-spine-002\n"
            + "    lag 11\n"
            + "\n"
            + "interface lag 12 multi-chassis\n"
            + "    no shutdown\n"
            + "    description ncn-s003:pcie-slot1:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 10\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface 1/1/12\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:pcie-slot1:2<==sw-spine-002\n"
            + "    lag 12\n"
        )

        assert ncn_s in str(result.output)

        uan = (
            "interface 1/1/13\n"
            + "    mtu 9198\n"
            + "    description uan001:pcie-slot1:1<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan access 2\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "\n"
            + "interface lag 14 multi-chassis\n"
            + "    description uan001:pcie-slot1:2<==sw-spine-002\n"
            + "    no routing\n"
            + "    lacp mode active\n"
            + "    lacp fallback\n"
            + "    spanning-tree port-type admin-edge\n"
            + "    no shutdown\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 6\n"
            + "\n"
            + "interface 1/1/14\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:pcie-slot1:2<==sw-spine-002\n"
            + "    lag 14\n"
        )
        assert uan in str(result.output)

        sw_spine_to_leaf_bmc = (
            "interface lag 151 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-leaf-bmc-001:47<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "\n"
            + "interface 1/1/51\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-leaf-bmc-001:47<==sw-spine-002\n"
            + "    lag 151\n"
        )
        assert sw_spine_to_leaf_bmc in str(result.output)

        spine_to_cdu = (
            "interface 1/1/49\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-002:49<==sw-spine-002\n"
            + "    lag 201\n"
            + "\n"
            + "interface lag 201 multi-chassis\n"
            + "    no shutdown\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "    spanning-tree root-guard\n"
            + "\n"
            + "interface 1/1/50\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-cdu-001:49<==sw-spine-002\n"
            + "    lag 201\n"
        )
        assert spine_to_cdu in str(result.output)

        assert (
            "interface lag 256\n"
            + "    no shutdown\n"
            + "    description ISL link\n"
            + "    no routing\n"
            + "    vlan trunk native 1 tag\n"
            + "    vlan trunk allowed all\n"
            + "    lacp mode active\n"
            + "interface 1/1/54\n"
            + "    no shutdown\n"
            + "    vrf attach keepalive\n"
            + "    description VSX keepalive\n"
            + "    ip address 192.168.255.1/31\n"
            + "interface 1/1/55\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "interface 1/1/56\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description vsx isl\n"
            + "    lag 256\n"
            + "vsx\n"
            + "    system-mac 02:00:00:00:01:00\n"
            + "    inter-switch-link lag 256\n"
            + "    role secondary\n"
            + "    keepalive peer 192.168.255.0 source 192.168.255.1 vrf keepalive\n"
            + "    linkup-delay-timer 600\n"
            + "    vsx-sync vsx-global\n"
            + "\n"
            + "interface loopback 0\n"
            + "    ip address 10.2.0.3/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.3/16\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.1.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.3.1\n"
            + "    ip helper-address 10.92.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.3/17\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.0.1\n"
            + "    ip helper-address 10.94.100.222\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.12.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "interface vlan 7\n"
            + "    vrf attach Customer\n"
            + "    description CAN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.11.3/24\n"
            + "    active-gateway ip mac 12:00:00:00:6b:00\n"
            + "    active-gateway ip 192.168.11.1\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "ip dns server-address 10.92.100.225\n"
        ) in str(result.output)

        assert (
            "ip prefix-list pl-cmn seq 10 permit 192.168.12.0/24 ge 24\n"
            + "ip prefix-list pl-can seq 20 permit 192.168.11.0/24 ge 24\n"
            + "ip prefix-list pl-hmn seq 30 permit 10.94.100.0/24 ge 24\n"
            + "ip prefix-list pl-nmn seq 40 permit 10.92.100.0/24 ge 24\n"
            + "ip prefix-list tftp seq 10 permit 10.92.100.60/32 ge 32 le 32\n"
            + "ip prefix-list tftp seq 20 permit 10.94.100.60/32 ge 32 le 32\n"
        ) in str(result.output)

        assert (
            "route-map ncn-w001 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w001 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w001 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w001 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.4\n"
            + "route-map ncn-w001 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.4\n"
            + "\n"
            + "route-map ncn-w001-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.4\n"
            + "route-map ncn-w001-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w002 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w002 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w002 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w002 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.5\n"
            + "route-map ncn-w002 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.5\n"
            + "\n"
            + "route-map ncn-w002-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.5\n"
            + "route-map ncn-w002-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
            + "\n"
            + "\n"
            + "route-map ncn-w003 permit seq 10\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.4\n"
            + "     set local-preference 1000\n"
            + "route-map ncn-w003 permit seq 20\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.5\n"
            + "     set local-preference 1100\n"
            + "route-map ncn-w003 permit seq 30\n"
            + "     match ip address prefix-list tftp\n"
            + "     match ip next-hop 192.168.4.6\n"
            + "     set local-preference 1200\n"
            + "route-map ncn-w003 permit seq 40\n"
            + "     match ip address prefix-list pl-hmn\n"
            + "     set ip next-hop 192.168.0.6\n"
            + "route-map ncn-w003 permit seq 50\n"
            + "     match ip address prefix-list pl-nmn\n"
            + "     set ip next-hop 192.168.4.6\n"
            + "\n"
            + "route-map ncn-w003-Customer permit seq 10\n"
            + "     match ip address prefix-list pl-can\n"
            + "     set ip next-hop 192.168.11.6\n"
            + "route-map ncn-w003-Customer permit seq 20\n"
            + "     match ip address prefix-list pl-cmn\n"
        ) in str(result.output)

        assert (
            "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.3\n"
            + "    default-information originate\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.3\n"
            + "    redistribute bgp\n"
            + "    area 0.0.0.0\n"
            + "\n"
            + "router bgp 65533\n"
            + "    bgp router-id 10.2.0.3\n"
            + "    maximum-paths 8\n"
            + "    timers bgp 1 3\n"
            + "    distance bgp 20 70\n"
            + "    neighbor 192.168.3.2 remote-as 65533\n"
            + "    neighbor 192.168.4.4 remote-as 65531\n"
            + "    neighbor 192.168.4.4 passive\n"
            + "    neighbor 192.168.4.5 remote-as 65531\n"
            + "    neighbor 192.168.4.5 passive\n"
            + "    neighbor 192.168.4.6 remote-as 65531\n"
            + "    neighbor 192.168.4.6 passive\n"
            + "    address-family ipv4 unicast\n"
            + "        neighbor 192.168.3.2 activate\n"
            + "        neighbor 192.168.4.4 activate\n"
            + "        neighbor 192.168.4.4 route-map ncn-w001 in\n"
            + "        neighbor 192.168.4.5 activate\n"
            + "        neighbor 192.168.4.5 route-map ncn-w002 in\n"
            + "        neighbor 192.168.4.6 activate\n"
            + "        neighbor 192.168.4.6 route-map ncn-w003 in\n"
            + "    exit-address-family\n"
            + "    vrf Customer\n"
            + "        bgp router-id 10.2.0.3\n"
            + "        maximum-paths 8\n"
            + "        timers bgp 1 3\n"
            + "        distance bgp 20 70\n"
            + "        neighbor 192.168.12.2 remote-as 65533\n"
            + "        neighbor 192.168.12.4 remote-as 65532\n"
            + "        neighbor 192.168.12.4 passive\n"
            + "        neighbor 192.168.12.5 remote-as 65532\n"
            + "        neighbor 192.168.12.5 passive\n"
            + "        neighbor 192.168.12.6 remote-as 65532\n"
            + "        neighbor 192.168.12.6 passive\n"
            + "        address-family ipv4 unicast\n"
            + "            neighbor 192.168.12.2 activate\n"
            + "            neighbor 192.168.12.4 activate\n"
            + "            neighbor 192.168.12.4 route-map ncn-w001-Customer in\n"
            + "            neighbor 192.168.12.5 activate\n"
            + "            neighbor 192.168.12.5 route-map ncn-w002-Customer in\n"
            + "            neighbor 192.168.12.6 activate\n"
            + "            neighbor 192.168.12.6 route-map ncn-w003-Customer in\n"
            + "        exit-address-family\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)


def test_switch_config_tds_leaf_bmc():
    """Test that the `canu generate switch config` command runs and returns valid tds leaf-bmc config."""
    leaf_bmc_tds = "sw-leaf-bmc-001"

    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture_tds,
                "--shcd",
                test_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                leaf_bmc_tds,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-leaf-bmc-001\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "no ip icmp redirect\n"
            + "vrf Customer\n"
            + "ntp server 192.168.4.4\n"
            + "ntp server 192.168.4.5\n"
            + "ntp server 192.168.4.6\n"
            + "ntp enable\n"
        ) in str(result.output)

        assert "ssh server vrf default\n" in str(result.output)
        assert banner_motd in str(result.output)

        assert (
            "ssh server vrf mgmt\n"
            + "ssh server vrf Customer\n"
            + "access-list ip mgmt\n"
            + "    10 comment ALLOW SSH, HTTPS, AND SNMP ON HMN SUBNET and CMN\n"
            + "    20 permit tcp 192.168.0.0/255.255.128.0 any eq ssh\n"
            + "    30 permit tcp 192.168.0.0/255.255.128.0 any eq https\n"
            + "    40 permit udp 192.168.0.0/255.255.128.0 any eq snmp\n"
            + "    50 permit udp 192.168.0.0/255.255.128.0 any eq snmp-trap\n"
            + "    60 permit tcp 192.168.12.0/255.255.255.0 any eq ssh\n"
            + "    70 permit tcp 192.168.12.0/255.255.255.0 any eq https\n"
            + "    80 permit udp 192.168.12.0/255.255.255.0 any eq snmp\n"
            + "    90 permit udp 192.168.12.0/255.255.255.0 any eq snmp-trap\n"
            + "    100 comment ALLOW SNMP FROM HMN METALLB SUBNET\n"
            + "    110 permit udp 10.94.100.0/255.255.255.0 any eq snmp\n"
            + "    120 permit udp 10.94.100.0/255.255.255.0 any eq snmp-trap\n"
            + "    130 comment BLOCK SSH, HTTPS, AND SNMP FROM EVERYWHERE ELSE\n"
            + "    140 deny tcp any any eq ssh\n"
            + "    150 deny tcp any any eq https\n"
            + "    160 deny udp any any eq snmp\n"
            + "    170 deny udp any any eq snmp-trap\n"
            + "    180 comment ALLOW ANYTHING ELSE\n"
            + "    190 permit any any any\n"
            + "access-list ip nmn-hmn\n"
            + "    10 deny any 192.168.3.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    20 deny any 192.168.0.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    30 deny any 192.168.3.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    40 deny any 192.168.0.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    50 deny any 192.168.100.0/255.255.128.0 192.168.0.0/255.255.128.0\n"
            + "    60 deny any 192.168.100.0/255.255.128.0 192.168.200.0/255.255.128.0\n"
            + "    70 deny any 192.168.200.0/255.255.128.0 192.168.3.0/255.255.128.0\n"
            + "    80 deny any 192.168.200.0/255.255.128.0 192.168.100.0/255.255.128.0\n"
            + "    90 permit any any any\n"
            + "access-list ip cmn-can\n"
            + "    10 deny any 192.168.12.0/255.255.255.0 192.168.11.0/255.255.255.0\n"
            + "    20 deny any 192.168.11.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    30 deny any 192.168.12.0/255.255.255.0 192.168.200.0/255.255.255.0\n"
            + "    40 deny any 192.168.200.0/255.255.255.0 192.168.12.0/255.255.255.0\n"
            + "    50 permit any any any\n"
            + "apply access-list ip mgmt control-plane vrf default\n"
            + "\n"
            + "vlan 1\n"
            + "vlan 2\n"
            + "    name NMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 4\n"
            + "    name HMN\n"
            + "    apply access-list ip nmn-hmn in\n"
            + "    apply access-list ip nmn-hmn out\n"
            + "vlan 6\n"
            + "    name CMN\n"
            + "\n"
            + "spanning-tree\n"
            + "spanning-tree forward-delay 4\n"
            + "spanning-tree config-name MST0\n"
            + "spanning-tree config-revision 1\n"
            + "interface mgmt\n"
            + "    shutdown\n"
            + "    ip dhcp\n"
        ) in str(result.output)
        leaf_bmc_to_leaf = (
            "interface lag 101\n"
            + "    no shutdown\n"
            + "    description leaf_bmc_to_spine_lag\n"
            + "    no routing\n"
            + "    vlan trunk native 1\n"
            + "    vlan trunk allowed 1-2,4,6\n"
            + "    lacp mode active\n"
            + "interface 1/1/47\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-002:51<==sw-leaf-bmc-001\n"
            + "    lag 101\n"
            + "interface 1/1/48\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description sw-spine-001:51<==sw-leaf-bmc-001\n"
            + "    lag 101\n"
        )
        assert leaf_bmc_to_leaf in str(result.output)

        bmc = (
            "interface 1/1/1\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/2\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/3\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-m003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/4\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/5\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/6\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-w003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/7\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/8\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/9\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description ncn-s003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/10\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description uan001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/11\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn001:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/12\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn002:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/13\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn003:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
            + "interface 1/1/14\n"
            + "    no shutdown\n"
            + "    mtu 9198\n"
            + "    description cn004:bmc:1<==sw-leaf-bmc-001\n"
            + "    no routing\n"
            + "    vlan access 4\n"
            + "    spanning-tree bpdu-guard\n"
            + "    spanning-tree port-type admin-edge\n"
        )
        assert bmc in str(result.output)

        assert (
            "interface loopback 0\n"
            + "    ip address 10.2.0.12/32\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 1\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.1.12/16\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 2\n"
            + "    description NMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.3.12/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "interface vlan 4\n"
            + "    description HMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.0.12/17\n"
            + "    ip ospf 1 area 0.0.0.0\n"
            + "    ip ospf passive\n"
            + "interface vlan 6\n"
            + "    vrf attach Customer\n"
            + "    description CMN\n"
            + "    ip mtu 9198\n"
            + "    ip address 192.168.12.12/24\n"
            + "    ip ospf 2 area 0.0.0.0\n"
            + "snmp-server vrf default\n"
            + "ip dns server-address 10.92.100.225\n"
            + "router ospf 2 vrf Customer\n"
            + "    router-id 10.2.0.12\n"
            + "    area 0.0.0.0\n"
            + "router ospf 1\n"
            + "    router-id 10.2.0.12\n"
            + "    area 0.0.0.0\n"
            + "https-server vrf Customer\n"
            + "https-server vrf default\n"
            + "https-server vrf mgmt\n"
        ) in str(result.output)
