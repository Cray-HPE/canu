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
"""NetworkNode to create a new node - switch, router or end device."""
import copy
import logging

from .NetworkPort import NetworkPort
from .NodeLocation import NodeLocation

log = logging.getLogger(__name__)


class NetworkNode:
    """A class representing a network node.

    Attributes
    ----------
    id : integer
        The id of the network node
    hardware :
    architecture :

    Methods
    -------
    available_ports(speed=None, slot=None, port=None):
        Return number of available ports
    id():
        Return unique node ID
    arch_type():
        Return architecture type
    common_name(name=None):
        Get/Set node common name
    device_connections():
        Returns a list of architecturally allowed connections.
    connect(node, bidirectional=True):
        Connect one device to another, from a mathematical node-edge perspective, not physical ports
    disconnect(node):
        Disconnect one device from another.
    edges():
        Return a list of all connections.
    serialize():
        Return the node as a JSON object.
    """

    def __init__(self, id=None, hardware=None, architecture=None):
        """
        Construct the necessary attributes for the network node object.

        Args:
            id: The id of the network node
            hardware: hardware
            architecture: architecture
        """
        self.__hardware = hardware
        self.__architecture = architecture

        self.__id = id
        self.__common_name = None
        self.__location = None
        self.__ports_block_metadata = copy.deepcopy(hardware["ports"])
        self.__ports = []

        self.__initialize_ports()

    # Use the base port/speed structure mapping and extend to track
    # ports used and track per-port data (NetworkPort)
    def __initialize_ports(self):
        """Create and fill out port structures for future use."""
        port_qty = 0
        for port in self.__ports_block_metadata:
            port_qty += port["count"]
            # Total is the immutable number of ports by speed "block".
            # Count is remaining ports which reduces on use.
            port["total"] = port["count"]
            if "slot" not in port:
                port["slot"] = None
        self.__ports = [None] * port_qty

        if "preserve_hardware_model_port_layout" not in self.__hardware:
            # Sort from lowest to highest speed.
            # NOTE: This implicitly makes the assumption that high speed ports are high port numbers.
            self.__ports_block_metadata = sorted(
                self.__ports_block_metadata,
                key=lambda k: max(k["speed"]),
            )
        # Find the list start index by speed.
        start_index = 0
        for block in self.__ports_block_metadata:
            block["start_index"] = start_index
            start_index += block["total"]

    """ Select a singular port type from a device given a port speed.
    This seems trivial, but it's possible that a devices's hardware
    may have port (sets/list) that have different max speeds and counts
    but supported (sub-speeds) in the ports overlap:
        ports:
         - count: 8
           speed: [100, 25]
         - count: 48
           speed: 25
         - count: 1
           speed: 1
           slot: "bmc"
    Here the port speed of 25 overlaps.  By default the selection would be
    determined based on the order in the hardware definition file.
    Here we make this deterministic based on a "cost" based on the highest
    port speed available and the number of ports.  We explicitly prefer matching
    slot types/names, but accept None"""

    def __select_port_block(self, speed=None, slot=None, port=None):
        """Find a block of ports that match a given speed, slot or port."""
        # Find blocks matching required speed, slot and remaining ports
        port_block = [
            x
            for x in self.__ports_block_metadata
            if speed in x["speed"] and slot == x["slot"] and x["count"] > 0
        ]

        if port_block:
            if len(port_block) > 1:
                # Prefer more total (not available) ports.
                port_block.sort(key=lambda k: (-k["total"]))
                log.warning(
                    "Multiple possible port blocks were found.  Using the first one.",
                )
            port_block = port_block[0]
        else:
            free_slots = ""
            for s in self.__ports_block_metadata:
                free_slots += f'{s["slot"]}:{s["count"]} '
            raise Exception(
                f"{__name__}: No available ports found for slot {slot} and speed {speed} "
                f"in node {self.__common_name}.  Available slot:ports - {free_slots}",
            )
        return port_block

    def __decrement_available_ports(self, port_block=None, count=1):
        """Subtract used port(s) from the count of the given block."""
        if port_block is None:
            raise Exception(
                f"{__name__}: Port block to decrement is a required argument.",
            )

        if port_block["count"] - count < 0:
            raise Exception(
                f"{__name__}: Port count in block {port_block} cannot be decremented as requested."
                f"Decrement of {count} uses more ports than are available.",
            )

        port_block["count"] -= count

        return self.__ports_block_metadata

    # Determine if a connection is allowed between components.
    #   Returns:  >0 speed of allowed connection if connection is allowed.
    #   Raises:   Exception of the connection is not architecturally allowed.
    #
    # The architectural definition only specifies upward/northbound
    # allowed connections.  Here we have no idea which node is north
    # of the other so we compare "bi-directionally" and return the speed
    # of the south-to-north direction.
    def __connection_allowed(self, node):
        connection_speed = None
        south_node = None
        north_node = None
        match_count = 0

        for connection in self.device_connections():
            if connection["name"] == node.arch_type():
                match_count += 1
                south_node = self
                north_node = node
                connection_speed = connection["speed"]
        for connection in node.device_connections():
            if connection["name"] == self.arch_type():
                match_count += 1
                south_node = node
                north_node = self
                connection_speed = connection["speed"]

        if match_count == 0:
            raise Exception(
                f"{__name__} The plan-of-record architectural definition does not allow connections "
                f"between {self.common_name()} ({self.arch_type()}) "
                f"and {node.common_name()} ({node.arch_type()}). "
                f"\nCheck that the correct architecture was selected or remove the connection.",
            )

        # Allow east-west connections (MLAG connections require this)
        # This is a bit of a trick since match_count will equal 2 when
        # arch_types are same.
        if self.arch_type() == node.arch_type():
            match_count -= 1

        if match_count != 1:
            log.warning(
                f"{__name__} Multiple architectural connection matches found between "
                f"{self.common_name()} ({self.arch_type()}) "
                f"and {node.common_name()} ({node.arch_type()}). "
                "This may not be an error, but validating the architectural definition is suggested.",
            )

        if south_node is None or north_node is None:
            raise Exception(
                f"{__name__} Cannot determine architectural direction between "
                f"{self.common_name()} ({self.arch_type()}) "
                f"and {node.common_name()} ({node.arch_type()}).  "
                "Check architectural definition.",
            )

        if connection_speed is None:
            raise Exception(
                f"{__name__} Connection not architecturally allowed between "
                f"{self.common_name()} ({self.arch_type()}) "
                f"and {node.common_name()} ({node.arch_type()}) at any speed. "
                "Check architectural definition.",
            )

        log.debug(
            f"Connection from {south_node.arch_type()} to {north_node.arch_type()} "
            f"architecturally allowed at speed {connection_speed}.",
        )

        return connection_speed

    # Unique node ID
    def id(self):
        """Return unique node ID."""
        return self.__id

    def arch_type(self):
        """Return architecture type."""
        return self.__architecture["name"]

    def common_name(self, name=None):
        """Get/Set node common name."""
        if name is not None:
            self.__common_name = name
        return self.__common_name

    def location(self, setlocation=None):
        """Get/Set position of node in the datacenter."""
        if setlocation is not None:
            if not isinstance(setlocation, NodeLocation):
                log.error("Attempting to set location a non-NodeLocation instance.")
            else:
                self.__location = setlocation
        return self.__location

    # Architecturally allowed connections.
    def device_connections(self):
        """Return a list of architecturally allowed connections."""
        # Returns list
        return self.__architecture["connections"]

    def available_ports(self, speed=None, slot=None, port=None, next_free_port=False):
        """Return number of available ports."""
        available = self.__select_port_block(speed=speed, slot=slot, port=port)

        if available is None:
            raise Exception(
                f"{__name__}: Available port at speed {speed} not found for {self.common_name()} "
                f'of type {self.__architecture["name"]} and model {self.__architecture["model"]}',
            )
        if next_free_port:
            return int(available["total"]) - int(available["count"]) + 1
        else:
            return available["count"]

    # Connect one device to another.
    # From a mathematical node-edge perspective, not physical ports
    def connect(
        self,
        dst_node,
        src_port=None,
        dst_port=None,
        strict=False,
        bidirectional=True,
    ):
        """Connect one device to another."""
        # Defensively check input node type.
        if not isinstance(dst_node, NetworkNode):
            raise TypeError(
                f"{__name__}: Node needs to be type NetworkNode",
            )
        if src_port is not None and not isinstance(src_port, NetworkPort):
            raise TypeError(
                f"{__name__}: Source Port needs to be type NetworkPort or None",
            )
        if dst_port is not None and not isinstance(dst_port, NetworkPort):
            raise TypeError(
                f"{__name__}: Source Port needs to be type NetworkPort or None",
            )

        # First create the connection on the destination (to local).
        # If this fails then we "roll back" by exiting out.
        if bidirectional:
            # The src and dst port swap here is required based on connection direction.
            if not dst_node.connect(
                self,
                src_port=dst_port,
                dst_port=src_port,
                bidirectional=False,
                strict=True,
            ):
                log.error(
                    "Connection of local to remote failed - "
                    "usually no ports are available or port already used.",
                )
                return False

        # Find the the architectural connection speed
        connection_speed = self.__connection_allowed(dst_node)

        # Create port stubs if needed and begin to fill out port info
        if src_port is None:
            src_port = NetworkPort()
            src_port.destination_node_id(dst_node.id())
        if dst_port is None:
            dst_port = NetworkPort()
            dst_port.destination_node_id(self.id())

        src_port.speed(connection_speed)
        dst_port.speed(connection_speed)

        log.debug(
            f"Node {self.__id} ({self.common_name()}) connecting "
            f"node {dst_node.id()} ({dst_node.common_name()}) "
            f"to itself at speed {connection_speed}.",
        )

        # Find a block of ports of the appropriate speed/slot
        selected_ports = self.__select_port_block(
            speed=connection_speed,
            slot=src_port.slot(),
            port=src_port.port(),
        )
        if selected_ports is None:
            log.error(
                f"No ports available in slot {src_port.slot()} at speed {connection_speed}",
            )
            return False
        log.debug(
            f'{selected_ports["count"]} remaining ports in slot {selected_ports["slot"]} at speed {connection_speed}',
        )

        # Second, connect the local node to the destination.
        # Focus on src_node and src_port here.  Bi-directional aspect
        # already dealt with dst_node and dst_port.
        if src_port.port() is not None:
            offset = 0
            if selected_ports["slot"] is not None:
                offset = selected_ports["start_index"]
            index = offset + src_port.port() - 1

            if index > len(self.__ports) - 1 or index < 0:
                raise Exception(
                    f"{__name__} Port {src_port.port()} was requested from {self.__id}:{self.__common_name} "
                    f"but only {len(self.__ports)-1} Ports are available on the Node.",
                )

            if self.__ports[index] is not None:
                existing_port = self.__ports[index]
                if existing_port.destination_node_id() == dst_node.id():
                    log.warning(
                        f"Node {self.__id} ({self.__common_name}): port {src_port.port()} in slot {src_port.slot()} "
                        f"already connected to Node {dst_node.id()} ({dst_node.common_name()}): port {dst_port.port()} "
                        f"in slot {dst_port.slot()} {src_port.destination_port()} {src_port.destination_slot()}",
                    )
                    if strict:
                        return False
                    return True  # no-op because already connected
                else:
                    raise Exception(
                        f"{__name__} Port {src_port.port()} in slot {src_port.slot()} "
                        f"already in use for {self.common_name()} connected to a different "
                        f"node {existing_port.destination_node_id()}.  Cannot repurpose previously used ports.",
                    )

            src_port.destination_node_id(dst_node.id())
            src_port.destination_port(dst_port.port())
            src_port.destination_slot(dst_port.slot())
            self.__ports[index] = src_port
            self.__decrement_available_ports(port_block=selected_ports)
            log.debug(
                f"Successfully connected {dst_node.common_name()} to {self.common_name()} at speed {connection_speed}",
            )
        else:
            # Assign ports based on first available.
            start_index = selected_ports["start_index"]
            stop_index = start_index + selected_ports["total"]
            next_free_port_index = None
            for index in range(start_index, stop_index):
                if self.__ports[index] is not None:
                    continue
                next_free_port_index = index
                break

            src_port.port(number=next_free_port_index + 1)
            self.__ports[next_free_port_index] = src_port
            self.__decrement_available_ports(port_block=selected_ports)
            log.debug(
                f"  Successfully connected {dst_node.common_name()} to {self.common_name()} at speed {connection_speed}",
            )
        return True

    def assign_port(self, port=None, destination_node=None):
        """Connect an edge connection to a physical port."""
        # Defensively check input node type.
        if not isinstance(port, NetworkPort):
            raise TypeError(
                f"{__name__}: Port needs to be type NetworkPort",
            )
        if not isinstance(destination_node, NetworkNode):
            raise TypeError(
                f"{__name__}: Node needs to be type NetworkNode",
            )
        pass

    def disconnect(self, node):
        """Disconnect one device from another."""
        # Defensively check input node type.
        if not isinstance(node, NetworkNode):
            raise TypeError(
                "Node needs to be type NetworkNode",
            )

        # TODO:  this for real
        return False

    def serialize(self):
        """Resolve this node as a JSON object."""
        serialized_ports = [
            port.serialize() for port in self.__ports if port is not None
        ]

        serialized_location = None
        if self.__location is not None:
            serialized_location = self.__location.serialize()

        serialized = {
            "common_name": self.__common_name,
            "id": self.__id,
            "architecture": self.__architecture["name"],
            "model": self.__hardware["model"],
            "type": self.__hardware["type"],
            "vendor": self.__hardware["vendor"],
            "ports": serialized_ports,
            "location": serialized_location,
        }
        return serialized

    def edges(self):
        """Return a list of all connections."""
        edges = []
        for port in self.__ports:
            if port is not None:
                edges.append(port.destination_node_id())
        return edges

    def ports(self):
        """Return a list of all connections."""
        ports = []
        for port in self.__ports:
            if port is not None:
                ports.append(port.serialize())
            else:
                ports.append(None)
        return ports
