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
"""Test CANU report switch firmware commands."""
import json
from unittest.mock import patch

from click import testing
from netmiko import ssh_exception
import pytest
import requests
import responses

from canu.cli import cli
from canu.report.switch.firmware.firmware import get_firmware_aruba
from canu.utils.cache import get_switch_from_cache, remove_switch_from_cache


username = "admin"
password = "admin"
ip = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
credentials = {"username": username, "password": password}
csm = "1.0"
cache_minutes = 0
runner = testing.CliRunner()


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


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_get_firmware_aruba_function(switch_vendor):
    """Test the `get_firmware_aruba` function returns valid switch information."""
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

        switch_firmware, switch_info = get_firmware_aruba(
            ip,
            credentials,
            True,
            cache_minutes,
        )
        assert switch_firmware["current_version"] == "Virtual.10.06.0001"
        assert switch_info["hostname"] == "test-switch"
        assert switch_info["platform_name"] == "X86-64"


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_get_firmware_aruba_function_bad_ip(switch_vendor):
    """Test that the `canu report switch firmware` command errors on a bad IP."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )

        with pytest.raises(requests.exceptions.ConnectionError) as connection_error:
            get_firmware_aruba(bad_ip, credentials, True, cache_minutes)

        assert "Failed to establish a new connection" in str(connection_error.value)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_get_firmware_aruba_function_bad_credentials(switch_vendor):
    """Test that the `canu report switch firmware` command errors on bad credentials."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        bad_credentials = {"username": "foo", "password": "foo"}

        with pytest.raises(requests.exceptions.HTTPError) as http_error:
            get_firmware_aruba(ip, bad_credentials, True, cache_minutes)
        assert "Unauthorized for url" in str(http_error.value)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid firmware."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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
        remove_switch_from_cache(ip)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_verbose(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid firmware in verbose mode."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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
        remove_switch_from_cache(ip)


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
                "--csm",
                csm,
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
                "--csm",
                csm,
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


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_bad_ip(switch_vendor):
    """Test that the `canu report switch firmware` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
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
                "--csm",
                csm,
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


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_bad_password(switch_vendor):
    """Test that the `canu report switch firmware` command errors on bad credentials."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_json(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns JSON."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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
        remove_switch_from_cache(ip)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_json_verbose(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns JSON in verbose mode."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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
        remove_switch_from_cache(ip)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_mismatch(switch_vendor):
    """Test that the `canu report switch firmware` command reports that a switch failed firmware check."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_mismatch_verbose(switch_vendor):
    """Test that the `canu report switch firmware` command reports that a switch failed firmware check in verbose mode."""
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
                "switch",
                "firmware",
                "--csm",
                csm,
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


# Dell
@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_dell(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid dell firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/system-sw-state/sw-version",
            json=dell_firmware_mock,
        )
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/dell-system:system/hostname",
            json=dell_hostname_mock,
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Pass - IP: 192.168.1.2 Hostname: test-dell Firmware: 10.5.1.4" in str(
            result.output,
        )
        remove_switch_from_cache(ip_dell)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_dell_cache(switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid dell firmware from cache."""
    minutes = 10
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/system-sw-state/sw-version",
            json=dell_firmware_mock,
        )
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/dell-system:system/hostname",
            json=dell_hostname_mock,
        )
        # Initial run, no cache
        runner.invoke(
            cli,
            [
                "--cache",
                minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--json",
                "--verbose",
            ],
        )
        # Second run, pull from cache
        result = runner.invoke(
            cli,
            [
                "--cache",
                minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--json",
                "--verbose",
            ],
        )
        result_json = json.loads(result.output)
        cached_switch = get_switch_from_cache(ip_dell)

        assert result.exit_code == 0
        assert (
            cached_switch["firmware"]["current_version"]
            == result_json["firmware"]["current_version"]
        )
        assert cached_switch["platform_name"] == result_json["platform_name"]
        assert cached_switch["hostname"] == result_json["hostname"]

        remove_switch_from_cache(ip_dell)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_firmware_dell_exception(switch_vendor):
    """Test that the `canu report switch firmware` command errors."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/system-sw-state/sw-version",
            body=requests.exceptions.HTTPError(),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Error getting firmware version from Dell switch 192.168.1.2" in str(
            result.output,
        )


# mellanox
@patch("canu.report.switch.firmware.firmware.switch_vendor")
@patch("canu.report.switch.firmware.firmware.netmiko_commands")
@responses.activate
def test_switch_firmware_mellanox(netmiko_commands, switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid mellanox firmware."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.return_value = netmiko_commands_mellanox
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Pass - IP: 192.168.1.3 Hostname: test-mellanox Firmware: 3.9.1014"
            in str(result.output)
        )
        remove_switch_from_cache(ip_mellanox)


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@patch("canu.report.switch.firmware.firmware.netmiko_commands")
@responses.activate
def test_switch_firmware_mellanox_timeout(netmiko_commands, switch_vendor):
    """Test that the `canu report switch firmware` command errors on mellanox timeout."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.side_effect = ssh_exception.NetmikoTimeoutException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Timeout error connecting to switch 192.168.1.3, check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@patch("canu.report.switch.firmware.firmware.netmiko_commands")
@responses.activate
def test_switch_firmware_mellanox_auth_exception(netmiko_commands, switch_vendor):
    """Test that the `canu report switch firmware` command errors on mellanox auth exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.side_effect = ssh_exception.NetmikoAuthenticationException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Authentication error connecting to switch 192.168.1.3, check the credentials or IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@patch("canu.report.switch.firmware.firmware.netmiko_commands")
@responses.activate
def test_switch_firmware_mellanox_cache(netmiko_commands, switch_vendor):
    """Test that the `canu report switch firmware` command runs and returns valid mellanox firmware from cache."""
    minutes = 10
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        netmiko_commands.return_value = netmiko_commands_mellanox
        # Initial run, no cache
        runner.invoke(
            cli,
            [
                "--cache",
                minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--json",
                "--verbose",
            ],
        )
        # Second run, pull from cache
        result = runner.invoke(
            cli,
            [
                "--cache",
                minutes,
                "report",
                "switch",
                "firmware",
                "--csm",
                csm,
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--json",
                "--verbose",
            ],
        )
        result_json = json.loads(result.output)
        cached_switch = get_switch_from_cache(ip_mellanox)

        assert result.exit_code == 0
        assert (
            cached_switch["firmware"]["current_version"]
            == result_json["firmware"]["current_version"]
        )
        assert cached_switch["platform_name"] == result_json["platform_name"]
        assert cached_switch["hostname"] == result_json["hostname"]

        remove_switch_from_cache(ip_mellanox)


dell_firmware_mock = {
    "dell-system-software:sw-version": {
        "sw-version": "10.5.1.4",
        "sw-platform": "S4048T-ON",
    },
}

dell_hostname_mock = {"dell-system:hostname": "test-dell"}

netmiko_commands_mellanox = [
    "X86_64 3.9.1014 2020-01-01 01:00:00 x86_64\n",
    "MSN2100\n",
    "   hostname test-mellanox\n   ip dhcp send-hostname\n",
]
