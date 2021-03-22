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
    assert "Missing option '--ips'" in str(result.output)


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
    print("+++bad IPs", result.output)
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
