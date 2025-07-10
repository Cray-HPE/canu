# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Test SLS utilities Reservation class."""
import pytest

from canu.utils.sls_utils.Reservations import Reservation


@pytest.fixture
def reservation():
    """Create default Reservation."""
    return Reservation("test", "192.168.1.1", [])


def test_name(reservation):
    """Test resetting name."""
    assert reservation.name() == "test"
    reservation.name("new_test")
    assert reservation.name() == "new_test"


def test_ipv4_address(reservation):
    """Test resetting IPv4 address."""
    assert str(reservation.ipv4_address()) == "192.168.1.1"
    reservation.ipv4_address("192.168.1.2")
    assert str(reservation.ipv4_address()) == "192.168.1.2"


def test_comment(reservation):
    """Test resetting comment."""
    assert reservation.comment() == ""
    reservation.comment("test comment")
    assert reservation.comment() == "test comment"


def test_aliases(reservation):
    """Test setting aliases."""
    assert reservation.aliases() == []
    reservation.aliases(["alias1", "alias2"])
    assert reservation.aliases() == ["alias1", "alias2"]


def test_to_sls(reservation):
    """Test serializing to SLS JSON."""
    expected_sls = {
        "Name": "test",
        "IPAddress": "192.168.1.1",
    }
    assert reservation.to_sls() == expected_sls

    reservation.comment("test comment")
    reservation.aliases(["alias1", "alias2"])

    expected_sls.update(
        {
            "Comment": "test comment",
            "Aliases": ["alias1", "alias2"],
        },
    )
    assert reservation.to_sls() == expected_sls
