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
"""Test NetworkNode in the model."""
import pytest

from network_modeling.NetworkNode import NetworkNode, NetworkPort

hardware_a = {
    "name": "Node A",
    "vendor": "node_a_vendor",
    "type": "node_a_type",
    "model": "node_a_model",
    "ports": [
        {
            "count": 4,
            "speed": [100],
        },
    ],
}

architecture_a = {
    "name": "node_a",
    "model": "node_a_model",
    "connections": [
        {
            "name": "top_node",
            "speed": 100,
        },
        {
            "name": "node_b",
            "speed": 100,
        },
    ],
}

hardware_b = {
    "name": "Node B",
    "vendor": "node_b_vendor",
    "type": "node_b_type",
    "model": "node_b_model",
    "ports": [
        {
            "count": 4,
            "speed": [100],
        },
    ],
}
architecture_b = {
    "name": "node_b",
    "model": "node_b_model",
    "connections": [
        {
            "name": "top_node",
            "speed": 100,
        },
        {
            "name": "node_a",
            "speed": 100,
        },
    ],
}


def test_node_basics():
    """Test creation of a basic Node."""
    hardware = {
        "name": "Node A",
        "vendor": "node_a_vendor",
        "type": "node_a_type",
        "model": "node_a_model",
        "ports": [
            {
                "count": 48,
                "speed": [10, 1],
            },
            {
                "count": 4,
                "speed": [100, 40],
            },
            {
                "count": 1,
                "speed": [1],
                "slot": "mgmt",
            },
        ],
    }
    architecture = {
        "name": "node_a_architecture",
        "model": "node_a_model",
        "connections": [
            {
                "name": "top_node",
                "speed": 100,
            },
            {
                "name": "node_b",
                "speed": 100,
                "number": 3,
                "comment": "test connection",
            },
        ],
    }
    node = NetworkNode(id=1, hardware=hardware, architecture=architecture)
    assert node.arch_type() == "node_a_architecture"
    assert node.id() == 1
    assert node.common_name() is None
    # Initially all ports are unassigned so this is a list with all None
    assert not [n for n in node.ports() if n is not None]


def test_node_assign_port_bad_port():
    """Test that assign_port fails when a NetworkPort is not passed in."""
    node_a = NetworkNode(id=1, hardware=hardware_a, architecture=architecture_a)
    stub = NetworkNode(id=2, hardware=hardware_a, architecture=architecture_a)
    with pytest.raises(Exception) as e:
        node_a.assign_port(port="not_a_port", destination_node=stub)
    assert e.type == TypeError
    assert "Port needs to be type NetworkPort" in str(e)


def test_node_assign_port_bad_node():
    """Test that assign_port fails when a NetworkNode is not passed in."""
    node_a = NetworkNode(id=1, hardware=hardware_a, architecture=architecture_a)
    stub = NetworkPort()
    with pytest.raises(Exception) as e:
        node_a.assign_port(port=stub, destination_node="not_a_node")
    assert e.type == TypeError
    assert "Node needs to be type NetworkNode" in str(e)


def test_disconnect_bad_node():
    """Test that disconnect fails when a NetworkNode is not passed in."""
    node_a = NetworkNode(id=1, hardware=hardware_a, architecture=architecture_a)
    with pytest.raises(Exception) as e:
        node_a.disconnect(node="not_a_node")
    assert e.type == TypeError
    assert "Node needs to be type NetworkNode" in str(e)


def test_node_connection_basic():
    """Test connection of node A to Node B."""
    node_a = NetworkNode(id=1, hardware=hardware_a, architecture=architecture_a)
    node_b = NetworkNode(id=2, hardware=hardware_b, architecture=architecture_b)

    node_a.connect(node_b)
    # Edges are a list of connected nodes - a connects to b and vice versa.
    assert 2 in node_a.edges()
    assert 1 in node_b.edges()


def test_node_connection_hardware_speed_mismatch():
    """Test failed connection of node A to Node B when speed match is not available.

    Today this tests corner cases in __select_port_block which is tries to find
    available ports based on speed, slot and remaining port count.  These are not
    architectural constraints but physical hardware constraints.
    """
    hardware = {
        "name": "Node A",
        "vendor": "node_a_vendor",
        "type": "node_a_type",
        "model": "node_a_model",
        "ports": [
            {
                "count": 4,
                "speed": [100],
            },
        ],
    }

    # Reset port speed artifically to 13 for node A which has no match in node B.
    hardware["ports"][0]["speed"] = [13]
    node_a = NetworkNode(id=1, hardware=hardware, architecture=architecture_a)
    node_b = NetworkNode(id=2, hardware=hardware_b, architecture=architecture_b)

    with pytest.raises(Exception) as e:
        node_a.connect(node_b)
    assert e.type == Exception
    assert "does not have slot None with port None available at speed 100" in str(e)
    assert "Available slot:ports:[speeds] - None:4:[13]" in str(e)


def test_node_connection_hardware_slot_mismatch():
    """Test failed connection of node A to Node B when speed match is not available.

    Today this tests corner cases in __select_port_block which is tries to find
    available ports based on speed, slot and remaining port count.  These are not
    architectural constraints but physical hardware constraints.
    """
    hardware = {
        "name": "Node A",
        "vendor": "node_a_vendor",
        "type": "node_a_type",
        "model": "node_a_model",
        "ports": [
            {
                "count": 4,
                "speed": [100],
            },
        ],
    }

    # Set port slot artifically for node A which has no match in node B.
    hardware["ports"][0]["slot"] = "test_slot"
    node_a = NetworkNode(id=1, hardware=hardware, architecture=architecture_a)
    node_b = NetworkNode(id=2, hardware=hardware_b, architecture=architecture_b)

    with pytest.raises(Exception) as e:
        node_a.connect(node_b)
    assert e.type == Exception
    assert "does not have slot None with port None available at speed 100" in str(e)
    assert "Available slot:ports:[speeds] - test_slot:4:[100]" in str(e)


def test_node_connection_hardware_count_mismatch():
    """Test failed connection of node A to Node B when speed match is not available.

    Today this tests corner cases in __select_port_block which is tries to find
    available ports based on speed, slot and remaining port count.  These are not
    architectural constraints but physical hardware constraints.
    """
    hardware = {
        "name": "Node A",
        "vendor": "node_a_vendor",
        "type": "node_a_type",
        "model": "node_a_model",
        "ports": [
            {
                "count": 4,
                "speed": [100],
            },
        ],
    }

    # Set number of available ports artifically to 0 for node A so can't connect to node B.
    hardware["ports"][0]["count"] = 0
    node_a = NetworkNode(id=1, hardware=hardware, architecture=architecture_a)
    node_b = NetworkNode(id=2, hardware=hardware_b, architecture=architecture_b)

    with pytest.raises(Exception) as e:
        node_a.connect(node_b)
    assert e.type == Exception
    assert "does not have slot None with port None available at speed 100" in str(e)
    assert "Available slot:ports:[speeds] - None:0:[100]" in str(e)


def test_node_connection_architecture_speed_mismatch():
    """Test failed connection of node A to Node B when speed match is not available.

    Today this tests corner cases in connection_allowed which checks that the PoR
    architecture allows the requested connection, even if hardware-wise it's ok.
    """
    architecture_new_a = {
        "name": "node_a",
        "model": "node_a_model",
        "connections": [
            {
                "name": "top_node",
                "speed": 100,
            },
            {
                "name": "x",
                "speed": 100,
            },
        ],
    }

    architecture_new_b = {
        "name": "node_b",
        "model": "node_b_model",
        "connections": [
            {
                "name": "top_node",
                "speed": 100,
            },
            {
                "name": "y",
                "speed": 100,
            },
        ],
    }

    # Set set the allowed architectural speed artifically to 0 for node A so can't connect to node B.
    node_a = NetworkNode(id=1, hardware=hardware_a, architecture=architecture_new_a)
    node_b = NetworkNode(id=2, hardware=hardware_b, architecture=architecture_new_b)

    with pytest.raises(Exception) as e:
        # connect b to a since we've messed with the arch definition of a and will throw an error
        node_b.connect(node_a)
    assert e.type == Exception
    assert "architectural definition does not allow connections between None (node_a) and None (node_b)" in str(e)
