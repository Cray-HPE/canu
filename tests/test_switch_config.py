"""Test CANU validate shcd commands."""
import json
import os
from pathlib import Path

import click.testing
import requests
import responses

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_0.0.6.xlsx"
test_file = os.path.join(test_file_directory, "data", test_file_name)
architecture = "full"
tabs = "INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T48,J14,T24,J14,T23"
csi_folder = "."
shasta = "1.4"
switch_name = "sw-spine-001"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"
runner = click.testing.CliRunner()


def test_switch_config_spine_primary():
    """Test that the `canu switch config` command runs and returns valid primary spine config."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)

        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # sw-spine-to-leaf.lag.j2
        assert "interface lag ***===> 1" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-spine-001:1==>sw-leaf-001:53" in str(
            result.output
        )
        assert "description ***===> sw-spine-001:2==>sw-leaf-002:53" in str(
            result.output
        )
        assert "description ***===> sw-spine-001:3==>sw-leaf-003:53" in str(
            result.output
        )
        assert "description ***===> sw-spine-001:4==>sw-leaf-004:53" in str(
            result.output
        )

        # spine-to-cdu.j2
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> sw-spine-001:5==>sw-cdu-001:50" in str(
            result.output
        )
        assert "description ***===> sw-spine-001:6==>sw-cdu-002:50" in str(
            result.output
        )

        # lag 256
        assert "interface ***===> 1/1/30" in str(result.output)
        assert "interface ***===> 1/1/31" in str(result.output)
        assert "interface ***===> 1/1/32" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.2" in str(result.output)
        # MTL_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.1.1" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.2" in str(result.output)
        # NMN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.3.1" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.2" in str(result.output)
        # HMN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.0.1" in str(result.output)

        # VLAN 7
        # CAN_IP_PRIMARY
        assert "ip address ***===> 192.168.11.2" in str(result.output)
        # CAN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.11.1" in str(result.output)


def test_switch_config_spine_secondary():
    """Test that the `canu switch config` command runs and returns valid secondary spine config."""
    spine_secondary = "sw-spine-002"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                spine_secondary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-spine-002" in str(result.output)

        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # sw-spine-to-leaf.lag.j2
        assert "interface lag ***===> 1" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-spine-002:1==>sw-leaf-001:52" in str(
            result.output
        )
        assert "description ***===> sw-spine-002:2==>sw-leaf-002:52" in str(
            result.output
        )
        assert "description ***===> sw-spine-002:3==>sw-leaf-003:52" in str(
            result.output
        )
        assert "description ***===> sw-spine-002:4==>sw-leaf-004:52" in str(
            result.output
        )

        # spine-to-cdu.j2
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> sw-spine-002:5==>sw-cdu-001:49" in str(
            result.output
        )
        assert "interface ***===> 1/1/6" in str(result.output)
        assert "description ***===> sw-spine-002:6==>sw-cdu-002:49" in str(
            result.output
        )

        # lag 256
        assert "interface ***===> 1/1/30" in str(result.output)
        assert "interface ***===> 1/1/31" in str(result.output)
        assert "interface ***===> 1/1/32" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.3" in str(result.output)
        # MTL_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.1.1" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.3" in str(result.output)
        # NMN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.3.1" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.3" in str(result.output)
        # HMN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.0.1" in str(result.output)

        # VLAN 7
        # CAN_IP_PRIMARY
        assert "ip address ***===> 192.168.11.3" in str(result.output)
        # CAN_IP_GATEWAY
        assert "active-gateway ip ***===> 192.168.11.1" in str(result.output)


def test_switch_config_leaf_primary():
    """Test that the `canu switch config` command runs and returns valid primary leaf config."""
    leaf_primary = "sw-leaf-001"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                leaf_primary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-leaf-001" in str(result.output)
        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # ncn-m.lag.j2
        assert "interface lag ***===> 61 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-leaf-001:1==>ncn-m001:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-001:2==>ncn-m001:ocp:2" in str(
            result.output
        )
        assert "interface lag ***===> 62 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-001:3==>ncn-m002:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-001:4==>ncn-m002:ocp:2" in str(
            result.output
        )

        # ncn-w.lag.j2
        assert "interface lag ***===> 121 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> sw-leaf-001:5==>ncn-w001:ocp:1" in str(
            result.output
        )

        # ncn-s.lag.j2
        assert "interface lag ***===> 71 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> sw-leaf-001:7==>ncn-s001:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-001:8==>ncn-s001:ocp:2" in str(
            result.output
        )
        assert "interface lag ***===> 72 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-001:9==>ncn-s002:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-001:10==>ncn-s002:ocp:2" in str(
            result.output
        )

        # leaf-bmc
        assert "interface lag ***===> 11 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-001:51==>sw-leaf-bmc-001:48" in str(
            result.output
        )
        assert "interface ***===> 1/1/51" in str(result.output)

        # leaf-to-spine
        assert "interface lag ***===> 1 multi-chassis" in str(result.output)
        assert "description leaf_to_spines_lag" in str(result.output)

        assert "interface ***===> 1/1/52" in str(result.output)
        assert "description ***===> sw-leaf-001:52==>sw-spine-002:1" in str(
            result.output
        )
        assert "lag ***===> 1" in str(result.output)

        assert "interface ***===> 1/1/53" in str(result.output)
        assert "description ***===> sw-leaf-001:53==>sw-spine-001:1" in str(
            result.output
        )

        # lag 256
        assert "interface ***===> 1/1/54" in str(result.output)
        assert "interface ***===> 1/1/55" in str(result.output)
        assert "interface ***===> 1/1/56" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.4" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.4" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.4" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.4/32" in str(result.output)


def test_switch_config_leaf_primary_to_uan():
    """Test that the `canu switch config` command runs and returns valid primary leaf config."""
    leaf_primary_3 = "sw-leaf-003"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                leaf_primary_3,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-leaf-003" in str(result.output)

        # ncn-m.lag.j2
        assert "interface lag ***===> 63 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-leaf-003:1==>ncn-m003:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-003:2==>ncn-m003:ocp:2" in str(
            result.output
        )

        # ncn-w.lag.j2
        assert "interface lag ***===> 122 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/3" in str(result.output)
        assert "description ***===> sw-leaf-003:3==>ncn-w002:ocp:1" in str(
            result.output
        )
        assert "interface lag ***===> 123 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-003:4==>ncn-w003:ocp:1" in str(
            result.output
        )

        # ncn-s.lag.j2
        assert "interface lag ***===> 73 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> sw-leaf-003:5==>ncn-s003:ocp:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-003:6==>ncn-s003:ocp:2" in str(
            result.output
        )

        # uan
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> sw-leaf-003:7==>uan001:ocp:1" in str(result.output)
        assert "interface ***===> 1/1/8" in str(result.output)
        assert "interface lag ***===> 181 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-003:8==>uan001:ocp:2" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.6/32" in str(result.output)


def test_switch_config_leaf_secondary():
    """Test that the `canu switch config` command runs and returns valid secondary leaf config."""
    leaf_secondary = "sw-leaf-002"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                leaf_secondary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-leaf-002" in str(result.output)
        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # ncn-m.lag.j2
        assert "interface lag ***===> 61 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-leaf-002:1==>ncn-m001:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-002:2==>ncn-m001:pcie-slot1:2" in str(
            result.output
        )
        assert "interface lag ***===> 62 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-002:3==>ncn-m002:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-002:4==>ncn-m002:pcie-slot1:2" in str(
            result.output
        )

        # ncn-w.lag.j2
        assert "interface lag ***===> 121 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/6" in str(result.output)
        assert "description ***===> sw-leaf-002:6==>ncn-w001:ocp:2" in str(
            result.output
        )

        # ncn-s.lag.j2
        assert "interface lag ***===> 71 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> sw-leaf-002:7==>ncn-s001:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-002:8==>ncn-s001:pcie-slot1:2" in str(
            result.output
        )
        assert "interface lag ***===> 72 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-002:9==>ncn-s002:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-002:10==>ncn-s002:pcie-slot1:2" in str(
            result.output
        )

        # leaf-bmc
        assert "interface lag ***===> 11 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-002:51==>sw-leaf-bmc-001:47" in str(
            result.output
        )
        assert "interface ***===> 1/1/51" in str(result.output)

        # leaf-to-spine
        assert "interface lag ***===> 1 multi-chassis" in str(result.output)
        assert "description leaf_to_spines_lag" in str(result.output)

        assert "interface ***===> 1/1/52" in str(result.output)
        assert "description ***===> sw-leaf-002:52==>sw-spine-002:2" in str(
            result.output
        )
        assert "lag ***===> 1" in str(result.output)

        assert "interface ***===> 1/1/53" in str(result.output)
        assert "description ***===> sw-leaf-002:53==>sw-spine-001:2" in str(
            result.output
        )

        # lag 256
        assert "interface ***===> 1/1/54" in str(result.output)
        assert "interface ***===> 1/1/55" in str(result.output)
        assert "interface ***===> 1/1/56" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.5" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.5" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.5" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.5/32" in str(result.output)


def test_switch_config_leaf_secondary_to_uan():
    """Test that the `canu switch config` command runs and returns valid secondary leaf config."""
    leaf_secondary_3 = "sw-leaf-004"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                leaf_secondary_3,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-leaf-004" in str(result.output)

        # ncn-m.lag.j2
        assert "interface lag ***===> 63 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-leaf-004:1==>ncn-m003:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-004:2==>ncn-m003:pcie-slot1:2" in str(
            result.output
        )

        # ncn-w.lag.j2
        assert "interface lag ***===> 122 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/3" in str(result.output)
        assert "description ***===> sw-leaf-004:3==>ncn-w002:ocp:2" in str(
            result.output
        )
        assert "interface lag ***===> 123 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-004:4==>ncn-w003:ocp:2" in str(
            result.output
        )

        # ncn-s.lag.j2
        assert "interface lag ***===> 73 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> sw-leaf-004:5==>ncn-s003:pcie-slot1:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-004:6==>ncn-s003:pcie-slot1:2" in str(
            result.output
        )

        # uan
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> sw-leaf-004:7==>uan001:pcie-slot1:1" in str(
            result.output
        )
        assert "interface ***===> 1/1/8" in str(result.output)
        assert "interface lag ***===> 181 multi-chassis" in str(result.output)
        assert "description ***===> sw-leaf-004:8==>uan001:pcie-slot1:2" in str(
            result.output
        )

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.7/32" in str(result.output)


def test_switch_config_cdu_primary():
    """Test that the `canu switch config` command runs and returns valid primary cdu config."""
    cdu_primary = "sw-cdu-001"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                cdu_primary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-cdu-001" in str(result.output)
        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # cmm
        assert "interface lag ***===> 170 static" in str(result.output)
        assert "interface ***===> 1/1/2" in str(result.output)
        assert "description ***===> sw-cdu-001:2==>cmm000:1" in str(result.output)
        assert "interface lag ***===> 171 static" in str(result.output)
        assert "description ***===> sw-cdu-001:3==>cmm001:1" in str(result.output)
        assert "interface lag ***===> 172 static" in str(result.output)
        assert "description ***===> sw-cdu-001:4==>cmm002:1" in str(result.output)
        assert "interface lag ***===> 173 static" in str(result.output)
        assert "description ***===> sw-cdu-001:5==>cmm003:1" in str(result.output)

        # cec
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-cdu-001:1==>cec000:1" in str(result.output)

        # cdu-to-spine
        # ip address ***===> ****TBD
        assert "interface ***===> 1/1/49" in str(result.output)
        assert "description ***===> sw-cdu-001:49==>sw-spine-002:5" in str(
            result.output
        )
        assert "description ***===> sw-cdu-001:50==>sw-spine-001:5" in str(
            result.output
        )

        # ip address ***===> ****TBD
        assert "interface ***===> 1/1/50" in str(result.output)
        assert "description ***===> sw-cdu-001:50==>sw-spine-001:5" in str(
            result.output
        )

        # mtn_hmn_vlan.j2
        assert "vlan ***===> 3000" in str(result.output)
        assert "name ***===> cabinet_1000" in str(result.output)
        assert "interface vlan ***===> 3000" in str(result.output)
        assert "ip address ***===> 192.168.100.0/22" in str(result.output)
        assert "active-gateway ip ***===> 192.168.100.1" in str(result.output)

        # mtn_nmn_vlan.j2
        assert "vlan ***===> 2000" in str(result.output)
        assert "name ***===> cabinet_1000" in str(result.output)
        assert "interface vlan ***===> 2000" in str(result.output)
        assert "ip address ***===> 192.168.106.0/22" in str(result.output)
        assert "active-gateway ip ***===> 192.168.106.1" in str(result.output)

        # VSX_KEEPALIVE
        assert "interface ***===> 1/1/48" in str(result.output)
        # VSX_ISL_PORT1
        assert "interface ***===> 1/1/51" in str(result.output)
        # VSX_ISL_PORT2
        assert "interface ***===> 1/1/52" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.16/32" in str(result.output)


def test_switch_config_cdu_secondary():
    """Test that the `canu switch config` command runs and returns valid secondary cdu config."""
    cdu_secondary = "sw-cdu-002"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                cdu_secondary,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-cdu-002" in str(result.output)
        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # cmm
        assert "interface lag ***===> 170 static" in str(result.output)
        assert "interface ***===> 1/1/2" in str(result.output)
        assert "description ***===> sw-cdu-002:2==>cmm000:2" in str(result.output)
        assert "interface lag ***===> 171 static" in str(result.output)
        assert "description ***===> sw-cdu-002:3==>cmm001:2" in str(result.output)
        assert "interface lag ***===> 172 static" in str(result.output)
        assert "description ***===> sw-cdu-002:4==>cmm002:2" in str(result.output)
        assert "interface lag ***===> 173 static" in str(result.output)
        assert "description ***===> sw-cdu-002:5==>cmm003:2" in str(result.output)

        # cdu-to-spine
        # ip address ***===> ****TBD
        assert "interface ***===> 1/1/49" in str(result.output)
        assert "description ***===> sw-cdu-002:49==>sw-spine-002:6" in str(
            result.output
        )

        # ip address ***===> ****TBD
        assert "interface ***===> 1/1/50" in str(result.output)
        assert "description ***===> sw-cdu-002:50==>sw-spine-001:6" in str(
            result.output
        )

        # mtn_hmn_vlan.j2
        assert "vlan ***===> 3000" in str(result.output)
        assert "name ***===> cabinet_1000" in str(result.output)
        assert "interface vlan ***===> 3000" in str(result.output)
        assert "ip address ***===> 192.168.100.0/22" in str(result.output)
        assert "active-gateway ip ***===> 192.168.100.1" in str(result.output)

        # mtn_nmn_vlan.j2
        assert "vlan ***===> 2000" in str(result.output)
        assert "name ***===> cabinet_1000" in str(result.output)
        assert "interface vlan ***===> 2000" in str(result.output)
        assert "ip address ***===> 192.168.106.0/22" in str(result.output)
        assert "active-gateway ip ***===> 192.168.106.1" in str(result.output)

        # VSX_KEEPALIVE
        assert "interface ***===> 1/1/48" in str(result.output)
        # VSX_ISL_PORT1
        assert "interface ***===> 1/1/51" in str(result.output)
        # VSX_ISL_PORT2
        assert "interface ***===> 1/1/52" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.17/32" in str(result.output)


def test_switch_config_leaf_bmc():
    """Test that the `canu switch config` command runs and returns valid leaf-bmc config."""
    leaf_bmc = "sw-leaf-bmc-001"

    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                leaf_bmc,
            ],
        )
        assert result.exit_code == 0
        assert "hostname ***===> sw-leaf-bmc-001" in str(result.output)
        # NTP
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)

        # ACL
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.100.0/17 ***===> 192.168.200.0/17" in str(
            result.output
        )
        assert "deny any ***===> 192.168.200.0/17 ***===> 192.168.3.0/17" in str(
            result.output
        )

        # 'leaf-bmc-to-leaf.lag.j2'
        assert "interface lag ***===> 255" in str(result.output)
        assert "description ***===> leaf_bmc_to_leaf_lag" in str(result.output)
        assert "interface ***===> 1/1/47" in str(result.output)
        assert "description ***===> sw-leaf-bmc-001:47==>sw-leaf-002:51" in str(
            result.output
        )
        assert "interface ***===> 1/1/48" in str(result.output)
        assert "description ***===> sw-leaf-bmc-001:48==>sw-leaf-001:51" in str(
            result.output
        )

        # 'bmc.j2' connection
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> sw-leaf-bmc-001:1==>ncn-m001:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:2==>ncn-m002:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:3==>ncn-m003:bmc:1" in str(
            result.output
        )

        assert "description ***===> sw-leaf-bmc-001:4==>ncn-w001:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:5==>ncn-w002:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:6==>ncn-w003:bmc:1" in str(
            result.output
        )

        assert "description ***===> sw-leaf-bmc-001:7==>ncn-s001:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:8==>ncn-s002:bmc:1" in str(
            result.output
        )
        assert "description ***===> sw-leaf-bmc-001:9==>ncn-s003:bmc:1" in str(
            result.output
        )

        assert "description ***===> sw-leaf-bmc-001:10==>uan001:bmc:1" in str(
            result.output
        )

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.12" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.12" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.12" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===> 10.2.0.12/32" in str(result.output)


def test_switch_config_csi_file_missing():
    """Test that the `canu switch config` command errors on sls_input_file.json file missing."""
    bad_csi_folder = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                bad_csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert (
            "The file sls_input_file.json was not found, check that this is the correct CSI directory"
            in str(result.output)
        )


def test_switch_config_missing_file():
    """Test that the `canu switch config` command fails on missing file."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--shcd'." in str(result.output)


def test_switch_config_bad_file():
    """Test that the `canu switch config` command fails on bad file."""
    bad_file = "does_not_exist.xlsx"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                bad_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--shcd': Could not open file: does_not_exist.xlsx: No such file or directory"
            in str(result.output)
        )


def test_switch_config_missing_tabs():
    """Test that the `canu switch config` command prompts for missing tabs."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
            ],
            input="INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES\n",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)


def test_switch_config_bad_tab():
    """Test that the `canu switch config` command fails on bad tab name."""
    bad_tab = "BAD_TAB_NAME"
    bad_tab_corners = "I14,S48"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                bad_tab,
                "--corners",
                bad_tab_corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 1
        assert f"Tab BAD_TAB_NAME not found in {test_file}" in str(result.output)


def test_switch_config_switch_name_prompt():
    """Test that the `canu switch config` command prompts for missing switch name."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
            ],
            input="sw-spine-001\n",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "interface ***===> 1/1/30" in str(result.output)
        assert "interface ***===> 1/1/31" in str(result.output)
        assert "interface ***===> 1/1/32" in str(result.output)


def test_switch_config_corner_prompt():
    """Test that the `canu switch config` command prompts for corner input and runs."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
            input="J14\nT42\nJ14\nT48\nJ14\nT24\nJ14\nT23",
        )
        assert result.exit_code == 0
        assert "hostname sw-spine-001" in str(result.output)
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "interface ***===> 1/1/30" in str(result.output)
        assert "interface ***===> 1/1/31" in str(result.output)
        assert "interface ***===> 1/1/32" in str(result.output)


def test_switch_config_not_enough_corners():
    """Test that the `canu switch config` command fails on not enough corners."""
    not_enough_corners = "H16"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                not_enough_corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 0
        assert "There were 1 corners entered, but there should be 8." in str(
            result.output
        )


def test_switch_config_bad_switch_name_1():
    """Test that the `canu switch config` command fails on bad switch name."""
    bad_name_1 = "sw-bad"
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
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
    """Test that the `canu switch config` command fails on bad switch name."""
    bad_name_2 = "sw-spine-999"
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
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
    """Test that the `canu switch config` command fails on non switch."""
    non_switch = "ncn-w001"
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                non_switch,
            ],
        )
        assert result.exit_code == 1
        assert (
            f"{non_switch} is not a switch. Only switch config can be generated."
            in str(result.output)
        )


@responses.activate
def test_switch_config_sls():
    """Test that the `canu switch config` command runs with SLS."""
    with runner.isolated_filesystem():
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
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
        assert "ntp server ***===> 192.168.4.4" in str(result.output)
        assert "ntp server ***===> 192.168.4.5" in str(result.output)
        assert "ntp server ***===> 192.168.4.6" in str(result.output)
        assert "deny any ***===> 192.168.3.0/17 ***===> 192.168.0.0/17" in str(
            result.output
        )
        assert "interface ***===> 1/1/30" in str(result.output)
        assert "interface ***===> 1/1/31" in str(result.output)
        assert "interface ***===> 1/1/32" in str(result.output)


@responses.activate
def test_switch_config_sls_token_bad():
    """Test that the `canu switch config` command errors on bad token file."""
    bad_token = "bad_token.token"
    with runner.isolated_filesystem():
        with open(bad_token, "w") as f:
            f.write('{"access_token": "123"}')

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            body=requests.exceptions.HTTPError(
                "503 Server Error: Service Unavailable for url"
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "switch",
                "config",
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
    """Test that the `canu switch config` command errors on no token file."""
    bad_token = "no_token.token"

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "--cache",
            cache_minutes,
            "switch",
            "config",
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
        result.output
    )


@responses.activate
def test_switch_config_sls_address_bad():
    """Test that the `canu switch config` command errors with bad SLS address."""
    bad_sls_address = "192.168.254.254"

    responses.add(
        responses.GET,
        f"https://{bad_sls_address}/apis/sls/v1/networks",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 51] Network is unreachable"
        ),
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "--cache",
            cache_minutes,
            "switch",
            "config",
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
                    }
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
                            {"Name": "sw-agg-001", "IPAddress": "192.168.0.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.0.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.0.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.0.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.0.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.0.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.0.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.0.15"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.0.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.0.17"},
                        ],
                        "VlanID": 4,
                        "Gateway": "192.168.0.1",
                    }
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
                            {"Name": "sw-agg-001", "IPAddress": "192.168.1.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.1.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.1.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.1.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.1.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.1.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.1.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.1.15"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.1.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.1.17"},
                        ],
                        "VlanID": 0,
                        "Gateway": "192.168.1.1",
                    }
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
                            {"Name": "sw-agg-001", "IPAddress": "192.168.3.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.3.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.3.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.3.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.3.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.3.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.3.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.3.15"},
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
                        "Name": "cabinet_1000",
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
                        "CIDR": "192.168.106.0/22",
                        "Name": "cabinet_3000",
                        "VlanID": 3000,
                        "Gateway": "192.168.106.1",
                        "DHCPStart": "192.168.106.10",
                        "DHCPEnd": "192.168.3.254",
                    },
                ],
            },
        },
    }
}
sls_networks = [
    network[x] for network in [sls_input.get("Networks", {})] for x in network
]
