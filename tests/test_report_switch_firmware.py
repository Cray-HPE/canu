"""Test CANU report switch firmware commands."""
import json

import click.testing
import pytest
import requests
import responses

from canu.cache import remove_switch_from_cache
from canu.cli import cli
from canu.report.switch.firmware.firmware import get_firmware


username = "admin"
password = "admin"
ip = "192.168.1.1"
credentials = {"username": username, "password": password}
shasta = "1.4"
cache_minutes = 0
runner = click.testing.CliRunner()


def test_switch_cli():
    """Test that the `canu report switch` command runs."""
    result = runner.invoke(
        cli,
        [
            "report",
            "switch",
        ],
    )
    assert result.exit_code == 0


@responses.activate
def test_get_firmware_function():
    """Test the `get_firmware` function returns valid switch information."""
    with runner.isolated_filesystem():
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

        switch_firmware, switch_info = get_firmware(
            ip, credentials, True, cache_minutes
        )

        assert switch_firmware["current_version"] == "Virtual.10.06.0001"
        assert switch_info["hostname"] == "test-switch"
        assert switch_info["platform_name"] == "X86-64"


@responses.activate
def test_get_firmware_function_bad_ip():
    """Test that the `canu report switch firmware` command errors on a bad IP."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))"
            ),
        )

        with pytest.raises(requests.exceptions.ConnectionError) as connection_error:
            get_firmware(bad_ip, credentials, True, cache_minutes)

        assert "Failed to establish a new connection" in str(connection_error.value)


@responses.activate
def test_get_firmware_function_bad_credentials():
    """Test that the `canu report switch firmware` command errors on bad credentials."""
    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        bad_credentials = {"username": "foo", "password": "foo"}

        with pytest.raises(requests.exceptions.HTTPError) as http_error:
            get_firmware(ip, bad_credentials, True, cache_minutes)
        assert "Unauthorized for url" in str(http_error.value)


@responses.activate
def test_switch_firmware():
    """Test that the `canu report switch firmware` command runs and returns valid firmware."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_switch_firmware_verbose():
    """Test that the `canu report switch firmware` command runs and returns valid firmware in verbose mode."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "Virtual.10.06.0001" in str(result.output)
        assert ip in str(result.output)


def test_switch_firmware_missing_ip():
    """Test that the `canu report switch firmware` command errors on missing IP address."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
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
        assert "Missing option '--ip'" in str(result.output)


def test_switch_firmware_invalid_ip():
    """Test that the `canu report switch firmware` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_firmware_bad_ip():
    """Test that the `canu report switch firmware` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_firmware_bad_password():
    """Test that the `canu report switch firmware` command errors on bad credentials."""
    bad_password = "foo"

    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                bad_password,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "check the username or password" in str(result.output)


@responses.activate
def test_switch_firmware_json():
    """Test that the `canu report switch firmware` command runs and returns JSON."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--json",
            ],
        )
        assert result.exit_code == 0
        assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_switch_firmware_json_verbose():
    """Test that the `canu report switch firmware` command runs and returns JSON in verbose mode."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--json",
                "--verbose",
            ],
        )
        assert result.exit_code == 0

        result_json = json.loads(result.output)
        assert result_json["firmware"]["current_version"] == "Virtual.10.06.0001"
        assert result_json["status"] == "Pass"


@responses.activate
def test_switch_firmware_mismatch():
    """Test that the `canu report switch firmware` command reports that a switch failed firmware check."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Firmware should be in:" in str(result.output)

        # Remove switch from cache file since it had incorrect information in it from this test
        remove_switch_from_cache(ip)


@responses.activate
def test_switch_firmware_mismatch_verbose():
    """Test that the `canu report switch firmware` command reports that a switch failed firmware check in verbose mode."""
    with runner.isolated_filesystem():
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
                "switch",
                "firmware",
                "--shasta",
                shasta,
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "Firmware should be in:" in str(result.output)

        # Remove switch from cache file since it had incorrect information in it from this test
        remove_switch_from_cache(ip)
