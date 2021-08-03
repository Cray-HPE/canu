"""Test CANU validate bgp commands."""
import click.testing
import requests
import responses

from canu.cli import cli


architecture = "tds"
shasta = "1.4"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
cache_minutes = 0
asn = 65533
runner = click.testing.CliRunner()


@responses.activate
def test_validate_bgp():
    """Test that the `canu validate bgp` command runs and returns PASS."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_full_architecture():
    """Test that the `canu validate bgp` command runs and returns PASS with full architecture."""
    full_architecture = "full"
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_file():
    """Test that the `canu validate bgp` command runs from a file input and returns PASS."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_verbose():
    """Test that the `canu validate bgp` command runs verbose and returns PASS."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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
    """Test that the `canu validate bgp` command errors on missing IPs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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
    """Test that the `canu validate bgp` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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
    """Test that the `canu validate bgp` command errors on invalid IPs."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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
    """Test that the `canu validate bgp` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_bad_ip():
    """Test that the `canu validate bgp` command errors on a bad IP."""
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_bad_ip_file():
    """Test that the `canu validate bgp` command errors on a bad IP from a file."""
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

        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_bad_password():
    """Test that the `canu validate bgp` command errors on bad credentials."""
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_fail():
    """Test that the `canu validate bgp` command reports that a switch failed bgp check."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_fail_verbose():
    """Test that the `canu validate bgp` command reports that a switch failed bgp check."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_not_spine():
    """Test that the `canu validate bgp` command reports SKIP on a switch not a spine."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_error_not_spine():
    """Test that the `canu validate bgp` command given an error on a switch not a spine."""
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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


@responses.activate
def test_validate_bgp_error_not_agg():
    """Test that the `canu validate bgp` command given an error on a switch not an agg or leaf."""
    full_architecture = "full"
    with runner.isolated_filesystem():
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
                "--shasta",
                shasta,
                "--cache",
                cache_minutes,
                "validate",
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
