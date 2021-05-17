"""Test CANU config BGP."""

import click.testing
import requests
import responses

from canu.cli import cli


shasta = "1.4"
username = "admin"
password = "admin"
fileout = "fileout.txt"
sls_address = "api-gw-service-nmn.local"
ip1 = "192.168.1.1"
ip2 = "192.168.1.2"
ips = "192.168.1.1,192.168.1.2"
cache_minutes = 0
asn = 65533
runner = click.testing.CliRunner()
token = "123abc"


@responses.activate
def test_config_bgp():
    """Test that the `canu config bgp` command runs."""
    with runner.isolated_filesystem():
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
            # ncn_names = ['ncn-w001', 'ncn-w002', 'ncn-w003', 'ncn-w004', 'ncn-w005']
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
                "--shasta",
                shasta,
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


def test_config_bgp_missing_ips():
    """Test that the `canu config bgp` command errors on missing IPs."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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


def test_config_bgp_too_many_ips():
    """Test that the `canu config bgp` command errors on too many IPs."""
    too_many_ips = "192.168.1.1,192.168.1.2,192.168.1.3"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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
                "--shasta",
                shasta,
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


@responses.activate
def test_config_bgp_sls_address_bad():
    """Error canu init SLS with bad SLS address."""
    bad_sls_address = "192.168.254.254"

    responses.add(
        responses.GET,
        f"https://{bad_sls_address}/apis/sls/v1/networks",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 51] Network is unreachable"
        ),
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
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
    print(result.output)
    assert result.exit_code == 0
    assert (
        "Error connecting to SLS 192.168.254.254, check the address or pass in a new address using --sls-address."
        in str(result.output)
    )


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
                }
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
                }
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
                }
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
                }
            ],
        },
    },
]
