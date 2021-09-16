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
"""Test CANU generate network config."""
import json
import os
from pathlib import Path

import click.testing
import requests
import responses

from canu.cli import cli
from .test_generate_switch_config import sls_input, sls_networks

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_0.0.6.xlsx"
test_file = os.path.join(test_file_directory, "data", test_file_name)
architecture = "full"
tabs = "INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T48,J14,T24,J14,T23"
csi_folder = "."
shasta = "1.4"
folder_name = "test_config"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"
runner = click.testing.CliRunner()


def test_network_config():
    """Test that the `canu generate network config` command runs and generates config."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 Config Generated" in str(result.output)
        assert "sw-spine-002 Config Generated" in str(result.output)
        assert "sw-leaf-001 Config Generated" in str(result.output)
        assert "sw-leaf-002 Config Generated" in str(result.output)
        assert "sw-leaf-003 Config Generated" in str(result.output)
        assert "sw-leaf-004 Config Generated" in str(result.output)
        assert "sw-cdu-001 Config Generated" in str(result.output)
        assert "sw-cdu-002 Config Generated" in str(result.output)
        assert "sw-leaf-bmc-001 Config Generated" in str(result.output)


def test_network_config_folder_prompt():
    """Test that the `canu generate network config` command prompts for missing folder name and runs and generates config."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
            input="test_folder\n",
        )
        assert result.exit_code == 0
        assert "sw-spine-001 Config Generated" in str(result.output)
        assert "sw-spine-002 Config Generated" in str(result.output)
        assert "sw-leaf-001 Config Generated" in str(result.output)
        assert "sw-leaf-002 Config Generated" in str(result.output)
        assert "sw-leaf-003 Config Generated" in str(result.output)
        assert "sw-leaf-004 Config Generated" in str(result.output)
        assert "sw-cdu-001 Config Generated" in str(result.output)
        assert "sw-cdu-002 Config Generated" in str(result.output)
        assert "sw-leaf-bmc-001 Config Generated" in str(result.output)


def test_network_config_csi_file_missing():
    """Test that the `canu generate network config` command errors on sls_input_file.json file missing."""
    bad_csi_folder = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 0
        assert (
            "The file sls_input_file.json was not found, check that this is the correct CSI directory"
            in str(result.output)
        )


def test_network_config_missing_file():
    """Test that the `canu generate network config` command fails on missing file."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
                "--architecture",
                architecture,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--shcd'." in str(result.output)


def test_network_config_bad_file():
    """Test that the `canu generate network config` command fails on bad file."""
    bad_file = "does_not_exist.xlsx"
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--shcd': Could not open file: does_not_exist.xlsx: No such file or directory"
            in str(result.output)
        )


def test_network_config_missing_tabs():
    """Test that the `canu generate network config` command prompts for missing tabs."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--corners",
                corners,
                "--csi-folder",
                csi_folder,
                "--folder",
                folder_name,
            ],
            input="INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES\n",
        )
        assert result.exit_code == 0
        assert "sw-spine-001 Config Generated" in str(result.output)
        assert "sw-spine-002 Config Generated" in str(result.output)
        assert "sw-leaf-001 Config Generated" in str(result.output)
        assert "sw-leaf-002 Config Generated" in str(result.output)
        assert "sw-leaf-003 Config Generated" in str(result.output)
        assert "sw-leaf-004 Config Generated" in str(result.output)
        assert "sw-cdu-001 Config Generated" in str(result.output)
        assert "sw-cdu-002 Config Generated" in str(result.output)
        assert "sw-leaf-bmc-001 Config Generated" in str(result.output)


def test_network_config_bad_tab():
    """Test that the `canu generate network config` command fails on bad tab name."""
    bad_tab = "BAD_TAB_NAME"
    bad_tab_corners = "I14,S48"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 1
        assert f"Tab BAD_TAB_NAME not found in {test_file}" in str(result.output)


def test_network_config_corner_prompt():
    """Test that the `canu generate network config` command prompts for corner input and runs."""
    with runner.isolated_filesystem():
        with open("sls_input_file.json", "w") as f:
            json.dump(sls_input, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--csi-folder",
                csi_folder,
                "--folder",
                folder_name,
            ],
            input="J14\nT42\nJ14\nT48\nJ14\nT24\nJ14\nT23",
        )
        assert result.exit_code == 0
        assert "sw-spine-001 Config Generated" in str(result.output)
        assert "sw-spine-002 Config Generated" in str(result.output)
        assert "sw-leaf-001 Config Generated" in str(result.output)
        assert "sw-leaf-002 Config Generated" in str(result.output)
        assert "sw-leaf-003 Config Generated" in str(result.output)
        assert "sw-leaf-004 Config Generated" in str(result.output)
        assert "sw-cdu-001 Config Generated" in str(result.output)
        assert "sw-cdu-002 Config Generated" in str(result.output)
        assert "sw-leaf-bmc-001 Config Generated" in str(result.output)


def test_network_config_not_enough_corners():
    """Test that the `canu generate network config` command fails on not enough corners."""
    not_enough_corners = "H16"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
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
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 0
        assert "There were 1 corners entered, but there should be 8." in str(
            result.output
        )


@responses.activate
def test_network_config_sls():
    """Test that the `canu generate network config` command runs with SLS."""
    with runner.isolated_filesystem():
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--folder",
                folder_name,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 Config Generated" in str(result.output)
        assert "sw-spine-002 Config Generated" in str(result.output)
        assert "sw-leaf-001 Config Generated" in str(result.output)
        assert "sw-leaf-002 Config Generated" in str(result.output)
        assert "sw-leaf-003 Config Generated" in str(result.output)
        assert "sw-leaf-004 Config Generated" in str(result.output)
        assert "sw-cdu-001 Config Generated" in str(result.output)
        assert "sw-cdu-002 Config Generated" in str(result.output)
        assert "sw-leaf-bmc-001 Config Generated" in str(result.output)


@responses.activate
def test_network_config_sls_token_bad():
    """Test that the `canu generate network config` command errors on bad token file."""
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
                "--cache",
                cache_minutes,
                "generate",
                "network",
                "config",
                "--shasta",
                shasta,
                "--architecture",
                architecture,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
                "--folder",
                folder_name,
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
def test_network_config_sls_token_missing():
    """Test that the `canu generate network config` command errors on no token file."""
    bad_token = "no_token.token"

    result = runner.invoke(
        cli,
        [
            "--cache",
            cache_minutes,
            "generate",
            "network",
            "config",
            "--shasta",
            shasta,
            "--architecture",
            architecture,
            "--shcd",
            test_file,
            "--tabs",
            tabs,
            "--corners",
            corners,
            "--folder",
            folder_name,
            "--auth-token",
            bad_token,
        ],
    )
    assert result.exit_code == 0
    assert "Invalid token file, generate another token or try again." in str(
        result.output
    )


@responses.activate
def test_network_config_sls_address_bad():
    """Test that the `canu generate network config` command errors with bad SLS address."""
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
            "--cache",
            cache_minutes,
            "generate",
            "network",
            "config",
            "--shasta",
            shasta,
            "--architecture",
            architecture,
            "--shcd",
            test_file,
            "--tabs",
            tabs,
            "--corners",
            corners,
            "--folder",
            folder_name,
            "--sls-address",
            bad_sls_address,
        ],
    )
    assert result.exit_code == 0
    assert (
        "Error connecting to SLS 192.168.254.254, check the address or pass in a new address using --sls-address."
        in str(result.output)
    )
