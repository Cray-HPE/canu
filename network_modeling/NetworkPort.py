"""NetworkPort to create and manage ports in a node."""
import logging

log = logging.getLogger(__name__)


class NetworkPort:
    """A class representing a port on a network device.

    Attributes
    ----------
    number: integer
        The physical port number (may relate to slot)
    speed: integer
        The port speed in Gigabits per second (Gbps)
    slot: integer
        (Optional) Device may have sub-devices with individual ports (eg. PCIe Slot 1 port 2)

    Methods
    -------
    port():
        Get or set the  port number
    speed():
        Get or set the  port speed (Gbps)
    slot():
        Get or set the  port slot (optional)
    reset():
        Reset all port attributes to default (None) values
    """

    def __init__(self, number=None, speed=None, slot=None):
        """
        Construct the port object.

        Args:
            number: The physical port number on the device
            speed: The speed of the port in Gbps
            slot: (optional) Device slot that the port exists on

        """
        self.__number = number
        self.__speed = speed
        self.__slot = slot

    def port(self, number=None):
        """Get or set the physical port number."""
        if number is not None:
            self.__number = number
        return self.__number

    def speed(self, speed=None):
        """Get or set the port rate in Gbps."""
        if speed is not None:
            self.__speed = speed
        return self.__speed

    def slot(self, slot=None):
        """Get or set the slot where the port exists (optional)."""
        if slot is not None:
            self.__slot = slot
        return self.__slot

    def reset(self):
        """Reset all port attributes to default (None)."""
        self.__number = None
        self.__speed = None
        self.__slot = None
