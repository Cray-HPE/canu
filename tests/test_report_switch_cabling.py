"""Test CANU report switch cabling commands."""
from unittest.mock import patch

import click.testing
from netmiko import ssh_exception
import pytest
import requests
import responses

from canu.cache import remove_switch_from_cache
from canu.cli import cli
from canu.report.switch.cabling.cabling import get_lldp


username = "admin"
password = "admin"
ip = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
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


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_get_lldp_function(switch_vendor):
    """Test the `get_lldp` function returns valid switch information."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_get_lldp_function_bad_ip(switch_vendor):
    """Test that the `canu report switch cabling` command errors on a bad IP."""
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

        with pytest.raises(requests.exceptions.ConnectionError) as connection_error:
            get_lldp(bad_ip, credentials, True)

        assert "Failed to establish a new connection" in str(connection_error.value)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_get_lldp_function_bad_credentials(switch_vendor):
    """Test that the `canu report switch cabling` command errors on bad credentials."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        bad_credentials = {"username": "foo", "password": "foo"}

        with pytest.raises(requests.exceptions.HTTPError) as http_error:
            get_lldp(ip, bad_credentials, True)
        assert "Unauthorized for url" in str(http_error.value)
    remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling(switch_vendor):
    """Test that the `canu switch cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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
        remove_switch_from_cache(ip)


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


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_bad_ip(switch_vendor):
    """Test that the `canu switch cabling` command errors on bad IP address."""
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


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_bad_password(switch_vendor):
    """Test that the `canu switch cabling` command errors on bad credentials."""
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


# Dell
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
def test_switch_cabling_dell(netmiko_commands, switch_vendor):
    """Test that the `canu switch cabling` command runs and returns valid Dell cabling."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.return_value = netmiko_commands_dell

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "cabling",
                "--ip",
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
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
def test_switch_cabling_dell_timeout(netmiko_commands, switch_vendor):
    """Test that the `canu switch cabling` command errors on ssh timeout."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.side_effect = ssh_exception.NetmikoTimeoutException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "cabling",
                "--ip",
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
def test_switch_cabling_dell_auth(netmiko_commands, switch_vendor):
    """Test that the `canu switch cabling` command errors on ssh auth."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.side_effect = ssh_exception.NetmikoAuthenticationException

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "cabling",
                "--ip",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Authentication error connecting to switch 192.168.1.2, check the credentials or IP address and try again."
            in str(result.output)
        )


# Mellanox
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox(switch_vendor):
    """Test that the `canu switch cabling` command runs and returns valid Mellanox cabling."""
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
                "switch",
                "cabling",
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
            "1/1/1   ==> sw-test03      1/1/11             sw-test03                                             Test Switch 3\n"
            "1/1/2   ==> sw-test04      1/1/12             sw-test04                                             Test Switch 4\n"
        ) in str(result.output)
        remove_switch_from_cache(ip_mellanox)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox_no_neighbors(switch_vendor):
    """Test that the `canu switch cabling` command runs and returns valid Mellanox cabling."""
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
            json={
                "status": "OK",
                "executed_command": "show lldp interfaces ethernet remote",
                "status_message": "",
                "data": [{"Lines": ["", "No lldp remote information.", ""]}],
            },
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
                "switch",
                "cabling",
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
            "Switch: sw-test03 (192.168.1.3)                       \n"
            "Mellanox MSN2100\n"
            "---------------------------------------------------------------------------------------------------------------"
            "---------------------------------------\n"
            "PORT        NEIGHBOR       NEIGHBOR PORT      PORT DESCRIPTION                                      DESCRIPTION\n"
            "---------------------------------------------------------------------------------------------------------------"
            "---------------------------------------\n"
            "\n"
            "\n"
        ) in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox_auth_error(switch_vendor):
    """Test that the `canu switch cabling` command errors on authentication error."""
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
                "switch",
                "cabling",
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
            "Error connecting to switch 192.168.1.3, check the username or password."
            in str(result.output)
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox_connection_error(switch_vendor):
    """Test that the `canu switch cabling` command errors on connection error."""
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
                "switch",
                "cabling",
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
            "Error connecting to switch 192.168.1.3, check the IP address and try again."
            in str(result.output)
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox_exception(switch_vendor):
    """Test that the `canu switch cabling` command errors on switch exception after login."""
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
                "switch",
                "cabling",
                "--ip",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "HTTPError  while connecting to 192.168.1.3." in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
def test_switch_cabling_vendor_error(switch_vendor):
    """Test that the `canu switch cabling` command errors."""
    with runner.isolated_filesystem():
        switch_vendor.side_effect = requests.exceptions.HTTPError

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
        assert "Error connecting to switch 192.168.1.1, HTTPError ." in str(
            result.output
        )


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

netmiko_commands_dell = [
    "",
    " \n"
    + "Remote Chassis ID: aa:bb:cc:dd:ee:ff\n"
    + "Remote Port ID: Eth1/15\n"
    + "Remote Port Description: sw-test01\n"
    + "Local Port ID: ethernet1/1/1\n"
    + "Remote System Name: sw-test01\n"
    + "Remote System Desc: Test Switch 1\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Chassis ID: 11:22:33:44:55:66\n"
    + "Remote Port ID: ethernet1/1/15\n"
    + "Remote Port Description: sw-test02\n"
    + "Local Port ID: ethernet1/1/2\n"
    + "Remote System Name: sw-test02\n"
    + "Remote System Desc: Test Switch 2\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Chassis ID: Not Advertised\n"
    + "Remote Port ID: Not Advertised\n"
    + "Remote Port Description: Not Advertised\n"
    + "Local Port ID: mgmt1/1/3\n"
    + "Remote System Name: Not Advertised\n"
    + "Remote System Desc: Not Advertised\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Port ID: Not Advertised\n"
    + "Local Port ID: ethernet1/1/4\n"
    + "--------------------------------------------------------------------------- \n",
    "OS Version: 10.5.1.4\nSystem Type: S3048-ON\n",
    "sw-test-dell",
    "Address        Hardware address    Interface                     Egress Interface    \n"
    + "------------------------------------------------------------------------------------------\n"
    + "192.168.1.1    aa:bb:cc:dd:ee:ff   vlan2                         port-channel100     \n"
    + "192.168.1.2    11:22:33:44:55:66   vlan7                         port-channel100     \n",
]

lldp_json_mellanox = {
    "status": "OK",
    "executed_command": "show lldp interfaces ethernet remote",
    "status_message": "",
    "data": [
        {
            "Eth1/1 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "aa:bb:cc:dd:ee:ff",
                    "Remote system description": "Test Switch 3",
                    "Remote port-id": "Eth1/11",
                    "Remote port description": "sw-test03",
                    "Remote system name": "sw-test03",
                },
            ]
        },
        {
            "Eth1/2 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "11:22:33:44:55:66",
                    "Remote system description": "Test Switch 4",
                    "Remote port-id": "ethernet1/1/12",
                    "Remote port description": "sw-test04",
                    "Remote system name": "sw-test04",
                },
            ]
        },
        {
            "Eth1/3 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "Not Advertised",
                    "Remote system description": "Not Advertised",
                    "Remote port-id": "Not Advertised",
                    "Remote port description": "Not Advertised",
                    "Remote system name": "Not Advertised",
                },
            ]
        },
        {
            "Eth1/4 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote port-id": "Not Advertised",
                },
            ]
        },
    ],
}

arp_neighbors_mellanox = {
    "status": "OK",
    "executed_command": 'show ip arp | exclude "Total number of entries"',
    "status_message": "",
    "data": [
        {"Flags": [{"G": "EVPN Default GW"}]},
        {
            "VRF Name default": [
                {
                    "192.168.1.9": [
                        {"Hardware Address": "aa:bb:cc:dd:ee:ff", "Interface": "vlan 7"}
                    ],
                    "192.168.1.10": [
                        {"Hardware Address": "11:22:33:44:55:66", "Interface": "vlan 4"}
                    ],
                }
            ]
        },
    ],
}
