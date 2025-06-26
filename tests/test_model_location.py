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
"""Test CANU network_model location class."""
from network_modeling.NodeLocation import NodeLocation


def test_rack():
    """Test setting and resetting rack attributes."""
    node_location = NodeLocation(rack="x1001", elevation="u19")
    assert node_location.rack() == "x1001"
    node_location.rack("y2002")
    assert node_location.rack() == "y2002"


def test_elevation():
    """Test setting and resetting elevation attributes."""
    node_location = NodeLocation(rack="x1001", elevation="u19")
    assert node_location.elevation() == "u19"


def test_elevation_sublocation():
    """Test setting and resetting rack sublocation attributes."""
    node_location = NodeLocation(rack="x1001", elevation="u20L")
    assert node_location.elevation() == "u20"
    assert node_location.sub_location() == "L"


def test_parent():
    """Test setting and resetting location parent attribute."""
    node_location = NodeLocation(rack="x1001", elevation="u19")
    assert node_location.parent() is None
    node_location.parent("parent")
    assert node_location.parent() == "parent"


def test_serialize():
    """Test serialization of a location."""
    node_location = NodeLocation(rack="x1001", elevation="u19")
    expected_output = {"rack": "x1001", "elevation": "u19"}
    assert node_location.serialize() == expected_output

    # With sub_location and parent
    node_location.sub_location("R")
    node_location.parent("parent")
    expected_output = {
        "rack": "x1001",
        "elevation": "u19",
        "sub_location": "R",
        "parent": "parent",
    }
    assert node_location.serialize() == expected_output


def test_location_from_paddle():
    """Test creation of a location object from paddle JSON data."""
    paddle_location = {
        "rack": "x1001",
        "elevation": "u19",
        "sub_location": "L",
        "parent": "parent",
    }
    node_location = NodeLocation()
    node_location.location_from_paddle(paddle_location)
    assert node_location.rack() == "x1001"
    assert node_location.elevation() == "u19"
    assert node_location.sub_location() == "L"
    assert node_location.parent() == "parent"
