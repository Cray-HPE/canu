"""Test CANU cli."""

import click.testing
import requests
import responses

from canu.cli import cli


fileout = "fileout.txt"
sls_address = "api-gw-service-nmn.local"
runner = click.testing.CliRunner()


def test_cli():
    """Run canu with no errors."""
    result = runner.invoke(cli)
    assert result.exit_code == 0


# def test_cli_missing_shasta():
#     """Error on Shasta flag required."""
#     result = runner.invoke(
#         cli,
#         [
#             "switch",
#         ],
#     )
#     assert result.exit_code == 2
#     assert "Error: Missing option '--shasta' / '-s'" in str(result.output)


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
        with open("sls_input_file.json", "w") as f:
            f.write(
                '{"Networks": {"CAN": {"Name": "CAN", "ExtraProperties": { "Subnets": [{"IPReservations":'
            )
            f.write(
                '[{"IPAddress": "192.168.1.2","Name": "sw-spine-001"},{"IPAddress": "192.168.1.3","Name": "sw-spine-002"}]}]}}}}'
            )

        result = runner.invoke(
            cli,
            ["init", "--out", fileout, "--csi-folder", "."],
        )
        assert result.exit_code == 0
        assert "2 IP addresses saved to fileout.txt" in str(result.output)


def test_cli_init_csi_file_missing():
    """Error canu init CSI on sls_input_file.json file missing."""
    bad_csi_folder = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "init",
                "--out",
                fileout,
                "--csi-folder",
                bad_csi_folder,
            ],
        )
        assert result.exit_code == 0
        assert (
            "The file sls_input_file.json was not found, check that this is the correct CSI directory"
            in str(result.output)
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
                    "Name": "CAN",
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
                            }
                        ],
                    },
                }
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
    assert "--auth-token option requires an argument" in str(result.output)


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
                "503 Server Error: Service Unavailable for url"
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
        result.output
    )


@responses.activate
def test_cli_init_sls_address_bad():
    """Error canu init SLS with bad SLS address."""
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
