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
"""Test CANU validate switch config commands."""
import json
from os import urandom
from unittest.mock import patch

from click import testing
from netmiko import ssh_exception

from canu.cli import cli


username = "admin"
password = "admin"
ip = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
credentials = {"username": username, "password": password}
cache_minutes = 0
generated_config_file = "switch.cfg"
running_config_file = "running_switch.cfg"
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
                "--cache",
                cache_minutes,
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
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_json(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command runs and prints json."""
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
                "--cache",
                cache_minutes,
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
                "--json",
            ],
        )
        result_json = json.loads(result.output)

        assert result.exit_code == 0
        assert result_json == {
            "additions": 1,
            "deletions": 1,
            "hostname_additions": 0,
            "hostname_deletions": 0,
            "interface_additions": 0,
            "interface_deletions": 0,
            "interface_lag_additions": 0,
            "interface_lag_deletions": 0,
            "spanning_tree_additions": 0,
            "spanning_tree_deletions": 0,
            "script_additions": 0,
            "script_deletions": 1,
            "router_additions": 1,
            "router_deletions": 0,
            "system_mac_additions": 0,
            "system_mac_deletions": 0,
            "isl_additions": 0,
            "isl_deletions": 0,
            "role_additions": 0,
            "role_deletions": 0,
            "keepalive_additions": 0,
            "keepalive_deletions": 0,
        }


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
                "--cache",
                cache_minutes,
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
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                13  |  Total Deletions:                13\n"
            + "Hostname:                        1  |  Hostname:                        1\n"
            + "Interface:                       1  |  Interface:                       1\n"
            + "Interface Lag:                   1  |  Interface Lag:                   1\n"
            + "Spanning Tree:                   1  |  Spanning Tree:                   1\n"
            + "Script:                          1  |  Script:                          1\n"
            + "Router:                          1  |  Router:                          1\n"
            + "System Mac:                      1  |  System Mac:                      1\n"
            + "Inter Switch Link:               1  |  Inter Switch Link:               1\n"
            + "Role:                            1  |  Role:                            1\n"
            + "Keepalive:                       1  |  Keepalive:                       1\n"
        ) in str(result.output)


def test_validate_config_running_file():
    """Test that the `canu validate switch config` command runs and sees an addition."""
    with runner.isolated_filesystem():
        with open("running_switch.cfg", "w") as switch_f:
            switch_f.writelines(switch_config)
        with open("switch.cfg", "w") as switch2_f:
            switch2_f.writelines(switch_config2)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
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
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                13  |  Total Deletions:                13\n"
            + "Hostname:                        1  |  Hostname:                        1\n"
            + "Interface:                       1  |  Interface:                       1\n"
            + "Interface Lag:                   1  |  Interface Lag:                   1\n"
            + "Spanning Tree:                   1  |  Spanning Tree:                   1\n"
            + "Script:                          1  |  Script:                          1\n"
            + "Router:                          1  |  Router:                          1\n"
            + "System Mac:                      1  |  System Mac:                      1\n"
            + "Inter Switch Link:               1  |  Inter Switch Link:               1\n"
            + "Role:                            1  |  Role:                            1\n"
            + "Keepalive:                       1  |  Keepalive:                       1\n"
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
                "--cache",
                cache_minutes,
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
        assert (
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_config_timeout(netmiko_command, switch_vendor):
    """Test that the `canu validate switch config` command fails on timeout."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.side_effect = ssh_exception.NetmikoTimeoutException
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
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
        netmiko_command.side_effect = ssh_exception.NetmikoAuthenticationException
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
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
            "Authentication error. Check the credentials or IP address and try again"
        ) in str(result.output)


def test_validate_config_bad_config_file():
    """Test that the `canu validate switch config` command fails on bad file."""
    non_config_file = "bad.file"
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
                "--cache",
                cache_minutes,
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
                "--cache",
                cache_minutes,
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
                "--cache",
                cache_minutes,
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
        assert (
            "Switch: sw-spine-001 (192.168.1.2)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_commands")
def test_validate_config_mellanox(netmiko_commands, switch_vendor):
    """Test that the `canu validate switch config` command runs on mellanox switch."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.return_value = [switch_config, "hostname: sw-spine-001"]
        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
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
                generated_config_file,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001 (192.168.1.3)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


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
