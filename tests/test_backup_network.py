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
"""Test CANU backup network."""

from pathlib import Path

from click import testing
import requests
import responses

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

sls_address = "api-gw-service-nmn.local"
runner = testing.CliRunner()
username = "user"
password = "password"
folder = "./"


@responses.activate
def test_backup_network_sls_address_bad():
    """Test that the `canu backup network config` command errors with bad SLS address."""
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
    assert "Error collecting secret from Kubernetes:" in str(result.output)


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
