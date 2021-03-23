"""
Test CANU.
"""
import click.testing
import requests
import responses

from canu.cli import cli


shasta = "1.4"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
runner = click.testing.CliRunner()


def test_network_cli():

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
        ],
    )
    assert result.exit_code == 0


@responses.activate
def test_network_firmware():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            ips,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_network_firmware_file():
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/firmware",
            json={
                "current_version": "Virtual.10.06.0001",
                "primary_version": "",
                "secondary_version": "",
                "default_image": "",
                "booted_image": "",
            },
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-switch", "platform_name": "X86-64"},
        )
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "network",
                "firmware",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_network_firmware_json():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            ips,
            "--username",
            username,
            "--password",
            password,
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"current_version": "Virtual.10.06.0001"' in str(result.output)
    assert '"status": "Pass"' in str(result.output)


def test_network_firmware_missing_ips():

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 2
    assert (
        "Error: Missing one of the required mutually exclusive options from 'Switch IPv4 input sources' option group:"
        in str(result.output)
    )


def test_network_firmware_mutually_exclusive_ips_and_file():

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--username",
            username,
            "--password",
            password,
            "--ips",
            ips,
            "--ips-file",
            "file.txt",
        ],
    )
    assert result.exit_code == 2
    assert (
        "Error: Mutually exclusive options from 'Switch IPv4 input sources' option group cannot be used at the same time"
        in str(result.output)
    )


def test_network_firmware_invalid_ip():

    invalid_ip = "999.999.999.999"

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            invalid_ip,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 2
    assert "These items are not ipv4 addresses" in str(result.output)


def test_network_firmware_invalid_ip_file():

    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "network",
                "firmware",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value:" in str(result.output)


@responses.activate
def test_network_firmware_bad_ip():

    bad_ip = "192.168.1.99"

    responses.add(
        responses.POST,
        f"https://{bad_ip}/rest/v10.04/login",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 60] Operation timed out'))"
        ),
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            bad_ip,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "Error - 1 switches" in str(result.output)


@responses.activate
def test_network_firmware_bad_ip_file():

    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(bad_ip)

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))"
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "network",
                "firmware",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Error - 1 switches" in str(result.output)


@responses.activate
def test_network_firmware_bad_password():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
        body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
    )

    bad_password = "foo"
    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            ips,
            "--username",
            username,
            "--password",
            bad_password,
        ],
    )
    assert result.exit_code == 0
    assert "Error - 1 switches" in str(result.output)


@responses.activate
def test_network_firmware_mismatch():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "8320"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "network",
            "firmware",
            "--ips",
            ips,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "Fail - 1 switches" in str(result.output)
