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
"""Test SLS utilities Manager convenience classes."""
import ipaddress
from collections import UserDict

import pytest

from canu.utils.sls_utils.Managers import NetworkManager, SubnetManager
from canu.utils.sls_utils.Networks import Network, Subnet


@pytest.fixture
def network_dict():
    """Construct networks to pass SLS schema checks."""
    nmn = Network("NMN", "ethernet", "10.1.0.0/24")
    nmn.mtu(9000)
    hmn = Network("HMN", "ethernet", "10.2.0.0/24")
    hmn.mtu(9000)
    return {
        nmn.name(): nmn.to_sls(),
        hmn.name(): hmn.to_sls(),
    }


@pytest.fixture
def subnet_dict():
    """Construct subnets to pass SLS schema checks."""
    return {
        "subnet1": Subnet("subnet1", "10.1.0.0/25", "10.1.0.1", 1),
        "subnet2": Subnet("subnet2", "10.2.0.0/25", "10.2.0.1", 2),
    }


def test_networkmanager_init_from_sls_data(network_dict):
    """Test Network Manager creation from SLS JSON."""
    nm = NetworkManager(network_dict)
    assert isinstance(nm, UserDict)
    assert isinstance(nm.data["NMN"], Network)
    assert isinstance(nm.data["HMN"], Network)


def test_networkmanager_update_existing(network_dict):
    """Test adding a new network to existing NetworkManager."""
    can = Network("CAN", "ethernet", "10.3.0.0/24")
    can.mtu(9000)
    nm = NetworkManager(network_dict)
    nm.update({can.name(): can})
    assert isinstance(nm.data["CAN"], Network)
    assert nm.get("CAN").ipv4_network() == ipaddress.IPv4Network("10.3.0.0/24")


def test_networkmanager_get(network_dict):
    """Test retrieval of a Network by Name and IPv4 Address."""
    nm = NetworkManager(network_dict)
    assert nm.get("NMN") == nm.data["NMN"]
    assert nm.get("10.2.0.0/24") == nm.data["HMN"]


def test_networkmanager_to_sls(network_dict):
    """Test serializing a NetworkManager object to SLS JSON."""
    nm = NetworkManager(network_dict)
    sls = nm.to_sls()
    assert sls["NMN"] == nm.get("NMN").to_sls()
    assert sls["HMN"] == nm.get("HMN").to_sls()


def test_subnetmanager_init(subnet_dict):
    """Test creation of Subnet Manager."""
    sm = SubnetManager(subnet_dict)
    assert isinstance(sm, UserDict)
    assert isinstance(sm.data["subnet1"], Subnet)
    assert isinstance(sm.data["subnet2"], Subnet)


def test_subnetmanager_update_existing(subnet_dict):
    """Test adding a new subnet to existing NetworkManager."""
    subnet3 = Subnet("subnet3", "10.3.0.0/25", "10.3.0.1", 3)
    sm = SubnetManager(subnet_dict)
    sm.update({subnet3.name(): subnet3})
    assert isinstance(sm.data["subnet3"], Subnet)
    assert sm.get("subnet3").ipv4_network() == ipaddress.IPv4Network("10.3.0.0/25")


def test_subnetmanager_get(subnet_dict):
    """Test Subnet Manager retrieval by name and IPv4 Address."""
    sm = SubnetManager(subnet_dict)
    assert sm.get("subnet1") == sm.data["subnet1"]
    assert sm.get("10.1.0.0/25") == sm.data["subnet1"]


def test_subnetmanager_to_sls(subnet_dict):
    """Test serialization of a SubnetManager object to SLS JSON."""
    sm = SubnetManager(subnet_dict)
    sls = sm.to_sls()
    assert sls["subnet1"] == sm.get("subnet1").to_sls()
    assert sls["subnet2"] == sm.get("subnet2").to_sls()
