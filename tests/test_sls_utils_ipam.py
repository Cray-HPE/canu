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
"""Test SLS utilities ipam functions."""
from collections import defaultdict
import ipaddress

import pytest

from canu.utils.sls_utils.ipam import free_ipv4_subnets, next_free_ipv4_address
from canu.utils.sls_utils.Networks import Network, Subnet


def test_raises_value_error_if_input_not_network():
    """Test raising exception of a non-Network is passed."""
    with pytest.raises(ValueError):
        free_ipv4_subnets("not a network")


def test_returns_no_subnets_if_no_subnets_used():
    """Test that entire Network is available if no Subnets are used."""
    network = Network("test", "ethernet", "192.168.0.0/24")
    assert isinstance(network.subnets(), defaultdict)
    assert ipaddress.IPv4Network("192.168.0.0/24") in free_ipv4_subnets(network)


def test_finds_available_subnets():
    """Test that remaining available Subnets are reported."""
    network = Network("test", "ethernet", "192.168.0.0/24")
    subnets = {
        "subnet1": Subnet("subnet1", "192.168.0.0/27", "192.168.0.1", 1),
        "subnet2": Subnet("subnet2", "192.168.0.32/27", "192.168.0.33", 2),
        "subnet3": Subnet("subnet3", "192.168.0.64/27", "192.168.0.65", 3),
    }
    network.subnets(subnets)
    available_subnets = free_ipv4_subnets(network)
    expected_subnets = [
        ipaddress.IPv4Network("192.168.0.96/27"),
        ipaddress.IPv4Network("192.168.0.128/25"),
    ]
    assert available_subnets == expected_subnets


def test_returns_empty_list_if_no_available_subnets_found():
    """Test returning empty list if the entire Network has been used."""
    network = Network("test", "ethernet", "192.168.0.0/24")
    subnets = {
        "subnet1": Subnet("subnet1", "192.168.0.0/26", "192.168.0.1", 1),
        "subnet2": Subnet("subnet2", "192.168.0.64/26", "192.168.0.65", 2),
        "subnet3": Subnet("subnet3", "192.168.0.128/25", "192.168.0.129", 3),
    }
    network.subnets(subnets)
    assert not free_ipv4_subnets(network)


def test_raises_exception_if_subnets_overlap():
    """Test that an exception is raised if a Network's Subnets overlap."""
    network = Network("test", "ethernet", "192.168.0.0/24")
    subnets = {
        "subnet1": Subnet("subnet1", "192.168.0.0/25", "192.168.0.1", 1),
        "subnet2": Subnet("subnet2", "192.168.0.64/26", "192.168.0.65", 2),
        "subnet3": Subnet("subnet3", "192.168.0.128/25", "192.168.0.129", 3),
    }
    network.subnets(subnets)
    with pytest.raises(Exception) as e:
        free_ipv4_subnets(network)
    assert e.type == Exception


def test_next_free_ipv4_address():
    subnet = Subnet("test1", "192.168.0.0/24", "192.168.0.1", 1)
    next_free_ip = next_free_ipv4_address(subnet)
    assert next_free_ip == ipaddress.IPv4Address("192.168.0.2")


def test_requested_ipv4_address():
    # TODO: looks like this code is broken next_free_ipv4_address(subnet, requested_ipv4_address)
    assert True


def test_value_error():
    with pytest.raises(ValueError):
        next_free_ipv4_address('not a subnet')
