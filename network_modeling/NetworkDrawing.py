"""NetworkDrawing creates network diagram image files."""

# Skip Testing this page, not currently used in CANU
# This creates network diagram image files.
# TODO: requires much work!
# import matplotlib.image as pltimg
import matplotlib.pyplot as plt  # pragma: no cover
import networkx as nx  # pragma: no cover


# Por reference: https://plotly.com/python/network-graphs/
class NetworkDrawing:  # pragma: no cover
    """A class to create network diagram image files.

    Attributes
    ----------
    nodes :

    prune_nodes :

    image_type :

    image_size :



    Methods
    -------
    draw():
        Create a network diagram image.
    create_topology(nodes):
        Not implemented
    assign_ports():
        Not implemented
    """

    def __init__(self, nodes, prune_nodes=False, image_type="svg", image_size=500):
        """Construct the necessary attributes for the network diagram.

        Parameters
        ----------
        nodes :

        prune_nodes :

        image_type :

        image_size :
        """
        self.__image_type = image_type
        self.__image_size = image_size
        self.__nodes = nodes
        self.__prune = prune_nodes  # Don't show server/cabinet devices

    def draw(self):
        """Create a network diagram image."""
        #
        # Convert the generated to a graph
        #    MultiGraph allows multiple edges (cables) between nodes.
        #
        G = nx.MultiGraph()

        # Edges first - will implicitly create graph nodes
        # Quick hack is that the leafs will show both self, spine and node connections
        # for leaf in leafs:
        node_list = self.__nodes
        node_color = ["red"] * len(self.__nodes)
        # TODO fix
        # if self.__prune:
        #     for node in self.__nodes:

        for node in node_list:
            print(node.arch_type())
            for edge in node.edges():
                print("Adding edge: {}".format((node.id(), edge)))
                G.add_edge(node.id(), edge)
        print()

        # node_list = spines + leafs + nodes
        # Quick hack - this should be autodiscovered
        for node in node_list:
            if node.arch_type().find("spine") != -1:
                G.nodes[node.id()]["tier"] = 3
                node_color[node.id()] = "red"
            elif node.arch_type().find("edge") != -1:
                G.nodes[node.id()]["tier"] = 4
                node_color[node.id()] = "purple"
            elif node.arch_type().find("leaf") != -1:
                G.nodes[node.id()]["tier"] = 2
                node_color[node.id()] = "orange"
            elif node.arch_type().find("bmc") != -1:
                G.nodes[node.id()]["tier"] = 1
                node_color[node.id()] = "yellow"
            else:
                G.nodes[node.id()]["tier"] = 0
                node_color[node.id()] = "blue"

            G.nodes[node.id()]["name"] = node.common_name()
        print()

        #
        # Graph layout - generate coordinates for the graph
        #
        pos = nx.multipartite_layout(
            G, subset_key="tier", align="horizontal", scale=3
        )  # scale positions

        #
        # xxx
        #

        #
        # Connections (with calcs for labels) (edges)
        #
        nx.draw(G, pos=pos)
        # nx.draw_networkx(G, pos=pos, with_labels=False, width=0.5)
        # nx.draw_networkx(G, pos=pos, node_color=node_color, with_labels=True)
        plt.savefig("fig2.png")
