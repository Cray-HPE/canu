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
"""Test CANU validate network bgp commands."""
from unittest.mock import patch

import click.testing
import requests
import responses

from canu.cli import cli


architecture = "tds"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
cache_minutes = 0
asn = 65533
runner = click.testing.CliRunner()


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp(switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.1 Hostname: test-spine" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_full_architecture(switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS with full architecture."""
    full_architecture = "full"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-leaf", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                full_architecture,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.1 Hostname: test-leaf" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_v1_architecture(switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS with full architecture."""
    v1_architecture = "v1"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-leaf", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                v1_architecture,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.1 Hostname: test-leaf" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_file(switch_vendor):
    """Test that the `canu validate network bgp` command runs from a file input and returns PASS."""
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
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.1 Hostname: test-spine" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_verbose(switch_vendor):
    """Test that the `canu validate network bgp` command runs verbose and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "test-spine ===> 192.168.1.2: Established" in str(result.output)
        assert "PASS - IP: 192.168.1.1 Hostname: test-spine" in str(result.output)


def test_validate_bgp_missing_ips():
    """Test that the `canu validate network bgp` command errors on missing IPs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Missing one of the required mutually exclusive options from 'Network cabling IPv4 input sources' option group:"
            in str(result.output)
        )


def test_validate_bgp_mutually_exclusive_ips_and_file():
    """Test that the `canu validate network bgp` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--ips-file",
                "file.txt",
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Mutually exclusive options from 'Network cabling IPv4 input sources' option group cannot be used"
            in str(result.output)
        )


def test_validate_bgp_invalid_ip():
    """Test that the `canu validate network bgp` command errors on invalid IPs."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 2
        assert "These items are not ipv4 addresses" in str(result.output)


def test_validate_bgp_invalid_ip_file():
    """Test that the `canu validate network bgp` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value:" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_bad_ip(switch_vendor):
    """Test that the `canu validate network bgp` command errors on a bad IP."""
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
                "validate",
                "network",
                "bgp",
                "--ips",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.99, check the IP address and try again"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_bad_ip_file(switch_vendor):
    """Test that the `canu validate network bgp` command errors on a bad IP from a file."""
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
                "validate",
                "network",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.99, check the IP address and try again"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_bad_password(switch_vendor):
    """Test that the `canu validate network bgp` command errors on bad credentials."""
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                bad_password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.1, check that this IP is an Aruba switch, or check the username or password"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_fail(switch_vendor):
    """Test that the `canu validate network bgp` command reports that a switch failed bgp check."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=one_idle,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "8320"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "FAIL - IP: 192.168.1.1 Hostname: test-spine" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_fail_verbose(switch_vendor):
    """Test that the `canu validate network bgp` command reports that a switch failed bgp check."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=one_idle,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "8320"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--verbose",
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "test-spine ===> 192.168.1.2: Established" in str(result.output)
        assert "FAIL - IP: 192.168.1.1 Hostname: test-spine" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_not_spine(switch_vendor):
    """Test that the `canu validate network bgp` command reports SKIP on a switch not a spine."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json={},
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-leaf", "platform_name": "8320"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "SKIP - IP: 192.168.1.1 Hostname: test-leaf" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_error_not_spine(switch_vendor):
    """Test that the `canu validate network bgp` command given an error on a switch not a spine."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-agg", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert (
            "test-agg not a spine switch, with TDS architecture BGP config only allowed with spine switches"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_error_not_agg(switch_vendor):
    """Test that the `canu validate network bgp` command given an error on a switch not an agg or leaf."""
    full_architecture = "full"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
            json=all_established,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            json={"hostname": "test-spine", "platform_name": "X86-64"},
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                full_architecture,
            ],
        )
        assert result.exit_code == 0
        assert (
            "test-spine not an agg or leaf switch, with Full architecture BGP config only allowed"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_vendor_error(switch_vendor):
    """Test that the `canu validate network bgp` command errors on 'None' vendor."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = None

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.get_bgp_neighbors_aruba")
@responses.activate
def test_validate_bgp_exception(get_bgp_neighbors_aruba, switch_vendor):
    """Test that the `canu validate network bgp` command errors on exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        get_bgp_neighbors_aruba.side_effect = requests.exceptions.HTTPError

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


# Dell
@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_dell(switch_vendor):
    """Test that the `canu validate network bgp` command runs with Dell switch."""
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "SKIP - IP: 192.168.1.2 Hostname: test-dell" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_dell_http_error(switch_vendor):
    """Test that the `canu validate network bgp` command errors with Dell switch http error."""
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
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.2     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_dell_request_error(switch_vendor):
    """Test that the `canu validate network bgp` command errors with Dell switch request error."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        responses.add(
            responses.GET,
            f"https://{ip_dell}/restconf/data/system-sw-state/sw-version",
            body=requests.exceptions.RequestException(),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.2     - Connection Error" in str(result.output)


# Mellanox
@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_mellanox(switch_vendor):
    """Test that the `canu validate network bgp` command runs with Mellanox switch."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "OK", "status_msg": "Successfully logged-in"},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=bgp_status_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": [{"Hostname": "sw-spine-mellanox"}]},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": {"value": ["MSN2100"]}},
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.3 Hostname: sw-spine-mellanox" in str(
            result.output
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_mellanox_connection_error(switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch connection error."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            status=404,
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.3     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_mellanox_bad_login(switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch bad login."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "ERROR", "status_msg": "Invalid username or password"},
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.3     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@responses.activate
def test_validate_bgp_mellanox_exception(switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "OK", "status_msg": "Successfully logged-in"},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            body=requests.exceptions.HTTPError(),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "bgp",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
                "--architecture",
                architecture,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.3     - Connection Error" in str(result.output)


all_established = {
    "192.168.1.2": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.1.3": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.1.4": {
        "status": {"bgp_peer_state": "Established"},
    },
}

one_idle = {
    "192.168.1.2": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.1.3": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.1.4": {
        "status": {"bgp_peer_state": "Idle"},
    },
}

dell_firmware_mock = {
    "dell-system-software:sw-version": {
        "sw-version": "10.5.1.4",
        "sw-platform": "S4048T-ON",
    }
}

dell_hostname_mock = {"dell-system:hostname": "test-dell"}

bgp_status_mellanox = {
    "status": "OK",
    "executed_command": "show ip bgp summary",
    "status_message": "",
    "data": [
        {
            "VRF name": "default",
        },
        {
            "192.168.1.9": [
                {
                    "State/PfxRcd": "ESTABLISHED/13",
                }
            ],
        },
    ],
}
