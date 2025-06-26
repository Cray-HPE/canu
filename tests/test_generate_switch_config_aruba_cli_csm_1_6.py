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

csm = "1.6"

test_file_name = "Full_Architecture_Golden_Config_1.1.5.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
custom_file_name = "aruba_custom.yaml"
custom_file = path.join(test_file_directory, "data", custom_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T53,J14,T34,J14,T27"
sls_file_name = "sls_input_file_csm_1.2.json"
sls_file = path.join(test_file_directory, "data", sls_file_name)

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
