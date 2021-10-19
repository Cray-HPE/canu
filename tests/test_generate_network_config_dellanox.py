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
from os import path
from pathlib import Path

from click import testing
import requests
import responses

from canu.cli import cli
from .test_generate_switch_config_dellanox import sls_input, sls_networks

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Architecture_Golden_Config_Dellanox.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
override_file_name = "override.yaml"
override_file = path.join(test_file_directory, "data", override_file_name)
architecture = "v1"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T30,J14,T48,J14,T28,J14,T27"
sls_file = "sls_file.json"
shasta = "1.4"
folder_name = "test_config"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

runner = testing.CliRunner()

def test_network_config():
    """Test that the `canu generate network config` command runs and generates config."""
    with runner.isolated_filesystem():
        with open(sls_file, "w") as f:
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
                "--sls-file",
                sls_file,
                "--folder",
                folder_name,
            ],
        )
        print(result.output)
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
        print(result.output)