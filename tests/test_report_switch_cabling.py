"""Test CANU report switch cabling commands."""

import click.testing
import pytest
import requests
import responses

from canu.cli import cli
from canu.report.switch.cabling.cabling import get_lldp


username = "admin"
password = "admin"
ip = "192.168.1.1"
credentials = {"username": username, "password": password}
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
def test_get_lldp_function():
    """Test the `get_lldp` function returns valid switch information."""
    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json={
                "hostname": "test-switch",
                "platform_name": "X86-64",
                "system_mac": "aa:aa:aa:aa:aa:aa",
            },
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        switch_info, switch_dict, arp = get_lldp(ip, credentials, True)

        assert switch_dict.keys() == {"1/1/1", "1/1/2", "1/1/3", "1/1/4"}
        assert switch_dict["1/1/1"][0]["chassis_id"] == "aa:bb:cc:88:99:00"
        assert switch_dict["1/1/2"][0]["chassis_id"] == "aa:bb:cc:88:00:00"
        assert switch_dict["1/1/3"][0]["chassis_id"] == "00:00:00:00:00:00"

        assert switch_info["hostname"] == "test-switch"
        assert switch_info["ip"] == ip

        assert arp["192.168.1.2,vlan1"]["mac"] == "00:00:00:00:00:00"
        assert list(arp["192.168.1.2,vlan1"]["port"])[0] == "vlan1"


@responses.activate
def test_get_lldp_function_bad_ip():
    """Test that the `canu report switch cabling` command errors on a bad IP."""
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
            get_lldp(bad_ip, credentials, True)

        assert "Failed to establish a new connection" in str(connection_error.value)


@responses.activate
def test_get_lldp_function_bad_credentials():
    """Test that the `canu report switch cabling` command errors on bad credentials."""
    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        bad_credentials = {"username": "foo", "password": "foo"}

        with pytest.raises(requests.exceptions.HTTPError) as http_error:
            get_lldp(ip, bad_credentials, True)
        assert "Unauthorized for url" in str(http_error.value)


@responses.activate
def test_switch_cabling():
    """Test that the `canu switch cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json={
                "hostname": "test-switch",
                "platform_name": "X86-64",
                "system_mac": "aa:aa:aa:aa:aa:aa",
            },
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json,
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
                "cabling",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "1/1/1   ==> sw-test01      1/1/1" in str(result.output)


def test_switch_cabling_missing_ip():
    """Test that the `canu switch cabling` command errors on missing IP address."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "cabling",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Missing option '--ip'" in str(result.output)


def test_switch_cabling_invalid_ip():
    """Test that the `canu switch cabling` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "cabling",
                "--ip",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_cabling_bad_ip():
    """Test that the `canu switch cabling` command errors on bad IP address."""
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
                "cabling",
                "--ip",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_cabling_bad_password():
    """Test that the `canu switch cabling` command errors on bad credentials."""
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
                "cabling",
                "--ip",
                ip,
                "--username",
                username,
                "--password",
                bad_password,
            ],
        )
        assert result.exit_code == 0
        assert "check the username or password" in str(result.output)


lldp_neighbors_json = {
    "1%2F1%2F1": {
        "aa:bb:cc:88:99:00,1/1/1": {
            "chassis_id": "aa:bb:cc:88:99:00",
            "mac_addr": "aa:bb:cc:88:99:01",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-test01",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        }
    },
    "1%2F1%2F2": {
        "aa:bb:cc:88:00:00,1/1/2": {
            "chassis_id": "aa:bb:cc:88:00:00",
            "mac_addr": "aa:bb:cc:88:00:01",
            "neighbor_info": {
                "chassis_description": "Test switch2 description",
                "chassis_name": "sw-test02",
                "port_description": "1/1/2",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/2",
        }
    },
    "1%2F1%2F3": {
        "00:00:00:00:00:00,00:00:00:00:00:00": {
            "chassis_id": "00:00:00:00:00:00",
            "mac_addr": "00:00:00:00:00:00",
            "neighbor_info": {
                "chassis_description": "",
                "chassis_name": "",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "00:00:00:00:00:00",
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
        "aa:aa:aa:aa:aa:aa,aa:aa:aa:aa:aa:aa": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:aa",
            "neighbor_info": {
                "chassis_description": "NCN description",
                "chassis_name": "ncn-test",
                "port_description": "mgmt1",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "aa:aa:aa:aa:aa:aa",
        }
    },
}

arp_neighbors_json = {
    "192.168.1.2,vlan1": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.1.2",
        "port": {"vlan1": "/rest/v10.04/system/interfaces/vlan1"},
    },
    "192.168.1.3,vlan2": {
        "mac": "11:11:11:11:11:11",
        "ip_address": "192.168.1.3",
        "port": {"vlan2": "/rest/v10.04/system/interfaces/vlan2"},
    },
}
