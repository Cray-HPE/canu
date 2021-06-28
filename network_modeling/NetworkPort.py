"""NetworkPort to create and manage ports in a node."""
import logging

import click

log = logging.getLogger(__name__)


class NetworkPort:
    """A class representing a port on a network device.

    Attributes
    ----------
    number: integer
        The physical port number (may relate to slot)
    slot: integer
        (Optional) Device may have sub-devices with individual ports (eg. PCIe Slot 1 port 2)
    speed: integer
        The port speed in Gigabits per second (Gbps)

    Methods
    -------
    port():
        Get or set the  port number
    slot():
        Get or set the  port slot (optional)
    speed():
        Get or set the  port speed (Gbps)
    reset():
        Reset all port attributes to default (None) values
    serialize():
        Return this port as a JSON object
    """

    def __init__(self, number=None, slot=None, speed=None, destination_node_id=None):
        """
        Construct the port object.

        Args:
            number: The physical port number on the device
            slot: (optional) Device slot that the port exists on
            speed: The speed of the port in Gbps
            destination_node_id: The destination node id (remote edge)

        Raises:
            Exception: When constructor port is not an integer
            Exception: When constructor speed is not an integer
        """
        if not isinstance(number, int) and number is not None:
            raise Exception(
                click.secho(f"Port number {number} must be an integer", fg="red")
            )
        self.__number = number

        if not isinstance(speed, int) and speed is not None:
            raise Exception(
                click.secho(f"Port speed {speed} must be an integer", fg="red")
            )
        self.__speed = speed
        self.__slot = slot
        self.__destination_node_id = destination_node_id

    def port(self, number=None):
        """Get or set the physical port number."""
        if number is not None:
            if not isinstance(number, int):
                raise Exception(
                    click.secho(f"Port number {number} must be an integer", fg="red")
                )
            self.__number = number
        return self.__number

    def speed(self, speed=None):
        """Get or set the port rate in Gbps."""
        if speed is not None:
            if not isinstance(speed, int):
                raise Exception(
                    click.secho(f"Port speed {speed} must be an integer", fg="red")
                )
            self.__speed = speed
        return self.__speed

    def slot(self, slot=None):
        """Get or set the slot where the port exists (optional)."""
        if slot is not None:
            self.__slot = slot
        return self.__slot

    def destination_node_id(self, id=None):
        """Set the destination Node (edge) id for this port."""
        if id is not None:
            self.__destination_node_id = id
        return self.__destination_node_id

    def reset(self):
        """Reset all port attributes to default (None)."""
        self.__number = None
        self.__speed = None
        self.__slot = None
        self.__destination_node_id = None

    def serialize(self):
        """Resolve this port as a JSON object."""
        serialized = {
            "port": self.__number,
            "speed": self.__speed,
            "slot": self.__slot,
            "destination_node_id": self.__destination_node_id,
        }
        return serialized
