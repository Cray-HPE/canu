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
from os import path
from pathlib import Path

from click import testing
import pkg_resources

from canu.cli import cli
from tests.lib.diff import diff_config_files

test_file_directory = Path(__file__).resolve().parent
data_directory = path.join(test_file_directory, "data")

csm = "1.5"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

sls_file_name = "sls_input_file_csm_1.2.json"
sls_file = path.join(data_directory, sls_file_name)

# Full systems
test_shcd_name = "Full_Architecture_Golden_Config_1.1.5.xlsx"
test_shcd_file = path.join(data_directory, test_shcd_name)
custom_file_name = "aruba_custom.yaml"
custom_file = path.join(data_directory, custom_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T53,J14,T34,J14,T27"

# TDS systems
test_shcd_name_tds = "TDS_Architecture_Golden_Config_1.1.5.xlsx"
test_shcd_file_tds = path.join(test_file_directory, "data", test_shcd_name_tds)
architecture_tds = "tds"
tabs_tds = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners_tds = "J14,T30,J14,T53,J14,T32,J14,T27"

canu_version = pkg_resources.get_distribution("canu").version

banner_version = f"# CANU version: {canu_version}\n"

runner = testing.CliRunner()


def test_switch_config_spine_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary spine config."""
    switch_name = "sw-spine-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_spine_primary_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid primary spine config."""
    switch_name = "sw-spine-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )

        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_spine_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary spine config."""
    switch_name = "sw-spine-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )

        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_spine_secondary_custom():
    """Test that the `canu generate switch config custom` command runs and returns valid primary spine config."""
    switch_name = "sw-spine-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )

        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary leaf config."""
    switch_name = "sw-leaf-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_primary_custom():
    """Test that the `canu generate switch config` command runs and returns valid custom primary leaf config."""
    switch_name = "sw-leaf-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary leaf config."""
    switch_name = "sw-leaf-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_secondary_custom():
    """Test that the `canu generate switch config` command runs and returns valid secondary leaf custom config."""
    switch_name = "sw-leaf-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_bmc():
    """Test that the `canu generate switch config` command runs and returns valid leaf bmc."""
    switch_name = "sw-leaf-bmc-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_bmc_custom():
    """Test that the `canu generate switch config` command runs and returns valid leaf bmc custom config."""
    switch_name = "sw-leaf-bmc-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary cdu config."""
    switch_name = "sw-cdu-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_primary_custom():
    """Test that the `canu generate switch config` command runs and returns valid custom primary cdu config."""
    switch_name = "sw-cdu-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary cdu config."""
    switch_name = "sw-cdu-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_secondary_custom():
    """Test that the `canu generate switch config` command runs and returns valid secondary cdu custom config."""
    switch_name = "sw-cdu-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_primary():
    """Test that the `canu generate switch config` command runs and returns valid primary edge config."""
    switch_name = "sw-edge-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_primary_custom():
    """Test that the `canu generate switch config` command runs and returns valid custom primary edge config."""
    switch_name = "sw-edge-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_secondary():
    """Test that the `canu generate switch config` command runs and returns valid secondary edge config."""
    switch_name = "sw-edge-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_secondary_custom():
    """Test that the `canu generate switch config` command runs and returns valid secondary edge custom config."""
    switch_name = "sw-edge-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/full_configs_custom_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                test_shcd_file,
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
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_spine_primary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds primary spine config."""
    switch_name = "sw-spine-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_spine_secondary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds secondary spine config."""
    switch_name = "sw-spine-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_leaf_bmc_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds leaf-bmc config."""
    switch_name = "sw-leaf-bmc-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_primary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds primary cdu config."""
    switch_name = "sw-cdu-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_cdu_secondary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds secondary cdu config."""
    switch_name = "sw-cdu-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_primary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds primary edge config."""
    switch_name = "sw-edge-001"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_switch_config_edge_secondary_tds():
    """Test that the `canu generate switch config` command runs and returns valid tds secondary edge config."""
    switch_name = "sw-edge-002"
    config_file = f"{switch_name}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/tds_configs_{csm}/{config_file}")

    with runner.isolated_filesystem():
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
                architecture_tds,
                "--shcd",
                test_shcd_file_tds,
                "--tabs",
                tabs_tds,
                "--corners",
                corners_tds,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0
