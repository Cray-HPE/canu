# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Test canu-inventory."""
import json
import os

import mock
import responses
from click import testing

import canu.inventory.ansible as ansible
from canu.inventory.ansible import ansible_inventory

sls_file = "./sls_input_file.json"
sls_address = "api-gw-service-nmn.local"
dumpstate_url = "https://{sls_address}/apis/sls/v1/dumpstate"
runner = testing.CliRunner()

# mock datasource switch_inventory
datasource = {
    "plugin": "DictInventory",
    "options": {
        "hosts": {
            "sw-spine-001": {
                "hostname": "127.1.2.3",
                "username": "admin",
                "password": "",
                "data": {"type": "spine"},
                "groups": ["aruba"],
            },
            "sw-spine-002": {
                "hostname": "127.4.5.6",
                "username": "admin",
                "password": "",
                "data": {"type": "spine"},
                "groups": ["aruba"],
            },
            "sw-leaf-bmc-001": {
                "hostname": "127.7.8.9",
                "username": "admin",
                "password": "",
                "data": {"type": "leaf-bmc"},
                "groups": ["aruba"],
            },
        },
        "groups": {
            "aruba": {
                "platform": "aruba_aoscx",
                "connection_options": {
                    "scrapli": {"extras": {"auth_strict_key": False}},
                },
            },
            "dell": {"platform": "dell_os10"},
            "mellanox": {"platform": "mellanox"},
        },
        "defaults": {},
    },
}

dumpstate = {
    "Hardware": {
        "x3000c0h12s1": {
            "Parent": "x3000c0h12",
            "Xname": "x3000c0h12s1",
            "Type": "comptype_hl_switch",
            "Class": "River",
            "TypeString": "MgmtHLSwitch",
            "LastUpdated": 1669049199,
            "LastUpdatedTime": "2022-11-21 16:46:39.615062 +0000 +0000",
            "ExtraProperties": {
                "Aliases": ["sw-spine-001"],
                "Brand": "Aruba",
                "IP4addr": "127.127.127.1",
            },
        },
        "x3000c0h13s1": {
            "Parent": "x3000c0h13",
            "Xname": "x3000c0h13s1",
            "Type": "comptype_hl_switch",
            "Class": "River",
            "TypeString": "MgmtHLSwitch",
            "LastUpdated": 1669049199,
            "LastUpdatedTime": "2022-11-21 16:46:39.615062 +0000 +0000",
            "ExtraProperties": {
                "Aliases": ["sw-spine-002"],
                "Brand": "Aruba",
                "IP4addr": "127.127.127.2",
            },
        },
    },
    "Networks": {
        "CMN": {
            "Name": "CMN",
            "FullName": "Customer Management Network",
            "IPRanges": ["127.1.0.0/16"],
            "Type": "ethernet",
            "LastUpdated": 1669049199,
            "LastUpdatedTime": "2022-11-21 16:46:39.675539 +0000 +0000",
            "ExtraProperties": {
                "CIDR": "127.1.0.0/16",
                "MTU": 9000,
                "MyASN": 65532,
                "PeerASN": 65533,
                "Subnets": [
                    {
                        "CIDR": "127.1.0.0/16",
                        "FullName": "CMN Management Network Infrastructure",
                        "Gateway": "127.1.1.1",
                        "IPReservations": [
                            {
                                "Comment": "x3000c0h12s1",
                                "IPAddress": "127.1.2.3",
                                "Name": "sw-spine-001",
                            },
                            {
                                "Comment": "x3000c0h13s1",
                                "IPAddress": "127.4.5.6",
                                "Name": "sw-spine-002",
                            },
                        ],
                        "Name": "network_hardware",
                        "VlanID": 7,
                    },
                ],
                "VlanRange": [7],
            },
        },
    },
}


def test_canu_inventory():
    """Run canu-inventory with no errors."""
    result = runner.invoke(ansible.ansible_inventory)
    assert result.exit_code == 0


@mock.patch("socket.gethostname")
def test_is_context_ncn_true(mock_get):
    """Test is_context_ncn with True."""
    mock_get.return_value = mock.Mock(ok=True)
    mock_get.return_value = "ncn-m001"
    assert ansible.is_context_ncn() is True


@mock.patch("socket.gethostname")
def test_is_context_ncn_false(mock_get):
    """Test is_context_ncn with False."""
    mock_get.return_value = mock.Mock(ok=True)
    mock_get.return_value = "bologna"
    assert ansible.is_context_ncn() is False


def test_get_switch_user(datasource=datasource, hostname="sw-spine-001"):
    """Test get_switch_user."""
    assert ansible.get_switch_user(datasource, hostname) == {"ansible_user": "admin"}


def test_get_switch_pass(datasource=datasource, hostname="sw-spine-001"):
    """Test get_switch_password."""
    assert ansible.get_switch_pass(datasource, hostname) == {"ansible_password": ""}


def test_get_switch_ip(datasource=datasource, hostname="sw-spine-001"):
    """Test get_switch_ip."""
    assert ansible.get_switch_ip(datasource, hostname) == {"ansible_host": "127.1.2.3"}


def test_get_groups(datasource=datasource, hostname="sw-spine-001"):
    """Test get_groups."""
    assert ansible.get_groups(datasource, hostname) == {"groups": ["aruba", "spine"]}


def test_get_aruba_vars(datasource=datasource, hostname="sw-spine-001"):
    """Test get_aruba_vars."""
    try:
        assert ansible.get_aruba_vars(datasource, hostname) == [
            {"ansible_network_os": "arubanetworks.aoscx.aoscx"},
            {"ansible_connection": "arubanetworks.aoscx.aoscx"},
            {"ansible_httpapi_use_ssl": True},
            {"ansible_httpapi_validate_certs": False},
            {"ansible_acx_no_proxy": False},
            {"ansible_aoscx_validate_certs": False},
            {"ansible_aoscx_use_proxy": False},
        ]
    except TypeError:
        raise AssertionError("get_aruba_vars() should return a list") from TypeError


def test_ansible_hostvars(datasource=datasource, hostname="sw-spine-001"):
    """Test ansible_hostvars."""
    assert ansible.ansible_hostvars(datasource, hostname) == {
        "ansible_host": "127.1.2.3",
        "ansible_user": "admin",
        "ansible_password": "",
        "groups": ["aruba", "spine"],
        "ansible_network_os": "arubanetworks.aoscx.aoscx",
        "ansible_connection": "arubanetworks.aoscx.aoscx",
        "ansible_httpapi_use_ssl": True,
        "ansible_httpapi_validate_certs": False,
        "ansible_acx_no_proxy": False,
        "ansible_aoscx_validate_certs": False,
        "ansible_aoscx_use_proxy": False,
    }


def mockenv(**envvars):
    """Allow more than one envvar to be mocked at once."""
    return mock.patch.dict(os.environ, envvars)


@mockenv(LANG="C.UTF-8", LC_ALL="C.UTF-8", SLS_API_GW=sls_address, SLS_TOKEN="test-token")
@responses.activate
def test_mock_api_dumpstate():
    """Run canu-inventory using the API."""
    # Mock the SLS dumpstate endpoint
    responses.add(
        responses.GET,
        f"https://{sls_address}/apis/sls/v1/dumpstate",
        json=dumpstate,
        status=200,
    )

    with runner.isolated_filesystem():
        result = runner.invoke(
            ansible_inventory,
            [
                "--host",
                "sw-spine-001",
            ],
        )

    assert "127.1.2.3" in result.stdout
    assert result.exit_code == 0


@mockenv(LANG="C.UTF-8", LC_ALL="C.UTF-8")
def test_mock_file_dumpstate():
    """Run canu-inventory using a local file."""
    with runner.isolated_filesystem():
        # Generate junk data in what should be a json file
        with open(sls_file, "w") as f:
            f.write(json.dumps(dumpstate))
        result = runner.invoke(
            ansible_inventory,
            [
                "--host",
                "sw-spine-002",
            ],
        )
        assert result.exit_code == 0
        assert "127.4.5.6" in result.output
