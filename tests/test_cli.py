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
"""Test CANU cli."""
from os import urandom

from click import testing
import requests
import responses

from canu.cli import cli
from canu.utils.cache import remove_switch_from_cache


fileout = "fileout.txt"
sls_address = "api-gw-service-nmn.local"
runner = testing.CliRunner()


def test_cli():
    """Run canu with no errors."""
    result = runner.invoke(cli)
    assert result.exit_code == 0


def test_cli_init_missing_out():
    """Error canu init on no --out flag."""
    result = runner.invoke(
        cli,
        [
            "init",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing option '--out'." in str(result.output)


def test_cli_init_csi_good():
    """Run canu init CSI with no errors."""
    with runner.isolated_filesystem():
        with open("sls_file.json", "w") as f:
            f.write(
                '{"Networks": {"NMN": {"Name": "NMN", "ExtraProperties": { "Subnets": [{"IPReservations":',
            )
            f.write(
                '[{"IPAddress": "192.168.1.2","Name": "sw-spine-001"},{"IPAddress": "192.168.1.3","Name": "sw-spine-002"}]}]}}}}',
            )

        result = runner.invoke(
            cli,
            ["init", "--out", fileout, "--sls-file", "sls_file.json"],
        )
        assert result.exit_code == 0
        assert "2 IP addresses saved to fileout.txt" in str(result.output)
        remove_switch_from_cache("192.168.1.2")
        remove_switch_from_cache("192.168.1.3")


def test_cli_init_sls_file_missing():
    """Error canu init SLS on sls_file.json file missing."""
    bad_sls_file = "bad_sls_file.json"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "init",
                "--out",
                fileout,
                "--sls-file",
                bad_sls_file,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value for '--sls-file':" in str(result.output)


def test_cli_init_sls_invalid_json():
    """Error canu init SLS on sls_file.json being invalid JSON."""
    bad_sls_file = "invalid_json_sls_file.json"
    with runner.isolated_filesystem():
        # Generate junk data in what should be a json file
        with open(bad_sls_file, "wb") as f:
            f.write(urandom(128))
        result = runner.invoke(
            cli,
            [
                "init",
                "--out",
                fileout,
                "--sls-file",
                bad_sls_file,
            ],
        )
        assert result.exit_code == 0
        assert "The file invalid_json_sls_file.json is not valid JSON" in str(
            result.output,
        )


@responses.activate
def test_cli_init_sls_good():
    """Run canu init SLS with no errors."""
    with runner.isolated_filesystem():
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=[
                {
                    "Name": "NMN",
                    "ExtraProperties": {
                        "Subnets": [
                            {
                                "IPReservations": [
                                    {
                                        "IPAddress": "192.168.1.2",
                                        "Name": "sw-spine-001",
                                    },
                                    {
                                        "IPAddress": "192.168.1.3",
                                        "Name": "sw-spine-002",
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        )
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/hardware",
            json=[
                {
                    "d0w1": {
                        "ExtraProperties": {
                            "Brand": "Aruba",
                            "Aliases": ["sw-spine-001"],
                        },
                    },
                    "d0w2": {
                        "ExtraProperties": {
                            "Brand": "Aruba",
                            "Aliases": ["sw-spine-002"],
                        },
                    },
                },
            ],
        )

        result = runner.invoke(
            cli,
            [
                "init",
                "--out",
                fileout,
            ],
        )
        assert result.exit_code == 0
        assert "2 IP addresses saved to fileout.txt" in str(result.output)
        remove_switch_from_cache("192.168.1.2")
        remove_switch_from_cache("192.168.1.3")


def test_cli_init_sls_token_flag_missing():
    """Error canu init SLS with token flag missing."""
    result = runner.invoke(
        cli,
        [
            "init",
            "--out",
            fileout,
            "--auth-token",
        ],
    )
    assert result.exit_code == 2
    assert "requires an argument" in str(result.output)


@responses.activate
def test_cli_init_sls_token_bad():
    """Error canu init SLS with bad token."""
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
            ["init", "--out", fileout, "--auth-token", bad_token],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting SLS api-gw-service-nmn.local, check that the token is valid, or generate a new one"
            in str(result.output)
        )


@responses.activate
def test_cli_init_sls_token_missing():
    """Error canu init SLS with no token file."""
    bad_token = "no_token.token"

    result = runner.invoke(
        cli,
        ["init", "--out", fileout, "--auth-token", bad_token],
    )
    assert result.exit_code == 0
    assert "Invalid token file, generate another token or try again." in str(
        result.output,
    )


@responses.activate
def test_cli_init_sls_address_bad():
    """Error canu init SLS with bad SLS address."""
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
            "init",
            "--out",
            fileout,
            "--sls-address",
            bad_sls_address,
        ],
    )
    assert result.exit_code == 0
    assert (
        "Error connecting to SLS 192.168.254.254, check the address or pass in a new address using --sls-address."
        in str(result.output)
    )
