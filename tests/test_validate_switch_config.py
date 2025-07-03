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
"""Test CANU validate switch config commands."""
from os import urandom
from unittest.mock import patch

from click import testing
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException

from canu.cli import cli

username = "admin"
password = "admin"
ip = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
credentials = {"username": username, "password": password}
generated_config_file = "switch.cfg"
mellanox_generated_config_file = "mellanox_switch.cfg"
running_config_file = "running_switch.cfg"
mellanox_running_config_file = "mellanox_running_switch.cfg"
runner = testing.CliRunner()


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command runs."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert ("- nae-script abc\n" + "+ router add\n") in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_additions(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config2)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert (
            "- hostname sw-spine-001\n"
            + "- spanning-tree priority 0\n"
            + "- interface lag 101 multi-chassis\n"
            + "  - no shutdown\n"
            + "  - description spine_to_leaf_lag\n"
            + "  - no routing\n"
            + "  - vlan trunk native 1\n"
            + "  - vlan trunk allowed 2,4,7\n"
            + "  - lacp mode active\n"
            + "  - spanning-tree root-guard\n"
            + "interface 1/1/1\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "interface 1/1/2\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "- interface 1/1/6\n"
            + "  - no shutdown\n"
            + "  - mtu 9198\n"
            + "  - description sw-spine-001:6==>sw-cdu-002:49\n"
            + "  - lag 201\n"
            + "vsx\n"
            + "  - system-mac 02:00:00:00:6b:00\n"
            + "  - inter-switch-link lag 256\n"
            + "  - role primary\n"
            + "  - keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "  + system-mac 02:00:00:00:6b:01\n"
            + "  + inter-switch-link lag 255\n"
            + "  + role secondary\n"
            + "  + keepalive peer 192.168.255.1 source 192.168.255.2 vrf keepalive\n"
            + "- router ospf 1\n"
            + "  - router-id 10.2.0.2/32\n"
            + "  - area 0.0.0.0\n"
            + "- nae-script abc\n"
            + "+ hostname sw-spine-01\n"
            + "+ spanning-tree priority 7\n"
            + "+ interface lag 100 multi-chassis\n"
            + "  + no shutdown\n"
            + "  + description spine_to_leaf_lag\n"
            + "  + no routing\n"
            + "  + vlan trunk native 1\n"
            + "  + vlan trunk allowed 2,4,7\n"
            + "  + lacp mode active\n"
            + "  + spanning-tree root-guard\n"
            + "+ interface 1/1/7\n"
            + "  + no shutdown\n"
            + "  + mtu 9198\n"
            + "  + description sw-spine-001:7==>sw-cdu-002:49\n"
            + "  + lag 201\n"
            + "+ router ospf 0\n"
            + "  + router-id 10.2.0.2/32\n"
            + "  + area 0.0.0.0\n"
            + "+ nae-script 123\n"
        ) in str(result.output)


def test_validate_config_running_file_aruba():
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        vendor = "aruba"
        with open("running_switch.cfg", "w") as switch_f:
            switch_f.writelines(switch_config)
        with open("switch.cfg", "w") as switch2_f:
            switch2_f.writelines(switch_config2)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--running",
                running_config_file,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
                "--vendor",
                vendor,
            ],
        )
        assert result.exit_code == 0

        assert (
            "- hostname sw-spine-001\n"
            + "- spanning-tree priority 0\n"
            + "- interface lag 101 multi-chassis\n"
            + "  - no shutdown\n"
            + "  - description spine_to_leaf_lag\n"
            + "  - no routing\n"
            + "  - vlan trunk native 1\n"
            + "  - vlan trunk allowed 2,4,7\n"
            + "  - lacp mode active\n"
            + "  - spanning-tree root-guard\n"
            + "interface 1/1/1\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "interface 1/1/2\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "- interface 1/1/6\n"
            + "  - no shutdown\n"
            + "  - mtu 9198\n"
            + "  - description sw-spine-001:6==>sw-cdu-002:49\n"
            + "  - lag 201\n"
            + "vsx\n"
            + "  - system-mac 02:00:00:00:6b:00\n"
            + "  - inter-switch-link lag 256\n"
            + "  - role primary\n"
            + "  - keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "  + system-mac 02:00:00:00:6b:01\n"
            + "  + inter-switch-link lag 255\n"
            + "  + role secondary\n"
            + "  + keepalive peer 192.168.255.1 source 192.168.255.2 vrf keepalive\n"
            + "- router ospf 1\n"
            + "  - router-id 10.2.0.2/32\n"
            + "  - area 0.0.0.0\n"
            + "- nae-script abc\n"
            + "+ hostname sw-spine-01\n"
            + "+ spanning-tree priority 7\n"
            + "+ interface lag 100 multi-chassis\n"
            + "  + no shutdown\n"
            + "  + description spine_to_leaf_lag\n"
            + "  + no routing\n"
            + "  + vlan trunk native 1\n"
            + "  + vlan trunk allowed 2,4,7\n"
            + "  + lacp mode active\n"
            + "  + spanning-tree root-guard\n"
            + "+ interface 1/1/7\n"
            + "  + no shutdown\n"
            + "  + mtu 9198\n"
            + "  + description sw-spine-001:7==>sw-cdu-002:49\n"
            + "  + lag 201\n"
            + "+ router ospf 0\n"
            + "  + router-id 10.2.0.2/32\n"
            + "  + area 0.0.0.0\n"
            + "+ nae-script 123\n"
        ) in str(result.output)


def test_validate_config_running_file_dell():
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        vendor = "dell"
        with open("running_switch.cfg", "w") as switch_f:
            switch_f.writelines(dell_switch_config)
        with open("switch.cfg", "w") as switch2_f:
            switch2_f.writelines(dell_switch_config2)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--running",
                running_config_file,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
                "--vendor",
                vendor,
            ],
        )
        assert result.exit_code == 0

        assert (
            "interface vlan3000\n"
            + "  - mode L3\n"
            + "  - description cabinet_3002\n"
            + "  - no shutdown\n"
            + "  - mtu 9216\n"
            + "  - ip address 192.168.104.2/22\n"
            + "  - ip ospf 1 area 0.0.0.0\n"
            + "  - ip ospf passive\n"
            + "  - ip helper-address 10.94.100.222\n"
            + "  - vrrp-group 30\n"
            + "    - virtual-address 192.168.104.1\n"
            + "    - priority 110\n"
            + "interface vlan2\n"
            + "  - ip address 192.168.3.16/17\n"
            + "interface port-channel5\n"
            + "  - vlt-port-channel 5\n"
            + "interface ethernet1/1/28\n"
            + "  - no shutdown\n"
            + "  - channel-group 100 mode active\n"
            + "  - flowcontrol receive off\n"
            + "  - flowcontrol transmit off\n"
            + "  + flowcontrol receive on\n"
            + "  + flowcontrol transmit on\n"
            + "ip access-list nmn-hmn\n"
            + "  - seq 40 deny ip 192.168.0.0/17 192.168.100.0/17\n"
            + "  - seq 50 deny ip 192.168.100.0/17 192.168.0.0/17\n"
            + "  + seq 85 deny ip 192.168.201.0/17 192.168.101.0/17\n"
            + "- router ospf 1\n"
            + "  - router-id 10.2.0.16\n"
            + "vlt-domain 1\n"
            + "  - vlt-mac 00:11:22:aa:bb:cc\n"
            + "- ntp server 192.168.4.4\n"
            + "+ router bgp\n"
            + "  + mode L3\n"
            + "  + description cabinet_3002\n"
            + "  + no shutdown\n"
            + "  + mtu 9216\n"
            + "  + ip address 192.168.104.2/22\n"
            + "  + ip ospf 1 area 0.0.0.0\n"
            + "  + ip ospf passive\n"
            + "  + ip helper-address 10.94.100.222\n"
            + "  + vrrp-group 30\n"
            + "    + virtual-address 192.168.104.1\n"
            + "    + priority 110\n"
            + "+ interface vlan7\n"
            + "  + description CAN\n"
            + "  + no shutdown\n"
            + "  + mtu 9216\n"
            + "  + ip address 192.168.0.16/17\n"
            + "  + ip access-group nmn-hmn in\n"
            + "  + ip access-group nmn-hmn out\n"
            + "  + ip ospf 1 area 0.0.0.0\n"
        ) in str(result.output)


def test_validate_config_running_file_mellanox():
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        vendor = "mellanox"
        with open("running_switch.cfg", "w") as switch_f:
            switch_f.writelines(mellanox_switch_config)
        with open("switch.cfg", "w") as switch2_f:
            switch2_f.writelines(mellanox_switch_config2)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--running",
                running_config_file,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
                "--vendor",
                vendor,
            ],
        )
        assert result.exit_code == 0

        assert (
            "- router ospf 1 vrf default\n"
            + "- no ntp server 192.168.4.6 disable\n"
            + "- ntp server 192.168.4.6 keyID 0\n"
            + "- no ntp server 192.168.4.6 trusted-enable\n"
            + "- ntp server 192.168.4.6 version 4\n"
            + "+ router ospf 0 vrf default\n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_password_prompt(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command runs after password prompt."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--generated",
                generated_config_file,
            ],
            input=password,
        )
        assert result.exit_code == 0

        assert ("- nae-script abc\n" + "+ router add\n") in str(result.output)


def test_validate_config_vendor_prompt():
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        vendor = "aruba"
        with open("running_switch.cfg", "w") as switch_f:
            switch_f.writelines(switch_config)
        with open("switch.cfg", "w") as switch2_f:
            switch2_f.writelines(switch_config2)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--running",
                running_config_file,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
            input=vendor,
        )
        assert result.exit_code == 0

        assert (
            "Please enter the vendor (Aruba, Dell, Mellanox): aruba\n"
            + "- hostname sw-spine-001\n"
            + "- spanning-tree priority 0\n"
            + "- interface lag 101 multi-chassis\n"
            + "  - no shutdown\n"
            + "  - description spine_to_leaf_lag\n"
            + "  - no routing\n"
            + "  - vlan trunk native 1\n"
            + "  - vlan trunk allowed 2,4,7\n"
            + "  - lacp mode active\n"
            + "  - spanning-tree root-guard\n"
            + "interface 1/1/1\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "interface 1/1/2\n"
            + "  - lag 101\n"
            + "  + lag 100\n"
            + "- interface 1/1/6\n"
            + "  - no shutdown\n"
            + "  - mtu 9198\n"
            + "  - description sw-spine-001:6==>sw-cdu-002:49\n"
            + "  - lag 201\n"
            + "vsx\n"
            + "  - system-mac 02:00:00:00:6b:00\n"
            + "  - inter-switch-link lag 256\n"
            + "  - role primary\n"
            + "  - keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
            + "  + system-mac 02:00:00:00:6b:01\n"
            + "  + inter-switch-link lag 255\n"
            + "  + role secondary\n"
            + "  + keepalive peer 192.168.255.1 source 192.168.255.2 vrf keepalive\n"
            + "- router ospf 1\n"
            + "  - router-id 10.2.0.2/32\n"
            + "  - area 0.0.0.0\n"
            + "- nae-script abc\n"
            + "+ hostname sw-spine-01\n"
            + "+ spanning-tree priority 7\n"
            + "+ interface lag 100 multi-chassis\n"
            + "  + no shutdown\n"
            + "  + description spine_to_leaf_lag\n"
            + "  + no routing\n"
            + "  + vlan trunk native 1\n"
            + "  + vlan trunk allowed 2,4,7\n"
            + "  + lacp mode active\n"
            + "  + spanning-tree root-guard\n"
            + "+ interface 1/1/7\n"
            + "  + no shutdown\n"
            + "  + mtu 9198\n"
            + "  + description sw-spine-001:7==>sw-cdu-002:49\n"
            + "  + lag 201\n"
            + "+ router ospf 0\n"
            + "  + router-id 10.2.0.2/32\n"
            + "  + area 0.0.0.0\n"
            + "+ nae-script 123\n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_timeout(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command fails on timeout."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.side_effect = NetmikoTimeoutException
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert ("Timeout error. Check the IP address and try again.") in str(
            result.output,
        )


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_auth_exception(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command fails on auth exception."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.side_effect = NetmikoAuthenticationException
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert ("Authentication error. Check the credentials or IP address and try again") in str(result.output)


def test_validate_config_bad_config_file():
    """Test that the `canu validate switch config` command fails on bad file."""
    non_config_file = "bad.file"
    vendor = "aruba"
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        # Generate random binary file
        with open(non_config_file, "wb") as f:
            f.write(urandom(128))

        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)
        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--running",
                non_config_file,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
                "--vendor",
                vendor,
            ],
        )
        assert result.exit_code == 0

        assert ("The file bad.file is not a valid config file.") in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_no_vendor(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command error on no vendor."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = None
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0
        assert "There wan an error determining the vendor of the switch." in str(
            result.output,
        )


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_commands")
def test_validate_config_dell(netmiko_commands, switch_vendor):
    """Test that the `canu validate switch config` command runs on dell switch."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.return_value = [switch_config, "sw-spine-001"]
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert ("- nae-script abc\n" + "+ router add\n") in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_commands")
def test_validate_config_mellanox(netmiko_commands, switch_vendor):
    """Test that the `canu validate switch config` command runs on mellanox switch."""
    switch_config_edit = mellanox_switch_config[:-1] + "\n" + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.return_value = [
            mellanox_switch_config,
            "hostname: sw-spine-001",
        ]
        with open("mellanox_switch.cfg", "w") as f:
            f.writelines(switch_config_edit)
        result = runner.invoke(
            cli,
            [
                "validate",
                "switch",
                "config",
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                mellanox_generated_config_file,
            ],
        )
        assert result.exit_code == 0

        assert ("+ router add") in str(result.output)


switch_config = (
    "hostname sw-spine-001\n"
    + "bfd\n"
    + "no ip icmp redirect\n"
    + "vrf CAN\n"
    + "vrf keepalive\n"
    + "ntp server 192.168.4.4\n"
    + "ntp server 192.168.4.5\n"
    + "ntp server 192.168.4.6\n"
    + "ntp enable\n"
    + "\n"
    + "\n"
    + "\n"
    + "ssh server vrf default\n"
    + "ssh server vrf mgmt\n"
    + "access-list ip nmn-hmn\n"
    + "    deny any 192.168.3.0/17 192.168.0.0/17\n"
    + "    deny any 192.168.3.0/17 192.168.200.0/17\n"
    + "    deny any 192.168.0.0/17 192.168.3.0/17\n"
    + "    deny any 192.168.0.0/17 192.168.100.0/17\n"
    + "    deny any 192.168.100.0/17 192.168.0.0/17\n"
    + "    deny any 192.168.100.0/17 192.168.200.0/17\n"
    + "    deny any 192.168.200.0/17 192.168.3.0/17\n"
    + "    deny any 192.168.200.0/17 192.168.100.0/17\n"
    + "    permit any any any\n"
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
    + "vlan 7\n"
    + "    name CAN\n"
    + "vlan 10\n"
    + "    name SUN\n"
    + "spanning-tree\n"
    + "spanning-tree priority 0\n"
    + "spanning-tree config-name MST0\n"
    + "spanning-tree config-revision 1\n"
    + "interface mgmt\n"
    + "    shutdown\n"
    + "\n"
    + "interface lag 101 multi-chassis\n"
    + "    no shutdown\n"
    + "    description spine_to_leaf_lag\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4,7\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/1\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:1==>sw-leaf-001:53\n"
    + "    lag 101\n"
    + "\n"
    + "interface 1/1/2\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:2==>sw-leaf-002:53\n"
    + "    lag 101\n"
    + "\n"
    + "interface lag 103 multi-chassis\n"
    + "    no shutdown\n"
    + "    description spine_to_leaf_lag\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4,7\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/3\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:3==>sw-leaf-003:53\n"
    + "    lag 103\n"
    + "\n"
    + "interface 1/1/4\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:4==>sw-leaf-004:53\n"
    + "    lag 103\n"
    + "\n"
    + "interface lag 201 multi-chassis\n"
    + "    no shutdown\n"
    + "    description sw-spine-001:5==>sw-cdu-001:49\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/5\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:5==>sw-cdu-001:49\n"
    + "    lag 201\n"
    + "\n"
    + "interface 1/1/6\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:6==>sw-cdu-002:49\n"
    + "    lag 201\n"
    + "\n"
    + "interface lag 256\n"
    + "    no shutdown\n"
    + "    description ISL link\n"
    + "    no routing\n"
    + "    vlan trunk native 1 tag\n"
    + "    vlan trunk allowed all\n"
    + "    lacp mode active\n"
    + "interface 1/1/30\n"
    + "    no shutdown\n"
    + "    vrf attach keepalive\n"
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
    + "interface loopback 0\n"
    + "    ip address 10.2.0.2/32\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 1\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.1.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.1.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "interface vlan 2\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.3.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.3.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 4\n"
    + "    ip mtu 9198\n"
    + "    ip address 10.254.0.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 10.254.0.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 7\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.11.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.11.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "vsx\n"
    + "    system-mac 02:00:00:00:6b:00\n"
    + "    inter-switch-link lag 256\n"
    + "    role primary\n"
    + "    keepalive peer 192.168.255.1 source 192.168.255.0 vrf keepalive\n"
    + "    linkup-delay-timer 600\n"
    + "    vsx-sync vsx-global\n"
    + "router ospf 1\n"
    + "    router-id 10.2.0.2/32\n"
    + "    area 0.0.0.0\n"
    + "router ospfv3 1\n"
    + "    router-id 10.2.0.2/32\n"
    + "    area 0.0.0.0\n"
    + "https-server vrf default\n"
    + "https-server vrf mgmt\n"
    + "https-server vrf CAN\n"
    + "nae-script abc\n"
)

switch_config2 = (
    "hostname sw-spine-01\n"
    + "bfd\n"
    + "no ip icmp redirect\n"
    + "vrf CAN\n"
    + "vrf keepalive\n"
    + "ntp server 192.168.4.4\n"
    + "ntp server 192.168.4.5\n"
    + "ntp server 192.168.4.6\n"
    + "ntp enable\n"
    + "\n"
    + "\n"
    + "\n"
    + "ssh server vrf default\n"
    + "ssh server vrf mgmt\n"
    + "access-list ip nmn-hmn\n"
    + "    deny any 192.168.3.0/17 192.168.0.0/17\n"
    + "    deny any 192.168.3.0/17 192.168.200.0/17\n"
    + "    deny any 192.168.0.0/17 192.168.3.0/17\n"
    + "    deny any 192.168.0.0/17 192.168.100.0/17\n"
    + "    deny any 192.168.100.0/17 192.168.0.0/17\n"
    + "    deny any 192.168.100.0/17 192.168.200.0/17\n"
    + "    deny any 192.168.200.0/17 192.168.3.0/17\n"
    + "    deny any 192.168.200.0/17 192.168.100.0/17\n"
    + "    permit any any any\n"
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
    + "vlan 7\n"
    + "    name CAN\n"
    + "vlan 10\n"
    + "    name SUN\n"
    + "spanning-tree\n"
    + "spanning-tree priority 7\n"
    + "spanning-tree config-name MST0\n"
    + "spanning-tree config-revision 1\n"
    + "interface mgmt\n"
    + "    shutdown\n"
    + "\n"
    + "interface lag 100 multi-chassis\n"
    + "    no shutdown\n"
    + "    description spine_to_leaf_lag\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4,7\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/1\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:1==>sw-leaf-001:53\n"
    + "    lag 100\n"
    + "\n"
    + "interface 1/1/2\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:2==>sw-leaf-002:53\n"
    + "    lag 100\n"
    + "\n"
    + "interface lag 103 multi-chassis\n"
    + "    no shutdown\n"
    + "    description spine_to_leaf_lag\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4,7\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/3\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:3==>sw-leaf-003:53\n"
    + "    lag 103\n"
    + "\n"
    + "interface 1/1/4\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:4==>sw-leaf-004:53\n"
    + "    lag 103\n"
    + "\n"
    + "interface lag 201 multi-chassis\n"
    + "    no shutdown\n"
    + "    description sw-spine-001:5==>sw-cdu-001:49\n"
    + "    no routing\n"
    + "    vlan trunk native 1\n"
    + "    vlan trunk allowed 2,4\n"
    + "    lacp mode active\n"
    + "    spanning-tree root-guard\n"
    + "\n"
    + "interface 1/1/5\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:5==>sw-cdu-001:49\n"
    + "    lag 201\n"
    + "\n"
    + "interface 1/1/7\n"
    + "    no shutdown\n"
    + "    mtu 9198\n"
    + "    description sw-spine-001:7==>sw-cdu-002:49\n"
    + "    lag 201\n"
    + "\n"
    + "interface lag 256\n"
    + "    no shutdown\n"
    + "    description ISL link\n"
    + "    no routing\n"
    + "    vlan trunk native 1 tag\n"
    + "    vlan trunk allowed all\n"
    + "    lacp mode active\n"
    + "interface 1/1/30\n"
    + "    no shutdown\n"
    + "    vrf attach keepalive\n"
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
    + "interface loopback 0\n"
    + "    ip address 10.2.0.2/32\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 1\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.1.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.1.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "interface vlan 2\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.3.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.3.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 4\n"
    + "    ip mtu 9198\n"
    + "    ip address 10.254.0.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 10.254.0.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "    ip ospf 1 area 0.0.0.0\n"
    + "interface vlan 7\n"
    + "    ip mtu 9198\n"
    + "    ip address 192.168.11.2\n"
    + "    active-gateway ip mac 12:00:00:00:6b:00\n"
    + "    active-gateway ip 192.168.11.1\n"
    + "    ip helper-address 10.92.100.222\n"
    + "vsx\n"
    + "    system-mac 02:00:00:00:6b:01\n"
    + "    inter-switch-link lag 255\n"
    + "    role secondary\n"
    + "    keepalive peer 192.168.255.1 source 192.168.255.2 vrf keepalive\n"
    + "    linkup-delay-timer 600\n"
    + "    vsx-sync vsx-global\n"
    + "router ospf 0\n"
    + "    router-id 10.2.0.2/32\n"
    + "    area 0.0.0.0\n"
    + "router ospfv3 1\n"
    + "    router-id 10.2.0.2/32\n"
    + "    area 0.0.0.0\n"
    + "https-server vrf default\n"
    + "https-server vrf mgmt\n"
    + "https-server vrf CAN\n"
    + "nae-script 123\n"
)

mellanox_switch_config = (
    "hostname sw-spine-001\n"
    + "no cli default prefix-modes enable\n"
    + "protocol mlag\n"
    + "protocol bgp\n"
    + "lacp\n"
    + "interface mlag-port-channel 1\n"
    + "interface mlag-port-channel 2\n"
    + "interface ethernet 1/1 mtu 9216 force\n"
    + "interface ethernet 1/2 mtu 9216 force\n"
    + "interface mlag-port-channel 1 mtu 9216 force\n"
    + "interface mlag-port-channel 2 mtu 9216 force\n"
    + "interface ethernet 1/1 mlag-channel-group 1 mode active\n"
    + "interface ethernet 1/2 mlag-channel-group 2 mode active\n"
    + "interface mlag-port-channel 1 switchport mode hybrid\n"
    + "interface mlag-port-channel 2 switchport mode hybrid\n"
    + "interface ethernet 1/1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
    + "interface ethernet 1/2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
    + "interface mlag-port-channel 1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
    + "interface mlag-port-channel 2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
    + "interface mlag-port-channel 1 no shutdown\n"
    + "interface mlag-port-channel 2 no shutdown\n"
    + "interface mlag-port-channel 1 lacp-individual enable force\n"
    + "interface mlag-port-channel 2 lacp-individual enable force\n"
    + 'vlan 2 name "RVR_NMN"\n'
    + 'vlan 4 name "RVR_HMN"\n'
    + 'vlan 7 name "CAN"\n'
    + 'vlan 4000 name "MLAG"\n'
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
    + "interface vlan 1\n"
    + "interface vlan 2\n"
    + "interface vlan 4\n"
    + "interface vlan 7\n"
    + "interface vlan 10\n"
    + "interface vlan 4000\n"
    + "interface vlan 1 mtu 9216\n"
    + "interface vlan 2 mtu 9216\n"
    + "interface vlan 4 mtu 9216\n"
    + "interface vlan 7 mtu 9216\n"
    + "interface vlan 4000 mtu 9216\n"
    + "interface vlan 1 ip address 192.168.1.2/16 primary\n"
    + "interface vlan 2 ip address 192.168.3.2/17 primary\n"
    + "interface vlan 4 ip address 192.168.0.2/17 primary\n"
    + "interface vlan 7 ip address 192.168.11.2/24 primary\n"
    + "interface vlan 4000 ip address 192.168.255.253/30 primary\n"
    + "ip load-sharing source-ip-port\n"
    + "ip load-sharing type consistent\n"
    + "spanning-tree mode mst\n"
    + "spanning-tree port type edge default\n"
    + "spanning-tree priority 4096\n"
    + "spanning-tree mst 1 vlan 1\n"
    + "spanning-tree mst 1 vlan 2\n"
    + "spanning-tree mst 1 vlan 4\n"
    + "spanning-tree mst 1 vlan 7\n"
    + "interface mlag-port-channel 151 spanning-tree port type network\n"
    + "interface mlag-port-channel 151 spanning-tree guard root\n"
    + "interface mlag-port-channel 201 spanning-tree port type network\n"
    + "interface mlag-port-channel 201 spanning-tree guard root\n"
    + "ipv4 access-list nmn-hmn\n"
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
    + "protocol ospf\n"
    + "router ospf 1 vrf default\n"
    + "router ospf 1 vrf default router-id 10.2.0.2\n"
    + "interface vlan 2 ip ospf area 0.0.0.0\n"
    + "interface vlan 4 ip ospf area 0.0.0.0\n"
    + "router ospf 1 vrf default redistribute ibgp\n"
    + "ip dhcp relay instance 2 vrf default\n"
    + "ip dhcp relay instance 4 vrf default\n"
    + "ip dhcp relay instance 2 address 10.92.100.222\n"
    + "ip dhcp relay instance 4 address 10.94.100.222\n"
    + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
    + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
    + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
    + "interface vlan 7 ip dhcp relay instance 2 downstream\n"
    + "protocol magp\n"
    + "interface vlan 1 magp 1\n"
    + "interface vlan 2 magp 2\n"
    + "interface vlan 4 magp 4\n"
    + "interface vlan 7 magp 7\n"
    + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
    + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
    + "interface vlan 4 magp 4 ip virtual-router address 192.168.0.1\n"
    + "interface vlan 7 magp 7 ip virtual-router address 192.168.11.1\n"
    + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 4 magp 4 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 7 magp 7 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
    + "no mlag shutdown\n"
    + "mlag system-mac 00:00:5E:00:01:01\n"
    + "interface port-channel 100 ipl 1\n"
    + "interface vlan 4000 ipl 1 peer-address 192.168.255.254\n"
    + "no interface mgmt0 dhcp\n"
    + "interface mgmt0 ip address 192.168.255.241 /29\n"
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
)

mellanox_switch_config2 = (
    "hostname sw-spine-001\n"
    + "no cli default prefix-modes enable\n"
    + "protocol mlag\n"
    + "protocol bgp\n"
    + "lacp\n"
    + "interface mlag-port-channel 1\n"
    + "interface mlag-port-channel 2\n"
    + "interface ethernet 1/1 mtu 9216 force\n"
    + "interface ethernet 1/2 mtu 9216 force\n"
    + "interface mlag-port-channel 1 mtu 9216 force\n"
    + "interface mlag-port-channel 2 mtu 9216 force\n"
    + "interface ethernet 1/1 mlag-channel-group 1 mode active\n"
    + "interface ethernet 1/2 mlag-channel-group 2 mode active\n"
    + "interface mlag-port-channel 1 switchport mode hybrid\n"
    + "interface mlag-port-channel 2 switchport mode hybrid\n"
    + "interface ethernet 1/1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
    + "interface ethernet 1/2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
    + "interface mlag-port-channel 1 description sw-spine-001:1==>ncn-m001:pcie-slot1:1\n"
    + "interface mlag-port-channel 2 description sw-spine-001:2==>ncn-m002:pcie-slot1:1\n"
    + "interface mlag-port-channel 1 no shutdown\n"
    + "interface mlag-port-channel 2 no shutdown\n"
    + "interface mlag-port-channel 1 lacp-individual enable force\n"
    + "interface mlag-port-channel 2 lacp-individual enable force\n"
    + 'vlan 2 name "RVR_NMN"\n'
    + 'vlan 4 name "RVR_HMN"\n'
    + 'vlan 7 name "CAN"\n'
    + 'vlan 4000 name "MLAG"\n'
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 2\n"
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 4\n"
    + "interface mlag-port-channel 1 switchport hybrid allowed-vlan add 7\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 2\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 4\n"
    + "interface mlag-port-channel 2 switchport hybrid allowed-vlan add 7\n"
    + "interface vlan 1\n"
    + "interface vlan 2\n"
    + "interface vlan 4\n"
    + "interface vlan 7\n"
    + "interface vlan 10\n"
    + "interface vlan 4000\n"
    + "interface vlan 1 mtu 9216\n"
    + "interface vlan 2 mtu 9216\n"
    + "interface vlan 4 mtu 9216\n"
    + "interface vlan 7 mtu 9216\n"
    + "interface vlan 4000 mtu 9216\n"
    + "interface vlan 1 ip address 192.168.1.2/16 primary\n"
    + "interface vlan 2 ip address 192.168.3.2/17 primary\n"
    + "interface vlan 4 ip address 192.168.0.2/17 primary\n"
    + "interface vlan 7 ip address 192.168.11.2/24 primary\n"
    + "interface vlan 4000 ip address 192.168.255.253/30 primary\n"
    + "ip load-sharing source-ip-port\n"
    + "ip load-sharing type consistent\n"
    + "spanning-tree mode mst\n"
    + "spanning-tree port type edge default\n"
    + "spanning-tree priority 4096\n"
    + "spanning-tree mst 1 vlan 1\n"
    + "spanning-tree mst 1 vlan 2\n"
    + "spanning-tree mst 1 vlan 4\n"
    + "spanning-tree mst 1 vlan 7\n"
    + "interface mlag-port-channel 151 spanning-tree port type network\n"
    + "interface mlag-port-channel 151 spanning-tree guard root\n"
    + "interface mlag-port-channel 201 spanning-tree port type network\n"
    + "interface mlag-port-channel 201 spanning-tree guard root\n"
    + "ipv4 access-list nmn-hmn\n"
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
    + "protocol ospf\n"
    + "router ospf 0 vrf default\n"
    + "router ospf 1 vrf default router-id 10.2.0.2\n"
    + "interface vlan 2 ip ospf area 0.0.0.0\n"
    + "interface vlan 4 ip ospf area 0.0.0.0\n"
    + "router ospf 1 vrf default redistribute ibgp\n"
    + "ip dhcp relay instance 2 vrf default\n"
    + "ip dhcp relay instance 4 vrf default\n"
    + "ip dhcp relay instance 2 address 10.92.100.222\n"
    + "ip dhcp relay instance 4 address 10.94.100.222\n"
    + "interface vlan 1 ip dhcp relay instance 2 downstream\n"
    + "interface vlan 2 ip dhcp relay instance 2 downstream\n"
    + "interface vlan 4 ip dhcp relay instance 4 downstream\n"
    + "interface vlan 7 ip dhcp relay instance 2 downstream\n"
    + "protocol magp\n"
    + "interface vlan 1 magp 1\n"
    + "interface vlan 2 magp 2\n"
    + "interface vlan 4 magp 4\n"
    + "interface vlan 7 magp 7\n"
    + "interface vlan 1 magp 1 ip virtual-router address 192.168.1.1\n"
    + "interface vlan 2 magp 2 ip virtual-router address 192.168.3.1\n"
    + "interface vlan 4 magp 4 ip virtual-router address 192.168.0.1\n"
    + "interface vlan 7 magp 7 ip virtual-router address 192.168.11.1\n"
    + "interface vlan 1 magp 1 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 2 magp 2 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 4 magp 4 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "interface vlan 7 magp 7 ip virtual-router mac-address 00:00:5E:00:01:01\n"
    + "mlag-vip mlag-domain ip 192.168.255.242 /29 force\n"
    + "no mlag shutdown\n"
    + "mlag system-mac 00:00:5E:00:01:01\n"
    + "interface port-channel 100 ipl 1\n"
    + "interface vlan 4000 ipl 1 peer-address 192.168.255.254\n"
    + "no interface mgmt0 dhcp\n"
    + "interface mgmt0 ip address 192.168.255.241 /29\n"
    + "no ntp server 192.168.4.4 disable\n"
    + "ntp server 192.168.4.4 keyID 0\n"
    + "no ntp server 192.168.4.4 trusted-enable\n"
    + "ntp server 192.168.4.4 version 4\n"
    + "no ntp server 192.168.4.5 disable\n"
    + "ntp server 192.168.4.5 keyID 0\n"
    + "no ntp server 192.168.4.5 trusted-enable\n"
    + "ntp server 192.168.4.5 version 4\n"
)

dell_switch_config = (
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
    + "interface vlan1\n"
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
    + "interface port-channel2\n"
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
    + "interface port-channel100\n"
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
    + "ip access-list nmn-hmn\n"
    + "  seq 10 deny ip 192.168.3.0/17 192.168.0.0/17\n"
    + "  seq 20 deny ip 192.168.0.0/17 192.168.3.0/17\n"
    + "  seq 30 deny ip 192.168.3.0/17 192.168.200.0/17\n"
    + "  seq 40 deny ip 192.168.0.0/17 192.168.100.0/17\n"
    + "  seq 50 deny ip 192.168.100.0/17 192.168.0.0/17\n"
    + "  seq 60 deny ip 192.168.100.0/17 192.168.200.0/17\n"
    + "  seq 70 deny ip 192.168.200.0/17 192.168.3.0/17\n"
    + "  seq 80 deny ip 192.168.200.0/17 192.168.100.0/17\n"
    + "  seq 90 permit ip any any\n"
    + "router ospf 1\n"
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
)

dell_switch_config2 = (
    "interface vlan3000\n"
    + "router bgp\n"
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
    + "interface vlan1\n"
    + "  Description MTL\n"
    + "  no shutdown\n"
    + "  ip address 192.168.1.16/16\n"
    + "interface vlan2\n"
    + "  description RIVER_NMN\n"
    + "  no shutdown\n"
    + "  mtu 9216\n"
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
    + "interface vlan7\n"
    + "  description CAN\n"
    + "  no shutdown\n"
    + "  mtu 9216\n"
    + "  ip address 192.168.0.16/17\n"
    + "  ip access-group nmn-hmn in\n"
    + "  ip access-group nmn-hmn out\n"
    + "  ip ospf 1 area 0.0.0.0\n"
    + "interface port-channel2\n"
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
    + "  spanning-tree guard root\n"
    + "interface port-channel100\n"
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
    + "  no switchport\n"
    + "  mtu 9216\n"
    + "  flowcontrol receive on\n"
    + "  flowcontrol transmit on\n"
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
    + "ip access-list nmn-hmn\n"
    + "  seq 10 deny ip 192.168.3.0/17 192.168.0.0/17\n"
    + "  seq 20 deny ip 192.168.0.0/17 192.168.3.0/17\n"
    + "  seq 30 deny ip 192.168.3.0/17 192.168.200.0/17\n"
    + "  seq 60 deny ip 192.168.100.0/17 192.168.200.0/17\n"
    + "  seq 70 deny ip 192.168.200.0/17 192.168.3.0/17\n"
    + "  seq 80 deny ip 192.168.200.0/17 192.168.100.0/17\n"
    + "  seq 85 deny ip 192.168.201.0/17 192.168.101.0/17\n"
    + "  seq 90 permit ip any any\n"
    + "spanning-tree mode mst\n"
    + "spanning-tree mst configuration\n"
    + "  instance 1 vlan 1-4093\n"
    + "vlt-domain 1\n"
    + "  backup destination 192.168.255.243\n"
    + "  discovery-interface ethernet1/1/25,1/1/26\n"
    + "  peer-routing\n"
    + "  primary-priority 4096\n"
    + "ntp server 192.168.4.5\n"
    + "ntp server 192.168.4.6\n"
)
