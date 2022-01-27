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
"""Test CANU report network cabling commands."""
from unittest.mock import patch

import requests
import responses
from click import testing
from netmiko import ssh_exception

from canu.cli import cli
from canu.utils.cache import remove_switch_from_cache
from canu.tests.test_report_switch_cabling import arp_neighbors_mellanox
from canu.tests.test_report_switch_cabling import lldp_json_mellanox
from canu.tests.test_report_switch_cabling import mac_address_table_mellanox
from canu.tests.test_report_switch_cabling import mlag_mellanox
from canu.tests.test_report_switch_cabling import netmiko_commands_dell

username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
credentials = {"username": username, "password": password}
cache_minutes = 0
runner = testing.CliRunner()


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_network_cabling(netmiko_command, switch_vendor):
    """Test that the `canu report network cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
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
                "cabling",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "1/1/1   ==> sw-test02      1/1/1" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_network_cabling_file(netmiko_command, switch_vendor):
    """Test that the `canu report network cabling` command runs from a file input and returns valid cabling."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
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
                "cabling",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "1/1/1   ==> sw-test02      1/1/1" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_network_cabling_file_bidirectional(netmiko_command, switch_vendor):
    """Test that the `canu report network cabling` command runs from a file input and returns valid cabling."""
    ip2 = "192.168.1.2"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        with open("test.txt", "w") as f:
            f.write("192.168.1.1\n")
            f.write(ip2)

        # Switch 2
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        # Switch 2
        responses.add(
            responses.POST,
            f"https://{ip2}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info2,
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json2,
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json2,
        )

        responses.add(
            responses.POST,
            f"https://{ip2}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "1/1/1   ==> sw-test02      1/1/1" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_network_cabling_equipment_view(netmiko_command, switch_vendor):
    """Test that the `canu report network cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
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
                "cabling",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--view",
                "equipment",
            ],
        )
        assert result.exit_code == 0
        assert "11:11:11:11:11:11         <=== sw-test01       1/1/3" in str(
            result.output,
        )
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_network_cabling_file_equipment_view_bidirectional(
    netmiko_command,
    switch_vendor,
):
    """Test that the `canu report network cabling` command runs from a file input and returns valid cabling."""
    ip2 = "192.168.1.2"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        with open("test.txt", "w") as f:
            f.write("192.168.1.1\n")
            f.write(ip2)

        # Switch 1
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )
        # Switch 2
        responses.add(
            responses.POST,
            f"https://{ip2}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info2,
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json2,
        )
        responses.add(
            responses.GET,
            f"https://{ip2}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json2,
        )

        responses.add(
            responses.POST,
            f"https://{ip2}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--view",
                "equipment",
            ],
        )
        assert result.exit_code == 0
        assert "11:11:11:11:11:11         <=== sw-test01       1/1/3" in str(
            result.output,
        )
        remove_switch_from_cache(ip)


def test_network_cabling_missing_ips():
    """Test that the `canu report network cabling` command errors on missing IP address."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Missing one of the required mutually exclusive options from 'Network cabling IPv4 input sources' option group"
            in str(result.output)
        )


def test_network_cabling_mutually_exclusive_ips_and_file():
    """Test that the `canu report network cabling` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
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
            "Error: Mutually exclusive options from 'Network cabling IPv4 input sources'"
            in str(result.output)
        )


def test_network_cabling_invalid_ip():
    """Test that the `canu report network cabling` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
                "--ips",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--ips': These items are not ipv4 addresses: ['999.999.999.999']"
            in str(result.output)
        )


def test_network_cabling_invalid_ip_file():
    """Test that the `canu report network cabling` command errors on invalid IPs from a file."""
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
                "cabling",
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


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.network.cabling.cabling.get_lldp")
@responses.activate
def test_network_cabling_bad_ip(get_lldp, switch_vendor):
    """Test that the `canu report network cabling` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        get_lldp.side_effect = requests.exceptions.ConnectionError
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
                "network",
                "cabling",
                "--ips",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.network.cabling.cabling.get_lldp")
@responses.activate
def test_network_cabling_bad_ip_file(get_lldp, switch_vendor):
    """Test that the `canu report network cabling` command errors on a bad IP from a file."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        get_lldp.side_effect = requests.exceptions.ConnectionError
        with open("test.txt", "w") as f:
            f.write(bad_ip)

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
                "network",
                "cabling",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_network_cabling_bad_password(switch_vendor):
    """Test that the `canu report network cabling` command errors on bad credentials."""
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
                "cabling",
                "--ips",
                ip,
                "--username",
                username,
                "--password",
                bad_password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.1, check the IP address and try again."
            in str(result.output)
        )


# Dell
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
@responses.activate
def test_network_cabling_dell(netmiko_commands, switch_vendor):
    """Test that the `canu report network cabling` command runs and returns valid Dell cabling."""
    switch_vendor.return_value = "dell"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.return_value = netmiko_commands_dell

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
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
            "1/1/1   ==> sw-test01      1/1/15             sw-test01                                             Test Switch 1\n"
            "1/1/2   ==> sw-test02      1/1/15             sw-test02                                             Test Switch 2\n"
        ) in str(result.output)
        remove_switch_from_cache(ip_dell)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
def test_network_cabling_dell_timeout(netmiko_commands, switch_vendor):
    """Test that the `canu report network cabling` command errors on ssh timeout."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.side_effect = ssh_exception.NetmikoTimeoutException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
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
            "Timeout error connecting to switch 192.168.1.2, check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
def test_network_cabling_dell_auth(netmiko_commands, switch_vendor):
    """Test that the `canu report network cabling` command errors on ssh auth."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.side_effect = ssh_exception.NetmikoAuthenticationException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
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
            "Auth error connecting to switch 192.168.1.2, check the credentials or IP address and try again."
            in str(result.output)
        )


# Mellanox
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_network_cabling_mellanox(switch_vendor):
    """Test that the `canu report network cabling` command runs and returns valid Mellanox cabling."""
    switch_vendor.return_value = "mellanox"
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
            json=lldp_json_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=mlag_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=mac_address_table_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": [{"Hostname": "sw-test03"}]},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": {"value": ["MSN2100"]}},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=arp_neighbors_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "network",
                "cabling",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "1/1/1   ==> sw-test03      1/1/11             sw-test03                                             Test Switch 3\n"
            "1/1/2   ==> sw-test04      1/1/12             sw-test04                                             Test Switch 4\n"
        ) in str(result.output)
        remove_switch_from_cache(ip_mellanox)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_network_cabling_mellanox_connection_error(switch_vendor):
    """Test that the `canu report network cabling` command errors on connection error."""
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
                "report",
                "network",
                "cabling",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.3, check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_network_cabling_mellanox_exception(switch_vendor):
    """Test that the `canu report network cabling` command errors on switch exception after login."""
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
                "report",
                "network",
                "cabling",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.3, check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_network_cabling_mellanox_bad_login(switch_vendor):
    """Test that the `canu report network cabling` command errors on bad login."""
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
                "report",
                "network",
                "cabling",
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.3, check the IP address and try again."
            in str(result.output)
        )


# Switch 1
switch_info1 = {
    "hostname": "sw-test01",
    "platform_name": "X86-64",
    "system_mac": "aa:aa:aa:aa:aa:aa",
}

lldp_neighbors_json1 = {
    "1%2F1%2F1": {
        "bb:bb:bb:bb:bb:bb,1/1/1": {
            "chassis_id": "bb:bb:bb:bb:bb:bb",
            "mac_addr": "bb:bb:bb:bb:bb:cc",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-test02",
                "port_description": "1/1/1",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        },
    },
    "1%2F1%2F2": {
        "bb:bb:bb:bb:bb:cc,1/1/2": {
            "chassis_id": "bb:bb:bb:bb:bb:bb",
            "mac_addr": "bb:bb:bb:bb:bb:cc",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-test02",
                "port_description": "1/1/2",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/2",
        },
    },
    "1%2F1%2F3": {
        "00:40:a6:00:00:00,00:40:a6:00:00:00": {
            "chassis_id": "00:40:a6:00:00:00",
            "mac_addr": "00:40:a6:00:00:00",
            "neighbor_info": {
                "chassis_description": "",
                "chassis_name": "",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "00:40:a6:00:00:00",
        },
        "11:11:11:11:11:11,11:11:11:11:11:11": {
            "chassis_id": "11:11:11:11:11:11",
            "mac_addr": "11:11:11:11:11:11",
            "neighbor_info": {
                "chassis_description": "",
                "chassis_name": "",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "11:11:11:11:11:11",
        },
    },
    "1%2F1%2F4": {
        "cc:cc:cc:cc:cc:cc,cc:cc:cc:cc:cc:cc": {
            "chassis_id": "cc:cc:cc:cc:cc:cc",
            "mac_addr": "cc:cc:cc:cc:cc:cc",
            "neighbor_info": {
                "chassis_description": "NCN description",
                "chassis_name": "ncn-test",
                "port_description": "mgmt1",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "cc:cc:cc:cc:cc:cc",
        },
    },
}

arp_neighbors_json1 = {
    "192.168.1.2,vlan1": {
        "mac": "00:40:a6:00:00:00",
        "ip_address": "192.168.1.2",
        "port": {"vlan1": "/rest/v10.04/system/interfaces/vlan1"},
    },
    "192.168.1.3,vlan2": {
        "mac": "11:11:11:11:11:11",
        "ip_address": "192.168.1.3",
        "port": {"vlan2": "/rest/v10.04/system/interfaces/vlan2"},
    },
    "192.168.2.2,vlan3": {
        "mac": "00:40:a6:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}

# Switch 2
switch_info2 = {
    "hostname": "sw-test02",
    "platform_name": "X86-64",
    "system_mac": "bb:bb:bb:bb:bb:bb",
}

lldp_neighbors_json2 = {
    "1%2F1%2F1": {
        "aa:aa:aa:aa:aa:aa,1/1/1": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:aa",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-test01",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        },
    },
    "1%2F1%2F2": {
        "aa:aa:aa:aa:aa:bb,1/1/2": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:bb",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-test01",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/2",
        },
    },
}

arp_neighbors_json2 = {
    "192.168.1.2,vlan1": {
        "mac": "00:40:a6:00:00:00",
        "ip_address": "192.168.1.2",
        "port": {"vlan1": "/rest/v10.04/system/interfaces/vlan1"},
    },
    "192.168.1.3,vlan2": {
        "mac": "11:11:11:11:11:11",
        "ip_address": "192.168.1.3",
        "port": {"vlan2": "/rest/v10.04/system/interfaces/vlan2"},
    },
    "192.168.2.2,vlan3": {
        "mac": "00:40:a6:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}

mac_address_table = (
    "MAC age-time            : 300 seconds\n"
    + "Number of MAC addresses : 90\n"
    + "\n"
    + "MAC Address          VLAN     Type                      Port\n"
    + "--------------------------------------------------------------\n"
    + "00:40:a6:00:00:00    2        dynamic                   1/1/3\n"
)
