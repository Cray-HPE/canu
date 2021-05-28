"""Test CANU validate shcd commands."""

import click.testing
from openpyxl import Workbook
import requests
import responses

from canu.cli import cli


architecture = "tds"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
credentials = {"username": username, "password": password}
test_file = "test_file.xlsx"
tabs = "25G_10G"
corners = "I14,S30"
shasta = "1.4"
cache_minutes = 0
runner = click.testing.CliRunner()


@responses.activate
def test_validate_shcd_cabling():
    """Test that the `canu validate shcd cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        generate_test_file(test_file)
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "['sw-leaf-bmc-001', 'uan001', 'ncn-s003', 'ncn-w003']" in str(
            result.output
        )


@responses.activate
def test_validate_shcd_cabling_full_architecture():
    """Test that the `canu validate shcd cabling` command runs and returns valid cabling with full architecture."""
    full_architecture = "full"
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json2,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                full_architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert (
            "['sw-leaf-bmc-099', 'sw-leaf-bmc-001', 'uan001', 'ncn-s003', 'ncn-w003']"
            in str(result.output)
        )
        assert "sw-leaf-002 connects to 1 nodes" in str(result.output)
        assert "sw-leaf-001 connects to 6 nodes" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_file():
    """Test that the `canu validate shcd cabling` command runs and returns valid cabling with IPs from file."""
    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")

        generate_test_file(test_file)
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "['sw-leaf-bmc-001', 'uan001', 'ncn-s003', 'ncn-w003']" in str(
            result.output
        )


def test_validate_shcd_cabling_missing_ips():
    """Test that the `canu validate shcd cabling` command errors on missing IP address."""
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Missing one of the required mutually exclusive options from 'Network cabling IPv4 input sources' option group"
            in str(result.output)
        )


def test_validate_shcd_cabling_mutually_exclusive_ips_and_file():
    """Test that the `canu validate shcd cabling` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
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


def test_validate_shcd_cabling_invalid_ip():
    """Test that the `canu validate shcd cabling` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--ips': These items are not ipv4 addresses: ['999.999.999.999']"
            in str(result.output)
        )


def test_validate_shcd_cabling_invalid_ip_file():
    """Test that the `canu validate shcd cabling` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value:" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_bad_ip():
    """Test that the `canu validate shcd cabling` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))"
            ),
        )
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_bad_ip_file():
    """Test that the `canu validate shcd cabling` command errors on a bad IP from a file."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(bad_ip)

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))"
            ),
        )
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_bad_password():
    """Test that the `canu validate shcd cabling` command errors on bad credentials."""
    bad_password = "foo"

    with runner.isolated_filesystem():
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ip,
                "--username",
                username,
                "--password",
                bad_password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "check the username or password" in str(result.output)


def test_validate_shcd_cabling_missing_file():
    """Test that the `canu validate shcd cabling` command fails on missing file."""
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--shcd'." in str(result.output)


def test_validate_shcd_cabling_bad_file():
    """Test that the `canu validate shcd cabling` command fails on bad file."""
    bad_file = "does_not_exist.xlsx"
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                bad_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--shcd': Could not open file: does_not_exist.xlsx: No such file or directory"
            in str(result.output)
        )


def test_validate_shcd_cabling_missing_tabs():
    """Test that the `canu validate shcd cabling` command fails on missing tabs."""
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--tabs'." in str(result.output)


@responses.activate
def test_validate_shcd_cabling_bad_tab():
    """Test that the `canu validate shcd cabling` command fails on bad tab name."""
    bad_tab = "NMN"
    with runner.isolated_filesystem():
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                bad_tab,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 1
        assert "Tab NMN not found in test_file.xlsx" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_corner_prompt():
    """Test that the `canu validate shcd cabling` command prompts for corner input and runs."""
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
            ],
            input="I16\nS30",
        )
        assert result.exit_code == 0
        assert "['sw-leaf-bmc-001', 'uan001', 'ncn-s003', 'ncn-w003']" in str(
            result.output
        )


@responses.activate
def test_validate_shcd_cabling_corners_too_narrow():
    """Test that the `canu validate shcd cabling` command fails on too narrow area."""
    corners_too_narrow = "I16,R48"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_too_narrow,
            ],
        )
        assert result.exit_code == 1
        assert (
            "Ensure that the upper left corner (Labeled 'Source'), and the lower right corner of the table is entered."
            in str(result.output)
        )


@responses.activate
def test_validate_shcd_cabling_corners_too_high():
    """Test that the `canu validate shcd cabling` command fails on empty cells."""
    corners_too_high = "H16,S48"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_too_high,
            ],
        )
        assert result.exit_code == 1
        assert "Ensure the range entered does not contain a row of empty cells." in str(
            result.output
        )


@responses.activate
def test_validate_shcd_cabling_corners_bad_cell():
    """Test that the `canu validate shcd cabling` command fails on bad cell."""
    corners_bad_cell = "16,S48"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_bad_cell,
            ],
        )
        assert result.exit_code == 1
        assert "Bad range of cells entered for tab 25G_10G." in str(result.output)


@responses.activate
def test_validate_shcd_cabling_not_enough_corners():
    """Test that the `canu validate shcd cabling` command fails on not enough corners."""
    not_enough_corners = "H16"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                not_enough_corners,
            ],
        )
        assert result.exit_code == 0
        assert "There were 1 corners entered, but there should be 2." in str(
            result.output
        )


@responses.activate
def test_validate_shcd_cabling_bad_headers():
    """Test that the `canu validate shcd cabling` command fails on bad headers."""
    bad_header_tab = "Bad_Headers"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                bad_header_tab,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 1
        assert "On tab Bad_Headers, header column Slot not found" in str(result.output)


@responses.activate
def test_validate_shcd_cabling_bad_architectural_definition():
    """Test that the `canu validate shcd cabling` command fails with bad connections."""
    corners_bad_row = "I14,S31"
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners_bad_row,
            ],
        )
        assert result.exit_code == 1
        assert "No architectural definition found to allow connection between" in str(
            result.output
        )


@responses.activate
def test_validate_shcd_cabling_rename():
    """Test that the `canu validate shcd cabling` command runs and finds bad naming."""
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert "sw-leaf-bmc99 should be renamed sw-leaf-bmc-099" in str(result.output)
        assert "sw-spine01 should be renamed sw-spine-001" in str(result.output)


@responses.activate
def test_validate_shcd_missing_connections():
    """Test that the `canu validate shcd cabling` command runs and finds missing connections."""
    with runner.isolated_filesystem():
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
        generate_test_file(test_file)
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
                "shcd-cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--shcd",
                test_file,
                "--tabs",
                tabs,
                "--corners",
                corners,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Found in SHCD and on the network, but missing the following connections on the network"
            in str(result.output)
        )
        assert "['sw-leaf-bmc-001', 'uan001', 'ncn-s003', 'ncn-w003']" in str(
            result.output
        )
        assert "uan001          : Found in SHCD but not found on the network." in str(
            result.output
        )
        assert (
            "ncn-m88         : Found on the network but not found in the SHCD."
            in str(result.output)
        )


# Switch 1
switch_info1 = {
    "hostname": "sw-spine01",
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
                "chassis_name": "sw-spine02",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        }
    },
    "1%2F1%2F2": {
        "aa:bb:cc:88:00:00,1/1/2": {
            "chassis_id": "aa:bb:cc:88:00:00",
            "mac_addr": "aa:bb:cc:88:00:03",
            "neighbor_info": {
                "chassis_description": "Test switch2 description",
                "chassis_name": "sw-spine02",
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
                "chassis_name": "sw-leaf-bmc99",
                "port_description": "mgmt1",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "aa:aa:aa:aa:aa:aa",
        }
    },
    "1%2F1%2F5": {
        "99:99:99:99:99:99,1/1/5": {
            "chassis_id": "99:99:99:99:99:99",
            "mac_addr": "99:99:99:99:99:99",
            "neighbor_info": {
                "chassis_description": "ncn-m88",
                "chassis_name": "ncn-m88",
                "port_description": "1/1/5",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/5",
        }
    },
}

arp_neighbors_json1 = {
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
    "192.168.2.2,vlan3": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}

# Switch 2
switch_info2 = {
    "hostname": "sw-leaf02",
    "platform_name": "X86-64",
    "system_mac": "bb:bb:bb:bb:bb:bb",
}

lldp_neighbors_json2 = {
    "1%2F1%2F1": {
        "aa:aa:aa:aa:aa:aa,1/1/1": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:bb",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-leaf01",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        }
    }
}

arp_neighbors_json2 = {
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
    "192.168.2.2,vlan3": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}


def generate_test_file(file_name):
    """Generate xlsx sheet for testing."""
    wb = Workbook()
    test_file = file_name
    ws1 = wb.active
    ws1.title = "25G_10G"
    ws1["I14"] = "Source"
    ws1["J14"] = "Rack"
    ws1["K14"] = "Location"
    ws1["L14"] = "Slot"
    # None
    ws1["N14"] = "Port"
    ws1["O14"] = "Destination"
    ws1["P14"] = "Rack"
    ws1["Q14"] = "Location"
    # None
    ws1["S14"] = "Port"

    test_data = [
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j1",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j1",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j2",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j2",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j3",
            "junk",
            "x3000",
            "u13",
            "-",
            "j2",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j4",
            "sw-smn99",
            "x3000",
            "u13",
            "-",
            "j2",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j5",
            "junk",
            "x3000",
            "u13",
            "-",
            "j2",
        ],
        [
            "sw-smn01",
            "x3000",
            "U14",
            "",
            "-",
            "j49",
            "sw-25g01",
            "x3000",
            "u12",
            "-",
            "j48",
        ],
        [
            "sw-smn01",
            "x3000",
            "U14",
            "",
            "",
            "j50",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j48",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j47",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j47",
        ],
        [
            "uan01",
            "x3000",
            "u19",
            "ocp",
            "-",
            "j1",
            "sw-25g01",
            "x3000",
            "u12",
            "-",
            "j16",
        ],
        [
            "uan01",
            "x3000",
            "u19",
            "ocp",
            "-",
            "j2",
            "sw-25g02",
            "x3000",
            "u12",
            "-",
            "j17",
        ],
        [
            "uan01",
            "x3000",
            "u19",
            "s1",
            "-",
            "j1",
            "sw-25g01",
            "x3000",
            "u13",
            "-",
            "j16",
        ],
        [
            "uan01",
            "x3000",
            "u19",
            "s1",
            "-",
            "j2",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j17",
        ],
        [
            "sn03",
            "x3000",
            "u09",
            "ocp",
            "-",
            "j1",
            "sw-25g01",
            "x3000",
            "u12",
            "-",
            "j15",
        ],
        [
            "wn03",
            "x3000",
            "u06",
            "ocp",
            "-",
            "j1",
            "sw-25g01",
            "x3000",
            "u12",
            "-",
            "j9",
        ],
        [
            "wn03",
            "x3000",
            "u06",
            "ocp",
            "-",
            "j2	",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j9",
        ],
        [
            "CAN switch",
            "cfcanb4s1",
            "",
            "",
            "-",
            "9",
            "sw-25g01",
            "x3000",
            "u12",
            "-",
            "j36",
        ],
        # BAD ROW, do not include in normal run
        [
            "mn99",
            "x3000",
            "u12",
            "",
            "-",
            "j1",
            "mn98",
            "x3000",
            "u13",
            "-",
            "j1",
        ],
    ]
    for row in range(0, 17):
        for col in range(0, 11):
            ws1.cell(column=col + 9, row=row + 15, value=f"{test_data[row][col]}")

    # Tab 2 "Bad_Headers"
    ws2 = wb.create_sheet(title="Bad_Headers")
    ws2["I14"] = "Source"
    ws2["J14"] = "Rack"
    ws2["K14"] = "Location"
    # ws2["L14"] = "Slot" # Missing Header
    # None
    ws2["M14"] = "Port"
    ws2["N14"] = "Destination"
    ws2["O14"] = "Rack"
    ws2["P14"] = "Location"
    # None
    ws2["R14"] = "Port"

    # Tab 3 "More_connections" containing bad connections
    ws3 = wb.create_sheet(title="More_connections")
    ws3["I14"] = "Source"
    ws3["J14"] = "Rack"
    ws3["K14"] = "Location"
    ws3["L14"] = "Slot"
    # None
    ws3["N14"] = "Port"
    ws3["O14"] = "Destination"
    ws3["P14"] = "Rack"
    ws3["Q14"] = "Location"
    # None
    ws3["S14"] = "Port"

    test_data3 = [
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j51",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j51",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "sw-25g01",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j51",
        ],
        [
            "sw-cdu01",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-smn99",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "mn-99",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-25g01",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "mn-99",
            "x3000",
            "u12",
            "",
            "-",
            "j50",
            "sw-25g02",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "mn-99",
            "x3000",
            "u12",
            "",
            "-",
            "j51",
            "sw-smn98",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "mn-99",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-smn99",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
        [
            "sw-100g01",
            "x3000",
            "u12",
            "",
            "-",
            "j52",
            "sw-smn99",
            "x3000",
            "u13",
            "-",
            "j52",
        ],
    ]
    for row in range(0, 9):
        for col in range(0, 11):
            ws3.cell(column=col + 9, row=row + 15, value=f"{test_data3[row][col]}")

    wb.save(filename=test_file)
