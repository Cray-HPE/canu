"""Test CANU validate shcd commands."""
from unittest.mock import patch

import click.testing

from canu.cli import cli


def netmiko_mock(*args):
    """Mock netmiko command."""
    return switch_config


def netmiko_mock_addition(*args):
    """Mock netmiko command."""
    return switch_config + "extra line"


username = "admin"
password = "admin"
ip = "192.168.1.1"
credentials = {"username": username, "password": password}
shasta = "1.4"
cache_minutes = 0
config_file = "switch.cfg"
runner = click.testing.CliRunner()


@patch("canu.validate.config.config.netmiko_command", side_effect=netmiko_mock)
def test_validate_config(*args):
    """Test that the `canu validate config` command runs."""
    with runner.isolated_filesystem():
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--config",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Differences\n"
            "------------------------------------------------------------\n"
            "Total Deletions (-): 0\n"
            "Total Additions (+): 0\n"
        ) in str(result.output)


@patch("canu.validate.config.config.netmiko_command", side_effect=netmiko_mock_addition)
def test_validate_config_additions(*args):
    """Test that the `canu validate config` command runs and sees an addition."""
    switch_config2 = switch_config[:-4] + "ABC"
    with runner.isolated_filesystem():
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config2)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--config",
                config_file,
            ],
        )
        print(result.output)
        assert result.exit_code == 0
        assert (
            "Differences\n"
            "------------------------------------------------------------\n"
            "Total Deletions (-): 1\n"
            "Total Additions (+): 2\n"
        ) in str(result.output)


switch_config = (
    "hostname sw-spine-001\n"
    "bfd\n"
    "no ip icmp redirect\n"
    "vrf CAN\n"
    "vrf keepalive\n"
    "ntp server 192.168.4.4\n"
    "ntp server 192.168.4.5\n"
    "ntp server 192.168.4.6\n"
    "ntp enable\n"
    "\n"
    "\n"
    "\n"
    "ssh server vrf default\n"
    "ssh server vrf mgmt\n"
    "access-list ip nmn-hmn\n"
    "    deny any 192.168.3.0/17 192.168.0.0/17\n"
    "    deny any 192.168.3.0/17 192.168.200.0/17\n"
    "    deny any 192.168.0.0/17 192.168.3.0/17\n"
    "    deny any 192.168.0.0/17 192.168.100.0/17\n"
    "    deny any 192.168.100.0/17 192.168.0.0/17\n"
    "    deny any 192.168.100.0/17 192.168.200.0/17\n"
    "    deny any 192.168.200.0/17 192.168.3.0/17\n"
    "    deny any 192.168.200.0/17 192.168.100.0/17\n"
    "    permit any any any\n"
    "\n"
    "vlan 1\n"
    "vlan 2\n"
    "    name NMN\n"
    "    apply access-list ip nmn-hmn in\n"
    "    apply access-list ip nmn-hmn out\n"
    "vlan 4\n"
    "    name HMN\n"
    "    apply access-list ip nmn-hmn in\n"
    "    apply access-list ip nmn-hmn out\n"
    "vlan 7\n"
    "    name CAN\n"
    "vlan 10\n"
    "    name SUN\n"
    "spanning-tree\n"
    "spanning-tree priority 0\n"
    "spanning-tree config-name MST0\n"
    "spanning-tree config-revision 1\n"
    "interface mgmt\n"
    "    shutdown\n"
    "\n"
    "interface lag 101 multi-chassis\n"
    "    no shutdown\n"
    "    description spine_to_leaf_lag\n"
    "    no routing\n"
    "    vlan trunk native 1\n"
    "    vlan trunk allowed 2,4,7\n"
    "    lacp mode active\n"
    "    spanning-tree root-guard\n"
    "\n"
    "interface 1/1/1\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:1==>sw-leaf-001:53\n"
    "    lag 101\n"
    "\n"
    "interface 1/1/2\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:2==>sw-leaf-002:53\n"
    "    lag 101\n"
    "\n"
    "interface lag 103 multi-chassis\n"
    "    no shutdown\n"
    "    description spine_to_leaf_lag\n"
    "    no routing\n"
    "    vlan trunk native 1\n"
    "    vlan trunk allowed 2,4,7\n"
    "    lacp mode active\n"
    "    spanning-tree root-guard\n"
    "\n"
    "interface 1/1/3\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:3==>sw-leaf-003:53\n"
    "    lag 103\n"
    "\n"
    "interface 1/1/4\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:4==>sw-leaf-004:53\n"
    "    lag 103\n"
    "\n"
    "interface lag 201 multi-chassis\n"
    "    no shutdown\n"
    "    description sw-spine-001:5==>sw-cdu-001:49\n"
    "    no routing\n"
    "    vlan trunk native 1\n"
    "    vlan trunk allowed 2,4\n"
    "    lacp mode active\n"
    "    spanning-tree root-guard\n"
    "\n"
    "interface 1/1/5\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:5==>sw-cdu-001:49\n"
    "    lag 201\n"
    "\n"
    "interface 1/1/6\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description sw-spine-001:6==>sw-cdu-002:49\n"
    "    lag 201\n"
    "\n"
    "interface lag 256\n"
    "    no shutdown\n"
    "    description ISL link\n"
    "    no routing\n"
    "    vlan trunk native 1 tag\n"
    "    vlan trunk allowed all\n"
    "    lacp mode active\n"
    "interface 1/1/30\n"
    "    no shutdown\n"
    "    vrf attach keepalive\n"
    "    ip address 192.168.255.0/31\n"
    "interface 1/1/31\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description vsx isl\n"
    "    lag 256\n"
    "interface 1/1/32\n"
    "    no shutdown\n"
    "    mtu 9198\n"
    "    description vsx isl\n"
    "    lag 256\n"
    "interface loopback 0\n"
    "    ip address 10.2.0.2/32\n"
    "    ip ospf 1 area 0.0.0.0\n"
    "interface vlan 1\n"
    "    ip mtu 9198\n"
    "    ip address 192.168.1.2\n"
    "    active-gateway ip mac 12:00:00:00:6b:00\n"
    "    active-gateway ip 192.168.1.1\n"
    "    ip helper-address 10.92.100.222\n"
    "interface vlan 2\n"
    "    ip mtu 9198\n"
    "    ip address 192.168.3.2\n"
    "    active-gateway ip mac 12:00:00:00:6b:00\n"
    "    active-gateway ip 192.168.3.1\n"
    "    ip helper-address 10.92.100.222\n"
    "    ip ospf 1 area 0.0.0.0\n"
    "interface vlan 4\n"
    "    ip mtu 9198\n"
    "    ip address 10.254.0.2\n"
    "    active-gateway ip mac 12:00:00:00:6b:00\n"
    "    active-gateway ip 10.254.0.1\n"
    "    ip helper-address 10.92.100.222\n"
    "    ip ospf 1 area 0.0.0.0\n"
    "interface vlan 7\n"
    "    ip mtu 9198\n"
    "    ip address 192.168.11.2\n"
    "    active-gateway ip mac 12:00:00:00:6b:00\n"
    "    active-gateway ip 192.168.11.1\n"
    "    ip helper-address 10.92.100.222\n"
    "vsx\n"
    "    system-mac 02:00:00:00:6b:00\n"
    "    inter-switch-link lag 256\n"
    "    role primary\n"
    "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
    "    linkup-delay-timer 600\n"
    "    vsx-sync vsx-global\n"
    "router ospf 1\n"
    "    router-id 10.2.0.2/32\n"
    "    area 0.0.0.0\n"
    "router ospfv3 1\n"
    "    router-id 10.2.0.2/32\n"
    "    area 0.0.0.0\n"
    "https-server vrf default\n"
    "https-server vrf mgmt\n"
    "https-server vrf CAN\n"
)
