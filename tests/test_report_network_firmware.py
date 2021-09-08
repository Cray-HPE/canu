"""Test CANU report network firmware commands."""
from unittest.mock import patch

import click.testing
from netmiko import ssh_exception
import requests
import responses

from canu.cache import remove_switch_from_cache
from canu.cli import cli


shasta = "1.4"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
cache_minutes = 0
runner = click.testing.CliRunner()


def test_network_cli():
    """Test that the `canu network` command runs."""
    result = runner.invoke(
        cli,
        [
            "report",
            "network",
        ],
    )
    assert result.exit_code == 0


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware(switch_vendor):
    """Test that the `canu report network firmware` command runs and returns valid firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
        remove_switch_from_cache(ip)


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_file(switch_vendor):
    """Test that the `canu report network firmware` command runs from a file input and returns valid firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"

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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
        remove_switch_from_cache(ip)


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_json(switch_vendor):
    """Test that the `canu report network firmware` command runs and returns JSON."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
        remove_switch_from_cache(ip)


def test_network_firmware_missing_ips():
    """Test that the `canu report network firmware` command errors on missing IPs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
    """Test that the `canu report network firmware` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
    """Test that the `canu report network firmware` command errors on invalid IPs."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
    """Test that the `canu report network firmware` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_bad_ip(switch_vendor):
    """Test that the `canu report network firmware` command errors on a bad IP."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_bad_ip_file(switch_vendor):
    """Test that the `canu report network firmware` command errors on a bad IP from a file."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_bad_password(switch_vendor):
    """Test that the `canu report network firmware` command errors on bad credentials."""
    bad_password = "foo"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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


@patch("canu.report.network.firmware.firmware.switch_vendor")
@responses.activate
def test_network_firmware_mismatch(switch_vendor):
    """Test that the `canu report network firmware` command reports that a switch failed firmware check."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
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
        # Remove switch from cache file since it had incorrect information in it from this test
        remove_switch_from_cache(ip)


@patch("canu.report.network.firmware.firmware.switch_vendor")
@patch("canu.report.network.firmware.firmware.get_firmware_dell")
def test_network_firmware_timeout_exception(switch_vendor, get_firmware_dell):
    """Test that the `canu report network firmware` command catches timeout exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        get_firmware_dell.side_effect = ssh_exception.NetmikoTimeoutException
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "192.168.1.2     - Timeout error. Check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.network.firmware.firmware.switch_vendor")
@patch("canu.report.network.firmware.firmware.get_firmware_dell")
def test_network_firmware_auth_exception(switch_vendor, get_firmware_dell):
    """Test that the `canu report network firmware` command catches auth exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        get_firmware_dell.side_effect = ssh_exception.NetmikoAuthenticationException
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "192.168.1.2     - Authentication error. Check the credentials or IP address and try again"
            in str(result.output)
        )


# Dell
@patch("canu.report.network.firmware.firmware.switch_vendor")
@patch("canu.report.network.firmware.firmware.get_firmware_dell")
def test_network_firmware_dell(get_firmware_dell, switch_vendor):
    """Test that the `canu report network firmware` command runs and returns valid dell firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        get_firmware_dell.return_value = {
            "current_version": "10.5.1.4",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        }, {"platform_name": "S3048-ON", "hostname": "test-dell"}
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Pass    192.168.1.2     test-dell           10.5.1.4" in str(
            result.output
        )
        remove_switch_from_cache(ip_dell)


# Mellanox
@patch("canu.report.network.firmware.firmware.switch_vendor")
@patch("canu.report.network.firmware.firmware.get_firmware_mellanox")
def test_network_firmware_mellanox(get_firmware_mellanox, switch_vendor):
    """Test that the `canu report network firmware` command runs and returns valid mellanox firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        get_firmware_mellanox.return_value = {
            "current_version": "3.9.1014",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        }, {"platform_name": "MSN2100", "hostname": "test-mellanox"}
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "firmware",
                "--shasta",
                shasta,
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Pass    192.168.1.3     test-mellanox       3.9.1014" in str(
            result.output
        )
        remove_switch_from_cache(ip_mellanox)
