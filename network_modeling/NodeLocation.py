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
