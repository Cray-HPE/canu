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
"""Test CANU config BGP."""
from collections import defaultdict
import json
from os import urandom
from unittest.mock import patch

from click import testing
import requests
import responses

from canu.cli import cli


username = "admin"
password = "admin"
fileout = "fileout.txt"
sls_address = "api-gw-service-nmn.local"
ip1 = "192.168.1.1"
ip2 = "192.168.1.2"
ips = "192.168.1.1,192.168.1.2"
ips_dell = "192.168.1.3,192.168.1.4"
ips_mellanox = "192.168.1.5,192.168.1.6"
cache_minutes = 0
asn = 65533
runner = testing.CliRunner()
token = "123abc"


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp(switch_vendor):
    """Test that the `canu config bgp` command runs."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        for ip in ips.split(","):
            # Login
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/login",
            )

            # Delete
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/prefix_lists/*",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/route_maps/*",
            )

            # Prefix Lists
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-can/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-hmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-nmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/tftp/prefix_list_entries",
            )

            # Route Maps
            # ncn_names are ['ncn-w001', 'ncn-w002', 'ncn-w003', 'ncn-w004', 'ncn-w005']
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w002/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w003/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w004/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w005/route_map_entries",
            )

            # Route Entry, multiple responses
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                    "50": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/50",
                },
            )

            # BGP Router ID
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers",
            )

            # BGP Neighbors
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
            )

            # Write Memory
            responses.add(
                responses.PUT,
                f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
            )

            # Logout
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
            ],
        )
        assert result.exit_code == 0
        assert "BGP Updated" in str(result.output)
        assert "192.168.1.1" in str(result.output)
        assert "192.168.1.2" in str(result.output)


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_file(switch_vendor):
    """Test that the `canu config bgp` command runs from SLS input."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        # format sls_networks to be like sls_file.json
        sls_json = defaultdict()
        for network in sls_networks:
            name = network["Name"]
            sls_json[name] = network
        sls_json = {"Networks": sls_json}

        with open("sls_file.json", "w") as f:
            f.write(json.dumps(sls_json))

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        for ip in ips.split(","):
            # Login
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/login",
            )

            # Delete
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/prefix_lists/*",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/route_maps/*",
            )

            # Prefix Lists
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-can/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-hmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-nmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/tftp/prefix_list_entries",
            )

            # Route Maps
            # ncn_names are ['ncn-w001', 'ncn-w002', 'ncn-w003', 'ncn-w004', 'ncn-w005']
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w002/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w003/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w004/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w005/route_map_entries",
            )

            # Route Entry, multiple responses
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                    "50": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/50",
                },
            )

            # BGP Router ID
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers",
            )

            # BGP Neighbors
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
            )

            # Write Memory
            responses.add(
                responses.PUT,
                f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
            )

            # Logout
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--sls-file",
                "sls_file.json",
            ],
        )
        assert result.exit_code == 0
        assert "BGP Updated" in str(result.output)
        assert "192.168.1.1" in str(result.output)
        assert "192.168.1.2" in str(result.output)


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_verbose(switch_vendor):
    """Test that the `canu config bgp` command runs with verbose output."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        for ip in ips.split(","):
            # Login
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/login",
            )

            # Delete
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/prefix_lists/*",
            )
            responses.add(
                responses.DELETE,
                f"https://{ip}/rest/v10.04/system/route_maps/*",
            )

            # Prefix Lists
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-can/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-hmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/pl-nmn/prefix_list_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/prefix_lists/tftp/prefix_list_entries",
            )

            # Route Maps
            # ncn_names are ['ncn-w001', 'ncn-w002', 'ncn-w003', 'ncn-w004', 'ncn-w005']
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w002/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w003/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w004/route_map_entries",
            )
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w005/route_map_entries",
            )

            # Route Entry, multiple responses
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                },
            )
            responses.add(
                responses.GET,
                f"https://{ip}/rest/v10.04/system/route_maps/ncn-w001/route_map_entries",
                json={
                    "10": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/10",
                    "20": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/20",
                    "30": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/30",
                    "40": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/40",
                    "50": "/rest/v10.04/system/route_maps/ncn-w001/route_map_entries/50",
                },
            )

            # BGP Router ID
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers",
            )

            # BGP Neighbors
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/system/vrfs/default/bgp_routers/{asn}/bgp_neighbors",
            )

            # Write Memory
            responses.add(
                responses.PUT,
                f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
            )

            # Logout
            responses.add(
                responses.POST,
                f"https://{ip}/rest/v10.04/logout",
            )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--verbose",
            ],
        )
        assert result.exit_code == 0
        assert "BGP Updated" in str(result.output)
        assert "192.168.1.1" in str(result.output)
        assert "192.168.1.2" in str(result.output)
        assert "CAN Prefix: 192.168.5.0/23" in str(result.output)
        assert "HMN Prefix: 192.168.6.0/24" in str(result.output)
        assert "NMN Prefix: 192.168.7.0/24" in str(result.output)
        assert "TFTP Prefix: 192.168.7.60/32" in str(result.output)


def test_config_bgp_missing_ips():
    """Test that the `canu config bgp` command errors on missing IPs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Missing one of the required mutually exclusive options from 'Network cabling IPv4 input sources' option group:"
            in str(result.output)
        )


def test_config_bgp_mutually_exclusive_ips_and_file():
    """Test that the `canu config bgp` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
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
            "Error: Mutually exclusive options from 'Network cabling IPv4 input sources' option group cannot be used"
            in str(result.output)
        )


def test_config_bgp_invalid_ip():
    """Test that the `canu config bgp` command errors on invalid IPs."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
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


def test_config_bgp_invalid_ip_file():
    """Test that the `canu config bgp` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
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


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_bad_ip(switch_vendor):
    """Test that the `canu config bgp` command errors on bad IPs."""
    bad_ip = "192.168.1.98"
    bad_ip2 = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )
        responses.add(
            responses.POST,
            f"https://{bad_ip2}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                f"{bad_ip},{bad_ip2}",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Error connecting to switch 192.168.1.98" in str(result.output)
        assert "Error connecting to switch 192.168.1.99" in str(result.output)


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_bad_ip_file(switch_vendor):
    """Test that the `canu config bgp` command errors on bad IPs from a file."""
    bad_ip = "192.168.1.98"
    bad_ip2 = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        with open("test.txt", "w") as f:
            f.write(bad_ip)
            f.write("\n")
            f.write(bad_ip2)
            f.write("\n")

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )
        responses.add(
            responses.POST,
            f"https://{bad_ip2}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Error connecting to switch 192.168.1.98" in str(result.output)
        assert "Error connecting to switch 192.168.1.99" in str(result.output)


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_bad_password(switch_vendor):
    """Test that the `canu config bgp` command errors on bad credentials."""
    bad_password = "foo"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        responses.add(
            responses.POST,
            f"https://{ip1}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        responses.add(
            responses.POST,
            f"https://{ip2}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                bad_password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting to switch 192.168.1.1, check the IP, username, or password"
            in str(result.output)
        )
        assert (
            "Error connecting to switch 192.168.1.2, check the IP, username, or password"
            in str(result.output)
        )


def test_config_bgp_too_many_ips():
    """Test that the `canu config bgp` command errors on too many IPs."""
    too_many_ips = "192.168.1.1,192.168.1.2,192.168.1.3"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                too_many_ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Incorrect number of IP addresses entered, there should be exactly 2 IPs."
            in str(result.output)
        )


def test_config_bgp_too_many_ips_file():
    """Test that the `canu config bgp` command errors on too many IPs from a file."""
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("192.168.1.1\n")
            f.write("192.168.1.2\n")
            f.write("192.168.1.3\n")

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Incorrect number of IP addresses entered, there should be exactly 2 IPs."
            in str(result.output)
        )


def test_config_bgp_not_enough_ips():
    """Test that the `canu config bgp` command errors on not enough IPs."""
    not_enough_ips = "192.168.1.1"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                not_enough_ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Incorrect number of IP addresses entered, there should be exactly 2 IPs."
            in str(result.output)
        )


def test_config_bgp_not_enough_ips_file():
    """Test that the `canu config bgp` command errors on not enough IPs from a file."""
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("192.168.1.1\n")

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Incorrect number of IP addresses entered, there should be exactly 2 IPs."
            in str(result.output)
        )


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_sls_token_bad(switch_vendor):
    """Test that the `canu config bgp` command errors on bad token file."""
    bad_token = "bad_token.token"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        with open(bad_token, "w") as f:
            f.write('{"access_token": "123"}')

        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            body=requests.exceptions.HTTPError(
                "503 Server Error: Service Unavailable for url",
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--auth-token",
                bad_token,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Error connecting SLS api-gw-service-nmn.local, check that the token is valid, or generate a new one"
            in str(result.output)
        )


@responses.activate
def test_config_bgp_sls_token_missing():
    """Test that the `canu config bgp` command errors on no token file."""
    bad_token = "no_token.token"

    result = runner.invoke(
        cli,
        [
            "--cache",
            cache_minutes,
            "config",
            "bgp",
            "--ips",
            ips,
            "--username",
            username,
            "--password",
            password,
            "--auth-token",
            bad_token,
        ],
    )
    assert result.exit_code == 0
    assert "Invalid token file, generate another token or try again." in str(
        result.output,
    )


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_sls_address_bad(switch_vendor):
    """Test that the `canu config bgp` command errors with bad SLS address."""
    switch_vendor.return_value = "aruba"
    bad_sls_address = "192.168.254.254"

    responses.add(
        responses.GET,
        f"https://{bad_sls_address}/apis/sls/v1/networks",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 51] Network is unreachable",
        ),
    )

    result = runner.invoke(
        cli,
        [
            "config",
            "bgp",
            "--username",
            username,
            "--password",
            password,
            "--ips",
            ips,
            "--sls-address",
            bad_sls_address,
        ],
    )
    assert result.exit_code == 0
    assert (
        "Error connecting to SLS 192.168.254.254, check the address or pass in a new address using --sls-address."
        in str(result.output)
    )


def test_config_bgp_sls_file_missing():
    """Test that the `canu config bgp` command errors on sls_file.json file missing."""
    bad_sls_folder = "/bad_folder"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--sls-file",
                bad_sls_folder,
            ],
        )
        assert result.exit_code == 2
        assert "No such file or directory" in str(result.output)


def test_config_bgp_sls_file_bad():
    """Test that the `canu config bgp` command errors on a bad sls_file.json."""
    bad_sls_file = "invalid_json_sls_file.json"
    with runner.isolated_filesystem():
        # Generate junk data in what should be a json file
        with open(bad_sls_file, "wb") as f:
            f.write(urandom(128))

        result = runner.invoke(
            cli,
            [
                "config",
                "bgp",
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--sls-file",
                bad_sls_file,
            ],
        )
        print(result.output)
        assert result.exit_code == 0
        assert "The file invalid_json_sls_file.json is not valid JSON." in str(
            result.output,
        )


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_no_vendor(switch_vendor):
    """Test that the `canu config bgp` command errors on unrecognized vendor."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = None
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                ips_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "Could not determine the vendor of the switch" in str(result.output)


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_dell(switch_vendor):
    """Test that the `canu config bgp` command warns about Dell."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                ips_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "BGP peering against Dell switch not allowed by CSM architecture."
            in str(result.output)
        )


@patch("canu.config.bgp.bgp.switch_vendor")
@responses.activate
def test_config_bgp_mellanox(switch_vendor):
    """Test that the `canu config bgp` command runs on Mellanox."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.GET,
            f"https://{sls_address}/apis/sls/v1/networks",
            json=sls_networks,
        )

        for ip in ips_mellanox.split(","):
            login_url = f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login"
            command_url = (
                login_url
                + "/admin/launch?script=rh&template=json-request&action=json-login"
            )
            # Login
            responses.add(
                responses.POST,
                login_url,
            )
            # Get Route Map
            responses.add(
                responses.POST,
                command_url,
                json=mellanox_route_map,
            )
            # posts NO route maps to the switch
            responses.add(
                responses.POST,
                command_url,
            )
            # delete prefix lists
            responses.add(
                responses.POST,
                command_url,
            )
            # post all the bgp configuration commands
            responses.add(
                responses.POST,
                command_url,
            )
            # write memory
            responses.add(
                responses.POST,
                command_url,
            )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "config",
                "bgp",
                "--ips",
                ips_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "BGP Updated\n"
            + "--------------------------------------------------\n"
            + "192.168.1.5\n"
            + "192.168.1.6\n"
        ) in str(result.output)


sls_networks = [
    {
        "Name": "NMNLB",
        "FullName": "Node Management Network LoadBalancers",
        "ExtraProperties": {
            "CIDR": "192.168.7.0/24",
            "Subnets": [
                {
                    "CIDR": "192.168.7.0/24",
                    "FullName": "NMN MetalLB",
                    "IPReservations": [
                        {"IPAddress": "192.168.7.60", "Name": "cray-tftp"},
                    ],
                },
            ],
        },
    },
    {
        "Name": "NMN",
        "FullName": "Node Management Network",
        "ExtraProperties": {
            "CIDR": "192.168.10.0/17",
            "Subnets": [
                {
                    "CIDR": "192.168.10.0/17",
                    "FullName": "NMN Bootstrap DHCP Subnet",
                    "IPReservations": [
                        {"IPAddress": "192.168.10.24", "Name": "ncn-w001"},
                        {"IPAddress": "192.168.10.25", "Name": "ncn-w002"},
                        {"IPAddress": "192.168.10.26", "Name": "ncn-w003"},
                        {"IPAddress": "192.168.10.27", "Name": "ncn-w004"},
                        {"IPAddress": "192.168.10.28", "Name": "ncn-w005"},
                    ],
                },
            ],
        },
    },
    {
        "Name": "CAN",
        "FullName": "Customer Access Network",
        "ExtraProperties": {
            "CIDR": "192.168.5.0/23",
            "Subnets": [
                {
                    "CIDR": "192.168.5.0/23",
                    "FullName": "CAN Bootstrap DHCP Subnet",
                    "IPReservations": [
                        {"IPAddress": "192.168.5.25", "Name": "ncn-w001"},
                        {"IPAddress": "192.168.5.26", "Name": "ncn-w002"},
                        {"IPAddress": "192.168.5.27", "Name": "ncn-w003"},
                        {"IPAddress": "192.168.5.28", "Name": "ncn-w004"},
                        {"IPAddress": "192.168.5.29", "Name": "ncn-w005"},
                    ],
                },
            ],
        },
    },
    {
        "Name": "HMNLB",
        "FullName": "Hardware Management Network LoadBalancers",
        "ExtraProperties": {
            "CIDR": "192.168.6.0/24",
            "Subnets": [
                {
                    "CIDR": "192.168.6.0/24",
                    "FullName": "HMN MetalLB",
                },
            ],
        },
    },
    {
        "Name": "HMN",
        "FullName": "Hardware Management Network",
        "ExtraProperties": {
            "CIDR": "192.168.20.0/17",
            "Subnets": [
                {
                    "CIDR": "192.168.20.0/17",
                    "FullName": "HMN Bootstrap DHCP Subnet",
                    "IPReservations": [
                        {"IPAddress": "192.168.20.44", "Name": "ncn-w001"},
                        {"IPAddress": "192.168.20.45", "Name": "ncn-w002"},
                        {"IPAddress": "192.168.20.46", "Name": "ncn-w003"},
                        {"IPAddress": "192.168.20.47", "Name": "ncn-w004"},
                        {"IPAddress": "192.168.20.48", "Name": "ncn-w005"},
                    ],
                },
            ],
        },
    },
]


mellanox_route_map = {
    "status": "OK",
    "executed_command": "show route-map",
    "status_message": "",
    "data": [
        {
            "route-map ncn-w001, permit, sequence 10": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-nmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.100.12"]}]},
            ],
        },
        {
            "route-map ncn-w001, permit, sequence 20": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-hmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.200.20"]}]},
            ],
        },
        {
            "route-map ncn-w001, permit, sequence 30": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-can"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.300.13"]}]},
            ],
        },
        {
            "route-map ncn-w002, permit, sequence 10": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-nmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.100.11"]}]},
            ],
        },
        {
            "route-map ncn-w002, permit, sequence 20": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-hmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.200.18"]}]},
            ],
        },
        {
            "route-map ncn-w002, permit, sequence 30": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-can"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.300.12"]}]},
            ],
        },
        {
            "route-map ncn-w003, permit, sequence 10": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-nmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.100.10"]}]},
            ],
        },
        {
            "route-map ncn-w003, permit, sequence 20": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-hmn"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.200.16"]}]},
            ],
        },
        {
            "route-map ncn-w003, permit, sequence 30": [
                {"Match clauses": [{"Lines": ["prefix ipv4 pl-can"]}]},
                {"Set clauses": [{"Lines": ["ip next-hop 192.168.300.11"]}]},
            ],
        },
    ],
}