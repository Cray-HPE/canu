# MIT License
#
# (C) Copyright 2022-2023, 2025 Hewlett Packard Enterprise Development LP
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
"""Classes for management of SLS Networks and Subnets."""
from collections import defaultdict
import ipaddress
from ipaddress import IPv4Address
from ipaddress import IPv4Network

from canu.utils.sls_utils.Reservations import Reservation

# A Subnet is a Network inside a Network CIDR range.
# A Subnet has IP reservations, a network does not
# https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html


class Network:
    """Represent a Network from and SLS data structure."""

    _name = None
    _full_name = ''
    _ipv4_address = None
    _mtu = None
    __type = None
    _subnets = None
    _bgp = None

    def __init__(self, name: str, ipv4_address: (str, ipaddress.IPv4Interface), **kwargs) -> None:
        """Create a Network.

        Args:
            name (str): Short name of the network
            ipv4_address: (str|IPv4Address): IPv4 CIDR of the network
        """
        self.name = name
        self.ipv4_address = ipv4_address

        self.type = kwargs.get('network_type', None)
        self.full_name = kwargs.get('full_name', '')
        self.mtu = kwargs.get('mtu', None)
        self.subnets = kwargs.get('subnets', defaultdict())
        self.bgp = kwargs.get('bgp', (None, None))  # [MyASN, PeerASN]

    @classmethod
    def network_from_sls_data(cls, sls_data):
        """Construct Network and any data-associated Subnets from SLS data.

        Args:
            sls_data: SLS data structure used to construct the network

        Returns:
            cls: Network object constructed from the SLS data structure
        """
        # "Promote" any ExtraProperties in Networks to ease initialization.
        if sls_data.get("ExtraProperties"):
            for key, value in sls_data["ExtraProperties"].items():
                sls_data[key] = value
            del sls_data["ExtraProperties"]

        # Cover specialty network(s)
        if sls_data.get("Name") == "BICAN":
            sls_network = BicanNetwork(
                default_route_network_name=sls_data.get("SystemDefaultRoute", "CMN"),
            )

        else:
            # Cover regular networks
            sls_network = cls(
                name=sls_data.get("Name"),
                network_type=sls_data.get("Type"),
                ipv4_address=sls_data.get("CIDR"),
            )

        sls_network.full_name = sls_data.get("FullName")

        # Check that the CIDR is in the IPRange, if IPRange exists.
        ipv4_range = sls_data.get("IPRanges")
        if ipv4_range and len(ipv4_range) > 0:
            temp_address = ipaddress.IPv4Interface(ipv4_range[0])
            if temp_address != sls_network.ipv4_address:
                print(f"WARNING: CIDR not in IPRanges from input {sls_network.name}.")

        sls_network.mtu = sls_data.get("MTU")

        subnets = sls_data.get("Subnets", defaultdict())
        for subnet in subnets:
            new_subnet = Subnet.subnet_from_sls_data(subnet)
            sls_network.subnets.update({new_subnet.name: new_subnet})

        sls_network.bgp = (sls_data.get("MyASN", None), sls_data.get("PeerASN"))

        return sls_network

    @property
    def name(self) -> str:
        """Short name of the network.

        Returns:
            name (str): Short name of the network for the getter
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Short name of the network.

        Args:
            name (str): Short name of the network for the setter
        """
        self._name = name

    @property
    def full_name(self) -> str:
        """Long, descriptive name of the network.

        Returns:
            full_name (str): Full name of the network for the getter
        """
        return self._full_name

    @full_name.setter
    def full_name(self, full_name: str) -> None:
        """Long, descriptive name of the network.

        Args:
            full_name (str): Full Name of the network for the setter
        """
        self._full_name = full_name

    @property
    def ipv4_address(self) -> ipaddress.IPv4Interface:
        """IPv4 network addressing.

        Returns:
            ipv4_address: IPv4 address of the network for the getter
        """
        return self._ipv4_address

    @ipv4_address.setter
    def ipv4_address(self, ipv4_address: (str, ipaddress.IPv4Interface)) -> None:
        """IPv4 network addressing.

        Args:
            ipv4_address: IPv4 address of the network for the setter
        """
        if isinstance(ipv4_address, str):
            ipv4_address = ipaddress.IPv4Interface(ipv4_address)
        self._ipv4_address = ipv4_address

    @property
    def ipv4_network(self) -> IPv4Network:
        """IPv4 network of the CIDR, Ranges, etc.

        Returns:
            ipv4_address.network: IPv4 network address of the Network.
        """
        return self.ipv4_address.network

    @property
    def mtu(self) -> int:
        """MTU of the network.

        Returns:
            mtu (int): MTU of the network for the getter
        """
        return self._mtu

    @mtu.setter
    def mtu(self, mtu: int) -> None:
        """MTU of the network.

        Args:
            mtu (int): MTU of the network for the setter
        """
        self._mtu = mtu

    @property
    def type(self) -> str:
        """Ethernet or specialty type of the network.

        Returns:
            type (str): Type of the network for the getter
        """
        return self.__type

    @type.setter
    def type(self, network_type: str) -> None:
        """Ethernet or specialty type of the network.

        Args:
            network_type (str): Type of the network (ethernet or otherwise) for the setter
        """
        self.__type = network_type

    @property
    def subnets(self) -> dict:
        """List of subnet objects in the network.

        Returns:
            subnets: A dict of subnets in the network for the getter
        """
        return self._subnets

    @subnets.setter
    def subnets(self, network_subnets: dict) -> None:
        """List of subnet objects in the network.

        Args:
            network_subnets: A dict of subnets in the network for the setter
        """
        self._subnets = network_subnets

    @property
    def bgp(self) -> tuple[int, int]:
        """Network BGP peering properties (optional).

        Returns:
            self._bgp (tuple): A tuple containing BGP ASNs (MyASN, PeerASN)
        """
        return self._bgp

    @bgp.setter
    def bgp(self, bgp: tuple[int, int]) -> None:
        """Network BGP peering properties (optional).

        Args:
            bgp (tuple): A tuple containing "my ASN" and the "Peer ASN"
        """
        self._bgp = bgp

    def to_sls(self):
        """Serialize the Network to SLS Networks format.

        Returns:
            sls: SLS data structure for the network
        """
        subnets = [x.to_sls() for x in self._subnets.values()]
        # TODO:  Is the VlanRange a list of used or a min/max?
        # x vlans = [min(vlans_list), max(vlans_list)]
        vlans_list = list(dict.fromkeys([x.vlan() for x in self._subnets.values()]))
        vlans = vlans_list
        sls = {
            "Name": self.name,
            "FullName": self.full_name,
            "Type": self.type,
            "IPRanges": [str(self.ipv4_address)],
            "ExtraProperties": {
                "CIDR": str(self.ipv4_address),
                "MTU": self.mtu,
                "VlanRange": vlans,
                "Subnets": subnets,
            },
        }

        if self.bgp[0] and self.bgp[1]:
            sls["ExtraProperties"]["MyASN"] = self.bgp[0]
            sls["ExtraProperties"]["PeerASN"] = self.bgp[1]

        return sls


class BicanNetwork(Network):
    """A customized BICAN Network."""

    _default_route_network = None

    def __init__(self, default_route_network_name: str = "CMN") -> None:
        """Create a new BICAN network.

        Args:
            default_route_network_name (str): Name of the user network for BICAN
        """
        super().__init__(
            name="BICAN",
            network_type="ethernet",
            ipv4_address="0.0.0.0/0",
            full_name = "System Default Route Network Name for Bifurcated CAN",
            mtu =9000,
        )
        self._default_route_network = default_route_network_name

    @property
    def default_route_network(self) -> str:
        """Returns the currently set default route, if any.

        Returns:
            self._default_route (str): The currently set default route.
        """
        return self._default_route_network

    @default_route_network.setter
    def default_route_network(self, default_route_network: str) -> None:
        """Sets the default route for this Network object.

        Args:
            default_route_network: The network to use for the default route.
        """
        self._default_route_network = default_route_network

    def to_sls(self):
        """Serialize the Network to SLS Networks format.

        Returns:
            sls: BICAN SLS Network structure
        """
        sls = super().to_sls()
        sls["ExtraProperties"]["SystemDefaultRoute"] = self._default_route_network
        return sls


class Subnet(Network):
    """Subnets are Networks with extra metadata: DHCP info, IP reservations, etc..."""

    _ipv4_dhcp_end_address = None
    _ipv4_dhcp_start_address = None
    _ipv4_gateway = None
    _ipv4_reservation_end_address = None
    _ipv4_reservation_start_address = None
    _pool_name = None
    _reservations = {}
    _vlan = None

    def __init__(self, name: str, ipv4_address: (str, ipaddress.IPv4Network), ipv4_gateway: (str, IPv4Address), vlan: int, **kwargs):
        """Create a new Subnet.

        Args:
            ipv4_gateway (str): IPv4 address of the network gateway
            vlan (int): VLAN ID of the subnet
        """
        super().__init__(name, ipv4_address, **kwargs)
        self.ipv4_gateway = ipv4_gateway
        self.vlan = vlan

    @classmethod
    def subnet_from_sls_data(cls, sls_data):
        """Create a Subnet from SLS data via a factory method.

        Args:
            sls_data (dict): Dictionary of Subnet SLS data

        Returns:
            cls (sls_utils.Subnet): Subnet constructed from SLS data
        """
        sls_subnet = cls(
            name=sls_data.get("Name"),
            ipv4_address=sls_data.get("CIDR"),
            ipv4_gateway=sls_data.get("Gateway"),
            vlan=sls_data.get("VlanID"),
        )

        sls_subnet.ipv4_gateway = ipaddress.IPv4Address(sls_data.get("Gateway"))

        sls_subnet.full_name = sls_data.get("FullName")
        sls_subnet.vlan = sls_data.get("VlanID")

        dhcp_start = sls_data.get("DHCPStart")
        if dhcp_start:
            dhcp_start = ipaddress.IPv4Address(dhcp_start)
            if dhcp_start not in sls_subnet.ipv4_network:
                print(f"ERROR: DHCP start [{dhcp_start}] not in Subnet [{sls_subnet.ipv4_network}].")
            sls_subnet.dhcp_start_address = dhcp_start

        dhcp_end = sls_data.get("DHCPEnd")
        if dhcp_end:
            dhcp_end = ipaddress.IPv4Address(dhcp_end)
            if dhcp_end not in sls_subnet.ipv4_network:
                print(f"ERROR: DHCP end [{dhcp_end}] not in Subnet [{sls_subnet.ipv4_network}].")
            sls_subnet.dhcp_end_address = dhcp_end

        reservation_start = sls_data.get("ReservationStart")
        if reservation_start is not None:
            reservation_start = ipaddress.IPv4Address(reservation_start)
            sls_subnet.reservation_start_address = reservation_start

        reservation_end = sls_data.get("ReservationEnd")
        if reservation_end is not None:
            reservation_end = ipaddress.IPv4Address(reservation_end)
            sls_subnet.reservation_end_address = reservation_end

        pool_name = sls_data.get("MetalLBPoolName")
        if pool_name is not None:
            sls_subnet.metallb_pool_name = pool_name

        reservations = sls_data.get("IPReservations", {})
        for reservation in reservations:
            sls_subnet.reservations.update(
                {
                    reservation.get("Name"): Reservation(
                        name=reservation.get("Name"),
                        ipv4_address=reservation.get("IPAddress"),
                        aliases=list(reservation.get("Aliases", [])),
                        comment=reservation.get("Comment"),
                    ),
                },
            )

        return sls_subnet

    @property
    def vlan(self) -> None:
        """VLAN of the subnet.

        Returns:
            vlan (int): Subnet VLAN ID for the getter
        """
        return self._vlan

    @vlan.setter
    def vlan(self, vlan: (int, str)) -> None:
        """VLAN of the subnet.

        Args:
            vlan (int, str): Subnet VLAN ID for the setter
        """
        if isinstance(vlan, str):
            vlan = int(vlan)
        if 1 <= vlan <= 4094:
            self._vlan = vlan

    @property
    def ipv4_gateway(self) -> IPv4Address:
        """IPv4 Gateway of the subnet.

        Returns:
            ipv4_gateway (IPv4Address): IPv4 gateway of the subnet for the getter
        """
        return self._ipv4_gateway

    @ipv4_gateway.setter
    def ipv4_gateway(self, ipv4_gateway: (str, IPv4Address)) -> None:
        """IPv4 Gateway of the subnet.

        Args:
            ipv4_gateway (str|IPv4Address): IPv4 gateway of the subnet for the setter
        """
        if isinstance(ipv4_gateway, str):
            ipv4_gateway = ipaddress.IPv4Address(ipv4_gateway)
        self._ipv4_gateway = ipv4_gateway

    @property
    def dhcp_start_address(self) -> IPv4Address:
        """IPv4 starting address if DHCP is used in the subnet.

        Returns:
            ipv4_dhcp_start_address (ipaddress.IPv4Address): Start DHCP address for getter
        """
        return self._ipv4_dhcp_start_address

    @dhcp_start_address.setter
    def dhcp_start_address(self, dhcp_start_address: (str, IPv4Address)) -> None:
        """IPv4 starting address if DHCP is used in the subnet.

        Args:
            dhcp_start_address (str|IPv4Address): IPv4 start of the DHCP range for setter
        """
        if isinstance(dhcp_start_address, str):
            dhcp_start_address = ipaddress.IPv4Address(dhcp_start_address)
        self._ipv4_dhcp_start_address = dhcp_start_address

    @property
    def dhcp_end_address(self) -> IPv4Address:
        """IPv4 ending address if DHCP is used in the subnet.

        Returns:
            ipv4_dhcp_end_address (ipaddress.IPv4Address): End DHCP address for getter
        """
        return self._ipv4_dhcp_end_address

    @dhcp_end_address.setter
    def dhcp_end_address(self, dhcp_end_address: (str, IPv4Address)) -> None:
        """IPv4 ending address if DHCP is used in the subnet.

        Args:
            dhcp_end_address (str|IPv4Address): IPv4 end of the DHCP range for setter
        """
        if isinstance(dhcp_end_address, str):
            dhcp_end_address = ipaddress.IPv4Address(dhcp_end_address)
        self._ipv4_dhcp_end_address = dhcp_end_address

    @property
    def reservation_start_address(self) -> IPv4Address:
        """IPv4 starting address used in uai_macvlan subnet.

        Returns:
            ipv4_reservation_start_address (ipaddress.IPv4Address): Start address of the reservation
        """
        return self._ipv4_reservation_start_address

    @reservation_start_address.setter
    def reservation_start_address(self, reservation_start: (str, IPv4Address)) -> None:
        """IPv4 starting address used in uai_macvlan subnet.

        Args:
            reservation_start (str|ipaddress.IPv4Address): Start address of the reservations
        """
        if isinstance(reservation_start, str):
            reservation_start = ipaddress.IPv4Address(reservation_start)
        self._ipv4_reservation_start_address = reservation_start

    @property
    def reservation_end_address(self) -> IPv4Address:
        """IPv4 ending address used in uai_macvlan subnet.

        Returns:
            ipv4_reservation_end_address (ipaddress.IPv4Address): Start address of the reservation
        """
        return self._ipv4_reservation_end_address

    @reservation_end_address.setter
    def reservation_end_address(self, reservation_end: (str, IPv4Address)) -> None:
        """IPv4 ending address used in uai_macvlan subnet.

        Args:
            reservation_end (ipaddress.IPv4Address): Start address of the reservations
        """
        if isinstance(reservation_end, str):
            reservation_end = ipaddress.IPv4Address(reservation_end)
        self._ipv4_reservation_end_address = reservation_end

    @property
    def metallb_pool_name(self) -> (str, None):
        """Retrieve or set the MetalLBPool name for the network (optional).

        Returns:
            pool_name (str|None): Name of the MetalLBPool (or None)
        """
        return self._pool_name

    @metallb_pool_name.setter
    def metallb_pool_name(self, pool_name: (str, None)) -> None:
        """Retrieve or set the MetalLBPool name for the network (optional).

        Args:
            pool_name (str): Name of the MetalLBPool (optional)
        """
        self._pool_name = pool_name

    @property
    def reservations(self) -> dict:
        """List of reservations for the subnet.

        Returns:
            reservations (dict): Lit of reservations for getter
        """
        return self._reservations

    @reservations.setter
    def reservations(self, reservations: dict) -> None:
        """List of reservations for the subnet.

        Args:
            reservations (dict): List of reservations for setter
        """
        self._reservations = reservations

    def to_sls(self):
        """Return SLS JSON for each Subnet.

        Returns:
            sls: SLS subnet data structure
        """
        sls = {
            "Name": self.name,
            "FullName": self.full_name,
            "CIDR": str(self.ipv4_address),
            "Gateway": str(self.ipv4_gateway),
            "VlanID": self.vlan,
        }

        if self.dhcp_start_address and self.dhcp_end_address:
            dhcp = {
                "DHCPStart": str(self.dhcp_start_address),
                "DHCPEnd": str(self.dhcp_end_address),
            }
            sls.update(dhcp)

        if (
            self.reservation_start_address is not None
            and self.reservation_end_address is not None  # noqa W503
        ):
            resrange = {
                "ReservationStart": str(self.reservation_start_address),
                "ReservationEnd": str(self.reservation_end_address),
            }
            sls.update(resrange)

        if self.metallb_pool_name is not None:
            sls.update({"MetalLBPoolName": self.metallb_pool_name})

        if self.reservations:
            reservations = {
                "IPReservations": [x.to_sls() for x in self.reservations.values()],
            }
            sls.update(reservations)
        return sls
