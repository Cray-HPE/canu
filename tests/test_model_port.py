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
"""Test CANU network_model port class."""
from network_modeling.NetworkPort import NetworkPort


def test_port():
    """Test setting and resetting the port number."""
    p = NetworkPort(number=1)
    assert p.port() == 1
    p.port(2)
    assert p.port() == 2


def test_speed():
    """Test setting and resetting the port speed."""
    p = NetworkPort(speed=100)
    assert p.speed() == 100
    p.speed(1000)
    assert p.speed() == 1000


def test_slot():
    """Test setting and resetting the slot."""
    p = NetworkPort(slot=2)
    assert p.slot() == 2
    p.slot(3)
    assert p.slot() == 3


def test_destination_node_id():
    """Test setting the destination node ID."""
    p = NetworkPort()
    assert p.destination_node_id() is None
    p.destination_node_id("remote_node_id")
    assert p.destination_node_id() == "remote_node_id"


def test_destination_port():
    """Test setting the destination port."""
    p = NetworkPort()
    assert p.destination_port() is None
    p.destination_port(4)
    assert p.destination_port() == 4


def test_destination_slot():
    """Test setting the destination slot."""
    p = NetworkPort()
    assert p.destination_slot() is None
    p.destination_slot(5)
    assert p.destination_slot() == 5


def test_reset():
    """Test resetting an active port."""
    p = NetworkPort(number=1, slot=2, speed=100)
    p.reset()
    assert p.port() is None
    assert p.slot() is None
    assert p.speed() is None


def test_serialize():
    """Test serialization of a port attributes."""
    p = NetworkPort(number=1, slot=2, speed=100)
    serialized = p.serialize()
    assert serialized["port"] == 1
    assert serialized["slot"] == 2
    assert serialized["speed"] == 100
    assert serialized["destination_node_id"] is None
    assert serialized["destination_port"] is None
    assert serialized["destination_slot"] is None
