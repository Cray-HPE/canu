# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
                click.secho(f"Port number {number} must be an integer", fg="red"),
            )
        self.__number = number

        if not isinstance(speed, int) and speed is not None:
            raise Exception(
                click.secho(f"Port speed {speed} must be an integer", fg="red"),
            )
        self.__speed = speed
        self.__slot = slot
        self.__destination_node_id = destination_node_id
        self.__destination_port = None
        self.__destination_slot = None

    def port(self, number=None):
        """Get or set the physical port number."""
        if number is not None:
            if not isinstance(number, int):
                raise Exception(
                    click.secho(f"Port number {number} must be an integer", fg="red"),
                )
            self.__number = number
        return self.__number

    def speed(self, speed=None):
        """Get or set the port rate in Gbps."""
        if speed is not None:
            if not isinstance(speed, int):
                raise Exception(
                    click.secho(f"Port speed {speed} must be an integer", fg="red"),
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

    def destination_port(self, port_number=None):
        """Set the destination Node (edge) port_number for this port."""
        if port_number is not None:
            self.__destination_port = port_number
        return self.__destination_port

    def destination_slot(self, slot=None):
        """Set the destination Node (edge) slot for this port."""
        if slot is not None:
            self.__destination_slot = slot
        return self.__destination_slot

    def reset(self):
        """Reset all port attributes to default (None)."""
        self.__number = None
        self.__speed = None
        self.__slot = None
        self.__destination_node_id = None
        self.__destination_port = None
        self.__destination_slot = None

    def serialize(self):
        """Resolve this port as a JSON object."""
        serialized = {
            "port": self.__number,
            "speed": self.__speed,
            "slot": self.__slot,
            "destination_node_id": self.__destination_node_id,
            "destination_port": self.__destination_port,
            "destination_slot": self.__destination_slot,
        }
        return serialized
