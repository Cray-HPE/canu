# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
"""NodeLocation to position and manage devices within a datacenter (incl. xnames)."""


class NodeLocation:
    """
    Construct the necessary attributes to manage a device's data center location.

    Args:
        rack: The rack name/number (e.g. x1001)
        elevation: The position of the device in the rack (e.g. u19)
    """

    def __init__(self, rack=None, elevation=None):
        """Initialize location of equipment in the datacenter."""
        self.__rack = rack
        self.__elevation = elevation

    def rack(self, setrack=None):
        """Get or set the rack location of the device."""
        if setrack is not None:
            self.__rack = setrack
        return self.__rack

    def elevation(self, setelevation=None):
        """Get or set the rack elevation of the device."""
        if setelevation is not None:
            self.__elevation = setelevation
        return self.__elevation

    def serialize(self):
        """Resolve the datacenter information as a JSON object."""
        serialized = {"rack": self.__rack, "elevation": self.__elevation}
        return serialized
