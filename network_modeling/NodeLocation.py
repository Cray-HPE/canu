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
        source_port:
        dest:
        dest_rack:
        dest_loc:
        dest_port:
    """

    def __init__(self, 
                rack=None, 
                elevation=None, 
                sub_elevation=None,
                source_slot=None,
                source_port=None,
                dest=None,
                dest_rack=None,
                dest_loc=None,
                dest_port=None):
        """Initialize location of equipment in the datacenter."""
        self.__rack = rack
        self.__elevation = elevation
        self.__sub_elevation = sub_elevation
        self.__source_slot = source_slot
        self.__source_port = source_port
        self.__dest = dest
        self.__dest_rack = dest_rack
        self.__dest_loc = dest_loc
        self.__dest_port = dest_port

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

    def sub_elevation(self, set_sub_elevation=None):
        """Get or set the rack elevation of the device."""
        if set_sub_elevation is not None:
            self.__sub_elevation = set_sub_elevation
        return self.__sub_elevation

    def source_slot(self, set_source_slot=None):
        """Get or set the source slot of the device."""
        if set_source_slot is not None:
            self.__source_slot = set_source_slot
        return self.__source_slot

    def source_port(self, set_source_port=None):
        """Get or set the source port of the device."""
        if set_source_port is not None:
            self.__source_port = set_source_port
        return self.__source_port

    def dest(self, setdest=None):
        """Get or set the destination of the device."""
        if setdest is not None:
            self.__dest = setdest
        return self.__dest

    def dest_rack(self, set_dest_rack=None):
        """Get or set the destination rack of the device."""
        if set_dest_rack is not None:
            self.__dest_rack = set_dest_rack
        return self.__dest_rack

    def dest_loc(self, set_dest_loc=None):
        """Get or set the destination location of the device."""
        if set_dest_loc is not None:
            self.__dest_loc = set_dest_loc
        return self.__dest_loc

    def dest_port(self, set_dest_port=None):
        """Get or set the destination port of the device."""
        if set_dest_port is not None:
            self.__dest_port = set_dest_port
        return self.__dest_port

    def serialize(self):
        """Resolve the datacenter information as a JSON object."""
        serialized = {"rack": self.__rack, 
                      "elevation": self.__elevation,
                      "sub_elevation": self.__sub_elevation,
                      "source_slot": self.__source_slot,
                      "source_port": self.__source_port,
                      "dest": self.__dest,
                      "dest_rack": self.__dest_rack,
                      "dest_loc": self.__dest_loc,
                      "dest_port": self.__dest_port}
        return serialized
