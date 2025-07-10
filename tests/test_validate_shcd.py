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
"""Test CANU validate shcd commands."""
import json
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent


test_file_name = "test_validate_shcd.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
architecture = "tds"
tabs = "25G_10G"
corners = "I14,S48"
runner = testing.CliRunner()


def test_validate_shcd():
    """Test that the `canu validate shcd` command runs and returns valid cabling."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-002 connects to 17 nodes:" in str(result.output)


def test_validate_shcd_full():
    """Test that the `canu validate shcd` command runs and returns valid cabling with '--architecture full' flag."""
    full_architecture = "full"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                full_architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "sw-leaf-002 connects to 17 nodes:" in str(result.output)


def test_validate_shcd_missing_file():
    """Test that the `canu validate shcd` command fails on missing file."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--shcd'." in str(result.output)


def test_validate_shcd_bad_file():
    """Test that the `canu validate shcd` command fails on bad file."""
    bad_file = "does_not_exist.xlsx"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                bad_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value for '--shcd':" in str(result.output)


def test_validate_shcd_missing_tabs():
    """Test that the `canu validate shcd` command prompts for missing tabs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--corners",
                corners,
            ],
            input="25G_10G\n",
        )
        assert result.exit_code == 0
        assert "sw-spine-001 connects to 18 nodes:" in str(result.output)


def test_validate_shcd_bad_tab():
    """Test that the `canu validate shcd` command fails on bad tab name."""
    bad_tab = "NMN"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                bad_tab,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 1
        assert f"Tab NMN not found in {test_file}" in str(result.output)


def test_validate_shcd_corner_prompt():
    """Test that the `canu validate shcd` command prompts for corner input and runs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
            ],
            input="I14\nS48",
        )
        assert result.exit_code == 0
        assert "sw-spine-002 connects to 17 nodes:" in str(result.output)


def test_validate_shcd_corners_too_narrow():
    """Test that the `canu validate shcd` command fails on too narrow area."""
    corners_too_narrow = "I16,P48"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_too_narrow,
            ],
        )
        assert result.exit_code == 1
        assert "Not enough columns exist." in str(result.output)


def test_validate_shcd_corners_too_high():
    """Test that the `canu validate shcd` command fails on empty headers."""
    corners_too_high = "H16,S48"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_too_high,
            ],
        )
        assert result.exit_code == 1
        assert "On tab 25G_10G, header column Source not found." in str(result.output)
        assert "On tab 25G_10G, the header is formatted incorrectly." in str(
            result.output,
        )


def test_validate_shcd_corners_bad_cell():
    """Test that the `canu validate shcd` command fails on bad cell."""
    corners_bad_cell = "16,S48"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_bad_cell,
            ],
        )
        assert result.exit_code == 1
        assert "Bad range of cells entered for tab 25G_10G." in str(result.output)


def test_validate_shcd_not_enough_corners():
    """Test that the `canu validate shcd` command fails on not enough corners."""
    not_enough_corners = "H16"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                not_enough_corners,
            ],
        )
        assert result.exit_code == 0
        assert "There were 1 corners entered, but there should be 2." in str(
            result.output,
        )


def test_validate_shcd_bad_headers():
    """Test that the `canu validate shcd` command fails on bad headers."""
    bad_header_tab = "Bad_Headers"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                bad_header_tab,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 1
        assert "On tab Bad_Headers, header column Slot not found" in str(result.output)


def test_validate_shcd_bad_architectural_definition():
    """Test that the `canu validate shcd` command fails with bad connections."""
    corners_bad_row = "I14,S50"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_bad_row,
            ],
        )
        assert result.exit_code == 1
        assert "The plan-of-record architectural definition does not allow connections" in str(
            result.output,
        )


def test_validate_shcd_port_reuse():
    """Test that the `canu validate shcd` command fails when a port is used multiple times."""
    multiple_connections_tab = "More_connections"
    multiple_connections_corners = "I14,S20"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                multiple_connections_tab,
                "--corners",
                multiple_connections_corners,
                "--log",
                "DEBUG",
            ],
        )
        assert result.exit_code == 1
        assert "Failed to connect sw-spine-001 to sw-spine-002" in str(
            result.output,
        )


def test_validate_shcd_json():
    """Test that the `canu validate shcd` command runs and returns valid JSON cabling."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--json",
            ],
        )
        assert result.exit_code == 0

        result_json = json.loads(result.output)

        assert result_json["topology"][-1]["common_name"] == "sw-cdu-002"
        assert result_json["topology"][-1]["architecture"] == "mountain_compute_leaf"
        assert result_json["topology"][-1]["location"]["rack"] == "x3000"
        assert result_json["topology"][-1]["location"]["elevation"] == "u13"


def test_validate_shcd_vi():
    """Test that the `canu validate shcd` command runs and returns valid cabling for Dell and Mellanox V1 arch."""
    architecture_v1 = "v1"
    test_file_name_v1 = "Architecture_Golden_Config_Dellanox.xlsx"
    test_file_v1 = path.join(test_file_directory, "data", test_file_name_v1)
    tabs_v1 = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
    corners_v1 = "J14,T30,J14,T34,J14,T28,J14,T27"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                architecture_v1,
                "--shcd",
                test_file_v1,
                "--tabs",
                tabs_v1,
                "--corners",
                corners_v1,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-002 connects to 18 nodes:" in str(result.output)


def test_validate_shcd_subrack():
    """Test that the `canu validate shcd` command runs and returns valid cabling including SubRack."""
    tabs_subrack = "25G_10G,HMN"
    corners_subrack = "I14,S48,I14,T19"
    full_architecture = "full"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "shcd",
                "--architecture",
                full_architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs_subrack,
                "--corners",
                corners_subrack,
                "--log",
                "DEBUG",
            ],
        )
        assert result.exit_code == 0
        assert "15: cn008 connects to 1 nodes: [16]" in str(result.output)
        assert "16: SubRack002-rcm connects to 2 nodes: [15, 17]" in str(result.output)
        assert "17: sw-leaf-bmc-002 connects to 2 nodes: [18, 16]" in str(result.output)
        assert "18: cn004 connects to 2 nodes: [19, 17]" in str(result.output)
        assert "19: SubRack001-rcm connects to 1 nodes: [18]" in str(result.output)
