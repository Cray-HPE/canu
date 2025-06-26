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
"""Test CANU backup network."""

from pathlib import Path
from unittest.mock import patch

import requests
import responses
from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

sls_address = "api-gw-service-nmn.local"
runner = testing.CliRunner()
username = "user"
password = "password"
folder = "./"
test_secret = "dGVzdC1zZWNyZXQ="  # base64 encoded "test-secret"


@patch("canu.utils.sls.config.load_kube_config")
@patch("canu.utils.sls.client.CoreV1Api")
@responses.activate
def test_backup_network_sls_address_bad(mock_core_v1, mock_load_kube_config):
    """Test that the `canu backup network config` command errors with bad SLS address."""
    bad_sls_address = "192.168.254.254"

    # Mock Kubernetes client
    mock_secret_obj = mock_core_v1.return_value.list_namespaced_secret.return_value
    mock_secret_obj.to_dict.return_value = {
        "items": [{"data": {"client-secret": test_secret}}],
    }

    # Mock keycloak token request
    responses.add(
        responses.POST,
        "https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token",
        json={"access_token": "test-token"},
    )

    # Mock SLS networks request - this should fail
    responses.add(
        responses.GET,
        f"https://api-gw-service-nmn.local/apis/sls/v1/networks",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 51] Network is unreachable",
        ),
    )

    result = runner.invoke(
        cli,
        [
            "backup",
            "network",
            "--folder",
            folder,
            "--sls-address",
            bad_sls_address,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 1
    print(result.output)
    assert "Error calling https://api-gw-service-nmn.local/apis/sls/v1/networks:" in str(result.output)


def test_backup_network_sls_file_missing():
    """Test that the `canu backup network` command errors on sls_file.json file missing."""
    bad_sls_file = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "backup",
                "network",
                "--sls-file",
                bad_sls_file,
                "password",
                password,
                "--folder",
                folder,
            ],
        )
        assert result.exit_code == 2
        assert "No such file or directory" in str(result.output)
