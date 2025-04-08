# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
"""Test SLS utilities Network class."""
from collections import defaultdict
import ipaddress

import pytest

from canu.utils.sls_utils.Networks import BicanNetwork, Network, Subnet
from canu.utils.sls_utils.Reservations import Reservation


@pytest.fixture
def network_data():
    """Create default SLS JSON Network data."""
    return {
        "Name": "TestNetwork",
        "FullName": "Test Network",
        "Type": "ethernet",
        "CIDR": "10.0.0.0/24",
        "IPRanges": ["10.0.0.0/24"],
        "MTU": 1500,
        "Subnets": [],
        "MyASN": 65000,
        "PeerASN": 65001,
    }


@pytest.fixture
def network(network_data):
    """Create default SLS Network."""
    return Network.network_from_sls_data(network_data)


@pytest.fixture
def subnet_data():
    """Create default SLS JSON Subnet data."""
    return {
        "Name": "TestSubnet",
        "CIDR": "10.0.0.0/24",
        "Gateway": "10.0.0.1",
        "VlanID": 1,
        "FullName": "Test Subnet",
        "DHCPStart": "10.0.0.2",
        "DHCPEnd": "10.0.0.254",
        "ReservationStart": "10.0.0.3",
        "ReservationEnd": "10.0.0.253",
        "MetalLBPoolName": "test-pool",
        "IPReservations": [
            {
                "Name": "test-reservation",
                "IPAddress": "10.0.0.4",
                "Aliases": ["alias1", "alias2"],
                "Comment": "Test reservation",
            },
        ],
    }


@pytest.fixture
def subnet():
    """Create default SLS Subnet."""
    return Subnet("TestSubnet", "10.0.0.0/24", "10.0.0.1", 1)


def test_network_init(network_data):
    """Test initializing a new Network."""
    network = Network(
        name=network_data["Name"],
        network_type=network_data["Type"],
        ipv4_address=network_data["CIDR"],
    )
    assert network.name == network_data["Name"]
    assert network.full_name == ""
    assert network.ipv4_address == ipaddress.IPv4Interface(network_data["CIDR"])
    assert network.type == network_data["Type"]
    assert network.mtu is None
    assert network.subnets == defaultdict()
    assert network.bgp == (None, None)


def test_network_from_sls_data(network_data, network):
    """Test initializing a new Network from SLS JSON."""
    assert network.name == network_data["Name"]
    assert network.full_name == network_data["FullName"]
    assert network.ipv4_address == ipaddress.IPv4Interface(network_data["CIDR"])
    assert network.type == network_data["Type"]
    assert network.mtu == network_data["MTU"]
    assert network.subnets == defaultdict()
    assert network.bgp == (network_data["MyASN"], network_data["PeerASN"])


def test_network_name(network_data, network):
    """Test resetting name."""
    assert network.name == network_data["Name"]
    network.name = "NewTestNetwork"
    assert network.name == "NewTestNetwork"


def test_network_full_name(network_data, network):
    """Test resetting full name."""
    assert network.full_name == network_data["FullName"]
    network.full_name = "New Test Network"
    assert network.full_name == "New Test Network"


def test_network_ipv4_address(network_data, network):
    """Test resetting IPv4 address."""
    assert network.ipv4_address == ipaddress.IPv4Interface(network_data["CIDR"])
    network.ipv4_address = "10.1.0.0/24"
    assert network.ipv4_address == ipaddress.IPv4Interface("10.1.0.0/24")
    assert network.ipv4_network == ipaddress.IPv4Network("10.1.0.0/24")


def test_network_mtu(network_data, network):
    """Test resetting MTU."""
    assert network.mtu == network_data["MTU"]
    network.mtu = 9000
    assert network.mtu == 9000


def test_network_type(network_data, network):
    """Test resetting type."""
    assert network.type == network_data["Type"]
    network.type = "test_type"
    assert network.type == "test_type"


def test_network_subnets(network):
    """Test resetting subnets."""
    assert network.subnets == defaultdict()
    subnet = Subnet("test_subnet", "192.168.0.0/25", "192.168.0.1", 13)
    network.subnets = [subnet]
    assert subnet in network.subnets


def test_network_bgp(network_data, network):
    """Test resetting bgp."""
    assert network.bgp == (network_data["MyASN"], network_data["PeerASN"])
    network.bgp = (65002, 65003)
    assert network.bgp == (65002, 65003)


def test_network_to_sls(network):
    """Test serializing Network to SLS JSON."""
    expected_sls = {
        "Name": "TestNetwork",
        "FullName": "Test Network",
        "Type": "ethernet",
        "IPRanges": ["10.0.0.0/24"],
        "ExtraProperties": {
            "CIDR": "10.0.0.0/24",
            "MTU": 1500,
            "VlanRange": [],
            "Subnets": [],
            "MyASN": 65000,
            "PeerASN": 65001,
        },
    }
    assert network.to_sls() == expected_sls


def test_bican_network_init():
    """Test creating default BiCAN network."""
    bican = BicanNetwork()
    assert bican.name == "BICAN"
    assert bican.full_name == "System Default Route Network Name for Bifurcated CAN"
    assert bican.type == "ethernet"
    assert bican.ipv4_address == ipaddress.IPv4Interface("0.0.0.0/0")
    assert bican.mtu == 9000
    bican_sls = bican.to_sls()
    assert bican_sls["ExtraProperties"]["SystemDefaultRoute"] == "CMN"
    assert bican.default_route_network == "CMN"


def test_subnet_init(subnet_data):
    """Test creating basic Subnet."""
    subnet = Subnet(
        subnet_data["Name"],
        subnet_data["CIDR"],
        ipaddress.IPv4Address(subnet_data["Gateway"]),
        subnet_data["VlanID"],
    )
    assert subnet.name == subnet_data["Name"]
    assert subnet.ipv4_address == ipaddress.IPv4Interface(subnet_data["CIDR"])
    assert subnet.ipv4_gateway == ipaddress.IPv4Address(subnet_data["Gateway"])
    assert subnet.vlan == subnet_data["VlanID"]
    assert subnet.full_name == ""
    assert subnet.dhcp_start_address is None
    assert subnet.dhcp_end_address is None
    assert subnet.reservation_start_address is None
    assert subnet.reservation_end_address is None
    assert subnet.metallb_pool_name is None
    assert subnet.reservations == {}


def test_subnet_from_sls_data(subnet_data):
    """Test creating Subnet from SLS JSON."""
    subnet = Subnet.subnet_from_sls_data(subnet_data)
    assert subnet.name == subnet_data["Name"]
    assert subnet.ipv4_address == ipaddress.IPv4Interface(subnet_data["CIDR"])
    assert subnet.ipv4_gateway == ipaddress.IPv4Address(subnet_data["Gateway"])
    assert subnet.vlan == subnet_data["VlanID"]
    assert subnet.full_name == subnet_data["FullName"]
    assert subnet.dhcp_start_address == ipaddress.IPv4Address(subnet_data["DHCPStart"])
    assert subnet.dhcp_end_address == ipaddress.IPv4Address(subnet_data["DHCPEnd"])
    assert subnet.reservation_start_address == ipaddress.IPv4Address(subnet_data["ReservationStart"])
    assert subnet.reservation_end_address == ipaddress.IPv4Address(subnet_data["ReservationEnd"])
    assert subnet.metallb_pool_name == subnet_data["MetalLBPoolName"]
    assert len(subnet.reservations) == 1
    assert list(subnet.reservations.keys())[0] == subnet_data["IPReservations"][0]["Name"]
    assert isinstance(list(subnet.reservations.values())[0], Reservation)


def test_subnet_vlan(subnet):
    """Test resetting Subnet VLAN."""
    assert subnet.vlan == 1
    subnet.vlan = 2
    assert subnet.vlan == 2


def test_subnet_ipv4_gateway(subnet):
    """Test resetting Subnet gateway."""
    assert subnet.ipv4_gateway == ipaddress.IPv4Address('10.0.0.1')
    subnet.ipv4_gateway = "10.0.0.2"
    assert subnet.ipv4_gateway == ipaddress.IPv4Address('10.0.0.2')


def test_subnet_dhcp_start_address(subnet):
    """Test resetting Subnet dhcp start address."""
    assert subnet.dhcp_start_address is None
    subnet.dhcp_start_address = "10.0.0.3"
    assert subnet.dhcp_start_address == ipaddress.IPv4Address("10.0.0.3")


def test_subnet_dhcp_end_address(subnet):
    """Test resetting Subnet dhcp end address."""
    assert subnet.dhcp_end_address is None
    subnet.dhcp_end_address = "10.0.0.4"
    assert subnet.dhcp_end_address == ipaddress.IPv4Address("10.0.0.4")


def test_subnet_reservation_start_address(subnet):
    """Test resetting Subnet reservation start address."""
    assert subnet.reservation_start_address is None
    subnet.reservation_start_address = "10.0.0.5"
    assert subnet.reservation_start_address == ipaddress.IPv4Address("10.0.0.5")


def test_subnet_reservation_end_address(subnet):
    """Test resetting Subnet reservation end address."""
    assert subnet.reservation_end_address is None
    subnet.reservation_end_address = "10.0.0.6"
    assert subnet.reservation_end_address == ipaddress.IPv4Address("10.0.0.6")


def test_subnet_metallb_pool_name(subnet):
    """Test resetting Subnet metallb pool name."""
    assert subnet.metallb_pool_name is None
    subnet.metallb_pool_name = "TestPool"
    assert subnet.metallb_pool_name == "TestPool"


def test_subnet_reservations(subnet):
    """Test adding reservations to Subnet."""
    assert subnet.reservations == {}
    subnet.reservations = [{"IP": "10.0.0.7"}]
    assert subnet.reservations == [{"IP": "10.0.0.7"}]


def test_subnet_to_sls(subnet):
    """Test creating a subnet from SLS JSON data."""
    expected_sls = {
        "Name": "TestSubnet",
        "FullName": "",
        "CIDR": "10.0.0.0/24",
        "Gateway": "10.0.0.1",
        "VlanID": 1,
    }
    assert subnet.to_sls() == expected_sls
