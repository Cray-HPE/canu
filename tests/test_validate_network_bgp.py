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
"""Test CANU validate network bgp commands."""
from unittest.mock import patch

from click import testing
import requests
import responses

from canu.cli import cli


username = "admin"
password = "admin"
ip = "192.168.1.1"
asn = 65533
sls_cache = {
    "HMN_IPs": {
        "sw-spine-001": "192.168.1.1",
        "sw-spine-002": "192.168.1.2",
    },
    "SWITCH_ASN": asn,
}
cache_minutes = 0

sls_address = "api-gw-service-nmn.local"
runner = testing.CliRunner()


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_aruba(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip in sls_cache["HMN_IPs"].items():
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
                f"https://{ip}/rest/v10.04/system/vrfs/Customer/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=all_established,
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "PASS - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "PASS - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_verbose(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip_address in sls_cache["HMN_IPs"].items():
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/login",
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=all_established,
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system/vrfs/Customer/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=all_established_cmn,
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "Switch: sw-spine-001 (192.168.1.1)      " in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.4: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.2: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.3: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.4: Established" in str(result.output)
    assert "Switch: sw-spine-002 (192.168.1.2)      " in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.4: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.2: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.3: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.4: Established" in str(result.output)
    assert "PASS - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "PASS - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_nmn(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip_address in sls_cache["HMN_IPs"].items():
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/login",
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=all_established,
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
            "--verbose",
            "--network",
            "nmn",
        ],
    )
    assert result.exit_code == 0
    assert "Switch: sw-spine-001 (192.168.1.1)      " in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.4: Established" in str(result.output)
    assert "Switch: sw-spine-002 (192.168.1.2)      " in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.4: Established" in str(result.output)
    assert "PASS - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "PASS - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_cmn(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip_address in sls_cache["HMN_IPs"].items():
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/login",
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system/vrfs/Customer/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=all_established_cmn,
            )
            responses.add(
                responses.GET,
                f"https://{ip_address}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip_address}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
            "--verbose",
            "--network",
            "cmn",
        ],
    )
    assert result.exit_code == 0
    assert "Switch: sw-spine-001 (192.168.1.1)      " in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.2: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.3: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.10.4: Established" in str(result.output)
    assert "Switch: sw-spine-002 (192.168.1.2)      " in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.2: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.3: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.10.4: Established" in str(result.output)
    assert "PASS - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "PASS - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_bad_password(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command errors on bad credentials."""
    bad_password = "foo"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                bad_password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.1, check the username or password"
            in str(result.output)
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_fail(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip in sls_cache["HMN_IPs"].items():
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
                f"https://{ip}/rest/v10.04/system/vrfs/Customer/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=one_idle,
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "FAIL - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "FAIL - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_fail_verbose(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        for name, ip in sls_cache["HMN_IPs"].items():
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
                f"https://{ip}/rest/v10.04/system/vrfs/Customer/bgp_routers/{asn}/bgp_neighbors?depth=2",
                json=one_idle,
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
                json={"hostname": name, "platform_name": "X86-64"},
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

    result = runner.invoke(
        cli,
        [
            "validate",
            "network",
            "bgp",
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "Switch: sw-spine-001 (192.168.1.1)      " in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-001 ===> 192.168.1.4: Idle" in str(result.output)
    assert "Switch: sw-spine-002 (192.168.1.2)      " in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.2: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.3: Established" in str(result.output)
    assert "sw-spine-002 ===> 192.168.1.4: Idle" in str(result.output)
    assert "FAIL - IP: 192.168.1.1 Hostname: sw-spine-001" in str(result.output)
    assert "FAIL - IP: 192.168.1.2 Hostname: sw-spine-002" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_vendor_error(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command errors on 'None' vendor."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = None
        pull_sls_networks.return_value = sls_cache
        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@patch("canu.validate.network.bgp.bgp.get_bgp_neighbors_aruba")
@responses.activate
def test_validate_bgp_exception(
    get_bgp_neighbors_aruba,
    pull_sls_networks,
    switch_vendor,
):
    """Test that the `canu validate network bgp` command errors on exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        pull_sls_networks.return_value = sls_cache
        get_bgp_neighbors_aruba.side_effect = requests.exceptions.HTTPError

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


# Mellanox
@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_mellanox(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command runs with Mellanox switch."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        pull_sls_networks.return_value = sls_cache
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "OK", "status_msg": "Successfully logged-in"},
        )
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json=bgp_status_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": [{"Hostname": "sw-spine-mellanox"}]},
        )
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": {"value": ["MSN2100"]}},
        )

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "PASS - IP: 192.168.1.1 Hostname: sw-spine-mellanox" in str(
            result.output,
        )


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_mellanox_connection_error(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch connection error."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        pull_sls_networks.return_value = sls_cache
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            status=404,
        )

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_mellanox_bad_login(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch bad login."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        pull_sls_networks.return_value = sls_cache
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "ERROR", "status_msg": "Invalid username or password"},
        )

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


@patch("canu.validate.network.bgp.bgp.switch_vendor")
@patch("canu.validate.network.bgp.bgp.pull_sls_networks")
@responses.activate
def test_validate_bgp_mellanox_exception(pull_sls_networks, switch_vendor):
    """Test that the `canu validate network bgp` command errors with Mellanox switch exception."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        pull_sls_networks.return_value = sls_cache
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "OK", "status_msg": "Successfully logged-in"},
        )
        responses.add(
            responses.POST,
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            body=requests.exceptions.HTTPError(),
        )

        result = runner.invoke(
            cli,
            [
                "validate",
                "network",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "192.168.1.1     - Connection Error" in str(result.output)


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

all_established_cmn = {
    "192.168.10.2": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.10.3": {
        "status": {"bgp_peer_state": "Established"},
    },
    "192.168.10.4": {
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
    },
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
                },
            ],
        },
    ],
}
