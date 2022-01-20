# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""Test CANU test."""

from os import path
from pathlib import Path

from click import testing
import requests
import responses

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent


test_file_name = "Full_Architecture_Golden_Config_0.0.6.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
override_file_name = "override.yaml"
override_file = path.join(test_file_directory, "data", override_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T44,J14,T48,J14,T28,J14,T27"
sls_file = "sls_file.json"
csm = "1.2"
folder_name = "test_config"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"
runner = testing.CliRunner()


@responses.activate
def test_test_sls_address_bad():
    """Test that the `canu generate network config` command errors with bad SLS address."""
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
            "test",
            "--sls-address",
            bad_sls_address,
        ],
    )
    assert result.exit_code == 1
    print(result.output)
    assert "Error collecting secret from Kubernetes:" in str(result.output)


def test_network_config_csi_file_missing():
    """Test that the `canu generate network config` command errors on sls_file.json file missing."""
    bad_sls_file = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "test",
                "--sls-file",
                bad_sls_file,
            ],
        )
        assert result.exit_code == 2
        assert "No such file or directory" in str(result.output)
