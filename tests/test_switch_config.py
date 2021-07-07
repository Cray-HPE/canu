"""Test CANU validate shcd commands."""
import json
import os
from pathlib import Path

import click.testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_0.0.6.xlsx"
test_file = os.path.join(test_file_directory, "data", test_file_name)
architecture = "full"
tabs = "INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T42,J14,T48,J14,T24,J14,T23"
csi_folder = "."
shasta = "1.4"
switch_name = "sw-spine-001"
cache_minutes = 0
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
        # sw-leaf-001
        assert "interface lag ***===> 1" in str(result.output)
        assert "description ***===> sw-leaf-001" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)

        # sw-leaf-004
        assert "interface lag ***===> 4" in str(result.output)
        assert "description ***===> sw-leaf-004" in str(result.output)
        assert "interface ***===> 1/1/4" in str(result.output)

        # sw-cdu-001
        assert "interface ***===> 1/1/5" in str(result.output)
        # assert "interface lag ***===> 4" in str(result.output)
        # assert "description ***===> sw-leaf-004" in str(result.output)

        # lag 99
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
        # sw-leaf-001
        assert "interface lag ***===> 1" in str(result.output)
        assert "description ***===> sw-leaf-001" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)

        # sw-leaf-004
        assert "interface lag ***===> 4" in str(result.output)
        assert "description ***===> sw-leaf-004" in str(result.output)
        assert "interface ***===> 1/1/4" in str(result.output)

        # sw-cdu-001
        assert "interface ***===> 1/1/5" in str(result.output)
        # assert "interface lag ***===> 4" in str(result.output)
        # assert "description ***===> sw-leaf-004" in str(result.output)

        # lag 99
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

        # ncn-m001
        assert "interface lag ***===> 1 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> ncn-m001" in str(result.output)

        # ncn-w001
        assert "interface lag ***===> 5 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/5" in str(result.output)
        assert "description ***===> ncn-w001" in str(result.output)

        # ncn-s001
        assert "interface lag ***===> 7 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> ncn-s001" in str(result.output)

        # uan connection needed

        # leaf-bmc connection needed

        # sw-spine-002
        assert "interface lag ***===> 52" in str(result.output)
        assert "description ***===> sw-spine-002" in str(result.output)
        assert "interface ***===> 1/1/52" in str(result.output)

        # sw-spine-001
        assert "interface lag ***===> 53" in str(result.output)
        assert "description ***===> sw-spine-001" in str(result.output)
        assert "interface ***===> 1/1/53" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.4" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.4" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.4" in str(result.output)


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

        # uan
        assert "interface lag ***===> 7 multi-chassis" in str(result.output)
        assert "description ***===> uan001" in str(result.output)
        assert "interface ***===> 1/1/7" in str(result.output)

        assert "interface lag ***===> 8 multi-chassis" in str(result.output)
        assert "description ***===> uan001" in str(result.output)
        assert "interface ***===> 1/1/8" in str(result.output)


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

        # ncn-m001
        assert "interface lag ***===> 1 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/1" in str(result.output)
        assert "description ***===> ncn-m001" in str(result.output)

        # ncn-w001
        assert "interface lag ***===> 6 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/6" in str(result.output)
        assert "description ***===> ncn-w001" in str(result.output)

        # ncn-s001
        assert "interface lag ***===> 7 multi-chassis" in str(result.output)
        assert "interface ***===> 1/1/7" in str(result.output)
        assert "description ***===> ncn-s001" in str(result.output)

        # uan connection needed

        # leaf-bmc connection needed

        # sw-spine-002
        assert "interface lag ***===> 52" in str(result.output)
        assert "description ***===> sw-spine-002" in str(result.output)
        assert "interface ***===> 1/1/52" in str(result.output)

        # sw-spine-001
        assert "interface lag ***===> 53" in str(result.output)
        assert "description ***===> sw-spine-001" in str(result.output)
        assert "interface ***===> 1/1/53" in str(result.output)

        # VLAN 1
        # MTL_IP
        assert "ip address ***===> 192.168.1.5" in str(result.output)

        # VLAN 2
        # NMN_IP
        assert "ip address ***===> 192.168.3.5" in str(result.output)

        # VLAN 4
        # HMN_IP
        assert "ip address ***===> 192.168.0.5" in str(result.output)


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

        # need cmm connection
        # need cec connection

        # sw-spine-002
        # assert "interface lag ***===> 49" in str(result.output)
        # assert "description ***===> sw-spine-002" in str(result.output)
        assert "interface ***===> 1/1/49" in str(result.output)

        # sw-spine-001
        # assert "interface lag ***===> 50" in str(result.output)
        # assert "description ***===> sw-spine-001" in str(result.output)
        assert "interface ***===> 1/1/50" in str(result.output)

        # VSX_KEEPALIVE
        assert "interface ***===> 1/1/48" in str(result.output)
        # VSX_ISL_PORT1
        assert "interface ***===> 1/1/51" in str(result.output)
        # VSX_ISL_PORT2
        assert "interface ***===> 1/1/52" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===>" in str(result.output)


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

        # need cmm connection
        # need cec connection

        # sw-spine-002
        # assert "interface lag ***===> 49" in str(result.output)
        # assert "description ***===> sw-spine-002" in str(result.output)
        assert "interface ***===> 1/1/49" in str(result.output)

        # sw-spine-001
        # assert "interface lag ***===> 50" in str(result.output)
        # assert "description ***===> sw-spine-001" in str(result.output)
        assert "interface ***===> 1/1/50" in str(result.output)

        # VSX_KEEPALIVE
        assert "interface ***===> 1/1/48" in str(result.output)
        # VSX_ISL_PORT1
        assert "interface ***===> 1/1/51" in str(result.output)
        # VSX_ISL_PORT2
        assert "interface ***===> 1/1/52" in str(result.output)

        # LOOPBACK_IP
        assert "router-id ***===>" in str(result.output)


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

        # need 'sw-leaf-bmc-uplink.j2' connection
        # need 'bmc.j2' connection

        # MTL_IP
        # NMN_IP
        # HMN_IP

        # LOOPBACK_IP
        # assert "router-id ***===>" in str(result.output)


def test_switch_config_csi_file_missing():
    """Error canu init CSI on sls_input_file.json file missing."""
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
        assert result.exit_code == 1
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
    """Test that the `canu switch config` command fails on missing tabs."""
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
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--name",
                switch_name,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--tabs'." in str(result.output)


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


sls_input = {
    "Networks": {
        "CAN": {
            "Name": "CAN",
            "ExtraProperties": {
                "CIDR": "192.168.11.0/24",
                "Subnets": [
                    {
                        "FullName": "CAN Bootstrap DHCP Subnet",
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
                        "FullName": "HMN Management Network Infrastructure",
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
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.0.14"},
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
                        "FullName": "MTL Management Network Infrastructure",
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
            },
        },
        "HMN_MTN": {
            "Name": "HMN_MTN",
            "ExtraProperties": {
                "CIDR": "192.168.200.0/17",
            },
        },
    }
}
