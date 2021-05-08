"""NetworkModel to create a new network."""

# Skip Testing this page, not currently used in CANU
import click  # pragma: no cover


class NetworkModel:  # pragma: no cover
    """A class representing a network model.

    Attributes
    ----------
    nodes : list
        A list of network nodes
    factory :

    Methods
    -------
    create_layer(old_nodes, reserve_ports=0):
        Creates a new layer in the hierarchy.
    create_topology(nodes):
        Not implemented
    assign_ports():
        Not implemented
    """

    def __init__(self, nodes=None, factory=None):
        """
        Construct the necessary attributes for the network model object.

        Args:
            nodes: A list of network nodes
            factory: factory

        Raises:
            Exception: A list of NetworkNode(s) is required
        """
        if factory:
            self.__factory = factory
        else:
            raise Exception(click.secho("A NetworkNodeFactory is required", fg="red"))

        if isinstance(nodes, list):
            self.__nodes = nodes
        else:
            raise Exception(
                click.secho("A list of NetworkNode(s) is required", fg="red")
            )

        self.__leafs = []
        self.__spines = []
        self.__superspines = []

    def create_layer(self, old_nodes, reserve_ports=0):
        """Create a new layer in the hierarchy.

        Creates a new layer in the hierarchy given the "southbound" list of devices
        E.g. Creates leafs given servers and cabinets, creates spines given leafs.
        In this case "old_nodes" is the list of the devices to create the new layer on.

        Args:
            old_nodes: the list of the devices to create the new layer on
            reserve_ports: Number of ports to reserve

        Returns:
            new_nodes
        """
        new_nodes = []
        for old in old_nodes:
            for connection in old.device_connections():
                node_type = connection["name"]
                node_speed = connection["speed"]
                msg = "Node {} is a {} and needs to ".format(old.id(), old.arch_type())
                msg += "connect to a {} at speed {}".format(node_type, node_speed)
                print(msg)

                # Find an existing node and connect the device
                node_found = False
                for new in new_nodes:
                    if (
                        new.arch_type() == node_type
                        and new.available_ports(node_speed) > reserve_ports
                    ):
                        print(
                            "    Found existing {} {}".format(new.arch_type(), new.id())
                        )
                        # Is bidirectional:  a.connect(b) also connects b to a.
                        # Internally new.connect(old) starts with the old connecting to new as those ports
                        # should be fewer (more used). Either way this will fully connect or roll back.
                        if new.connect(old):
                            print(
                                "    Connected existing node {} to node {} (bi-directionally)".format(
                                    old.id(), new.id()
                                )
                            )
                            node_found = True
                            break
                        else:
                            print(
                                "    Node {} to {} connection failed. Possibly out of ports".format(
                                    old.id(), new.id()
                                )
                            )
                            node_found = False
                            break
                    else:
                        print(
                            "    DEBUG: SKIPPING existing {} {} with non-matching type or {} available ports".format(
                                new.arch_type(),
                                new.id(),
                                new.available_ports(node_speed),
                            )
                        )

                # Create a new node and connect the device
                print(
                    "    Creating new node because matching device not found: {}".format(
                        not new_nodes or not node_found
                    )
                )
                if not new_nodes or not node_found:
                    new_node = self.__factory.generate_node(node_type)
                    print(
                        "    Created new {} {}".format(
                            new_node.arch_type(), new_node.id()
                        )
                    )
                    if reserve_ports:
                        print(
                            "    Reserving {} ports as requested on {}".format(
                                reserve_ports, new_node.arch_type()
                            )
                        )
                        # TODO: actually reserve the ports

                    # Is bidirectional:  a.connect(b) also connects b to a.
                    # Internally new.connect(old) starts with the old connecting to new as those ports
                    # should be fewer (more used). Either way this will fully connect or roll back.
                    if new_node.connect(old):
                        print(
                            "    Connected {} to {} (bi-directionally)".format(
                                old.id(), new_node.id()
                            )
                        )
                        new_nodes.append(new_node)
                        break
                    else:
                        print(
                            "    DEBUG: Could not connect new {} to {} (bi-directionally)".format(
                                old.id(), new_node.id()
                            )
                        )
                else:
                    break  # A device to connect to has already been found above.
        return new_nodes

    def create_topology(self, nodes):
        """Not implemented."""
        pass

    def assign_ports(self):
        """Not implemented."""
        pass
