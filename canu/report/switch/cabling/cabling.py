# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
"""CANU commands that report the cabling of an individual switch."""
from collections import defaultdict, OrderedDict
import datetime
from json import decoder
import re
import sys
from urllib.parse import unquote

import click
import natsort
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException
import requests
import urllib3

from canu.style import Style
from canu.utils.cache import cache_switch
from canu.utils.mac import find_mac
from canu.utils.ssh import netmiko_command, netmiko_commands
from canu.utils.vendor import switch_vendor

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command(
    cls=Style.CanuHelpColorsCommand,
)
@click.option("--ip", required=True, help="The IP address of the switch")
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--out",
    help="Output results to a file",
    type=click.File("w"),
    default="-",
)
@click.pass_context
def cabling(ctx, ip, username, password, out):
    """Report the cabling of a switch (Aruba, Dell, or Mellanox) on the network by using LLDP.

    If the neighbor name is not in LLDP, the IP and vlan information are displayed
    by looking up the MAC address in the ARP table or the mac address table.

    If there is a duplicate port, the duplicates will be highlighted in 'bright white'.

    Ports highlighted in 'blue' contain the string "ncn" in the hostname.

    Ports are highlighted in 'green' when the port name is set with the interface name.

    --------
    \f
    # noqa: D301, B950

    Args:
        ctx: CANU context settings
        ip: Switch IPv4 address
        username: Switch username
        password: Switch password
        out: Name of the output file
    """
    credentials = {"username": username, "password": password}
    switch_info, switch_dict, arp = get_lldp(ip, credentials)
    if switch_info is None:
        return

    print_lldp(switch_info, switch_dict, arp, out)


def get_lldp(ip, credentials, return_error=False):
    """Get lldp of an Aruba, Dell, or Mellanox switch.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: Bool if the error should be printed or returned

    Returns:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary

    Raises:
        NetmikoTimeoutException: Timeout error connecting to switch
        NetmikoAuthenticationException: Authentication error connecting to switch
    """
    try:
        vendor = switch_vendor(ip, credentials, return_error)

        if vendor is None:
            return None, None, None
        elif vendor == "aruba":
            switch_info, switch_dict, arp = get_lldp_aruba(
                ip,
                credentials,
                return_error,
            )
        elif vendor == "dell":
            switch_info, switch_dict, arp = get_lldp_dell(ip, credentials, return_error)
        elif vendor == "mellanox":
            switch_info, switch_dict, arp = get_lldp_mellanox(
                ip,
                credentials,
                return_error,
            )

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.RequestException,
        requests.exceptions.ConnectionError,
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
    ) as error:
        if return_error:
            raise error

        exception_type = type(error).__name__
        click.secho(
            f"Error connecting to switch {ip}, {exception_type} {error}.",
            fg="white",
            bg="red",
        )
        return None, None, None

    return switch_info, switch_dict, arp


def get_lldp_aruba(ip, credentials, return_error=False):
    """Get lldp of an Aruba switch using v10.04 API.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: Bool if the error should be printed or returned

    Returns:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary

    Raises:
        error: Error
    """
    session = requests.Session()
    try:
        # Login
        login = session.post(
            f"https://{ip}/rest/v10.04/login",
            data=credentials,
            verify=False,
        )
        login.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as err:
        if return_error:
            raise err

        exception_type = type(err).__name__

        if exception_type == "HTTPError":
            error_message = (
                f"Error connecting to switch {ip}, check the username or password."
            )
        elif exception_type == "ConnectionError":
            error_message = (
                f"Error connecting to switch {ip}, check the entered username, IP address and password."
            )
        else:
            error_message = f"Error connecting to switch {ip}."

        click.secho(
            str(error_message),
            fg="white",
            bg="red",
        )

        return None, None, None

    try:
        # GET switch info
        switch_info_response = session.get(
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            verify=False,
        )
        switch_info_response.raise_for_status()
        switch_info = switch_info_response.json()
        switch_info["ip"] = ip
        switch_info["vendor"] = "aruba"

        # GET LLDP neighbors
        neighbors = session.get(
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            verify=False,
        )
        neighbors.raise_for_status()
        neighbors_dict = neighbors.json()

        arp_response = session.get(
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            verify=False,
        )
        arp_response.raise_for_status()
        arp = arp_response.json()

        lldp_dict = defaultdict(list)
        for port_number, port in neighbors_dict.items():
            interface = unquote(port_number)

            for _mac, lldp_info in port.items():
                neighbor_info = lldp_info["neighbor_info"]
                if neighbor_info["chassis_description"] == "":
                    description = find_mac(lldp_info["mac_addr"])
                else:
                    description = neighbor_info["chassis_description"]
                lldp_neighbor = {
                    "chassis_id": lldp_info["chassis_id"],
                    "mac_addr": lldp_info["mac_addr"],
                    "chassis_description": description,
                    "chassis_name": neighbor_info["chassis_name"],
                    "port_description": neighbor_info["port_description"],
                    "port_id_subtype": neighbor_info["port_id_subtype"],
                    "port_id": lldp_info["port_id"],
                }

                lldp_dict[interface].append(lldp_neighbor)

        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

        # Get the mac-address-table to help fill in port data if not reported over LLDP
        command = "show mac-address-table"
        command_output = netmiko_command(ip, credentials, command, "aruba")
        mac_address_table = defaultdict()

        # Start parsing after the header
        for line in command_output.splitlines()[5:]:
            line = line.split()
            table_mac = line[0]
            table_port = line[3]
            if "lag" not in table_port:
                mac_address_table[table_port] = table_mac

        # Add the mac-address-table data to the lldp_dict
        for device_port, mac in mac_address_table.items():
            if device_port not in lldp_dict.keys():
                lldp_dict[device_port] = [
                    {
                        "chassis_id": "",
                        "mac_addr": mac,
                        "chassis_description": find_mac(mac),
                        "port_description": "",
                        "chassis_name": "",
                        "port_id": mac,
                        "port_id_subtype": "link_local_addr",
                    },
                ]

        # Order the ports in natural order
        lldp_dict = OrderedDict(natsort.natsorted(lldp_dict.items()))

        cache_lldp(switch_info, lldp_dict, arp)

        return switch_info, lldp_dict, arp

    except requests.exceptions.RequestException as error:  # pragma: no cover
        if return_error:
            raise error

        click.secho(
            f"Error getting cabling information from switch {ip}",
            fg="white",
            bg="red",
        )
        return None, None, None


def get_lldp_dell(ip, credentials, return_error):
    """Get lldp of a Dell switch using ssh commands.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: Bool if the error should be printed or returned

    Returns:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary

    Raises:
        Exception: Unknown error
        NetmikoTimeoutException: Timeout error connecting to switch
        NetmikoAuthenticationException: Authentication error connecting to switch
    """
    try:
        neighbors_dict = defaultdict(dict)
        port = 0
        commands = [
            "terminal length 0",
            "show lldp neighbors detail",
            "show version",
            "system hostname",
            "show ip arp",
            "show mac address-table",
        ]
        command_output = netmiko_commands(ip, credentials, commands, "dell")

        for line in command_output[1].splitlines():
            if line.startswith("-----------------------"):
                port += 1
            elif line.startswith("Remote Chassis ID:"):
                chassis_id = line[19:]
                if chassis_id == "Not Advertised":
                    chassis_id = ""
                neighbors_dict[port]["chassis_id"] = chassis_id
                neighbors_dict[port]["mac_addr"] = chassis_id
            elif line.startswith("Remote System Desc:"):
                chassis_description = line[20:]
                if chassis_description == "Not Advertised":
                    chassis_description = ""
                if chassis_description == "":
                    chassis_description = find_mac(
                        neighbors_dict[port]["mac_addr"],
                    )
                neighbors_dict[port]["chassis_description"] = chassis_description
            elif line.startswith("Remote Port Description:"):
                port_description = line[25:]
                if port_description == "Not Advertised":
                    port_description = ""
                if port_description == "":
                    port_description = find_mac(
                        neighbors_dict[port]["mac_addr"],
                    )
                neighbors_dict[port]["port_description"] = port_description
            elif line.startswith("Remote System Name:"):
                chassis_name = line[20:]
                if chassis_name == "Not Advertised":
                    chassis_name = ""
                neighbors_dict[port]["chassis_name"] = chassis_name
            elif line.startswith("Remote Port ID: "):
                port_id = line[16:]
                if port_id.startswith("Eth"):
                    port_id = "1/" + port_id[3:]
                if port_id.startswith("ethernet"):
                    port_id = port_id[8:]
                neighbors_dict[port]["port_id"] = port_id
            elif line.startswith("Local Port ID: "):
                if line.startswith("Local Port ID: ethernet"):
                    neighbors_dict[port]["local_port_id"] = line.split("ethernet")[1]
                elif line.startswith("Local Port ID: mgmt"):
                    neighbors_dict[port]["local_port_id"] = line.split("mgmt")[1]

        lldp_dict = defaultdict(list)
        for port in neighbors_dict:
            port_dict = neighbors_dict[port]

            if "chassis_id" not in port_dict.keys():
                neighbors_dict[port]["chassis_id"] = ""
            if "chassis_description" not in port_dict.keys():
                neighbors_dict[port]["chassis_description"] = ""
            if "mac_addr" not in port_dict.keys():
                neighbors_dict[port]["mac_addr"] = port_dict.get("chassis_id", "")
            if "port_description" not in port_dict.keys():
                neighbors_dict[port]["port_description"] = ""
            if "chassis_name" not in port_dict.keys():
                neighbors_dict[port]["chassis_name"] = ""

            neighbors_dict[port]["port_id_subtype"] = "if_name"
            interface = neighbors_dict[port]["local_port_id"]

            lldp_dict[interface].append(neighbors_dict[port])

        # Get the mac-address-table to help fill in port data if not reported over LLDP
        mac_address_table = defaultdict()

        # Start parsing mac address-table after the header
        for line in command_output[5].splitlines()[1:]:
            line = line.split()
            table_mac = line[1]
            table_port = line[3]
            if "ethernet" in table_port:
                table_port = table_port.replace("ethernet", "")
                mac_address_table[table_port] = table_mac

        # Add the mac-address-table data to the lldp_dict
        for device_port, mac in mac_address_table.items():
            if device_port not in lldp_dict.keys():
                lldp_dict[device_port] = [
                    {
                        "chassis_id": "",
                        "mac_addr": mac,
                        "chassis_description": find_mac(mac),
                        "port_description": "",
                        "chassis_name": "",
                        "port_id": mac,
                        "port_id_subtype": "link_local_addr",
                    },
                ]

        # Order the ports in natural order
        lldp_dict = OrderedDict(natsort.natsorted(lldp_dict.items()))

        # Switch Firmware and Switch Model
        switch_firmware = {
            "current_version": "",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        }
        for line in command_output[2].splitlines():
            if line.startswith("OS Version:"):
                switch_firmware["current_version"] = line[12:]
            if line.startswith("System Type:"):
                platform_name = line[13:]

        # Switch Hostname
        hostname = command_output[3]

        switch_info = {
            "platform_name": platform_name,
            "hostname": hostname,
        }

        # Cache switch values
        switch_json = {
            "ip_address": ip,
            "ip": ip,
            "hostname": switch_info["hostname"],
            "platform_name": switch_info["platform_name"],
            "vendor": "dell",
            "firmware": switch_firmware,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # ARP
        arp = defaultdict(dict)
        for line in command_output[4].splitlines()[2:]:
            line_list = line.split()
            if len(line_list) != 4:
                pass
            arp_ip = line_list[0]
            arp_mac = line_list[1]
            arp_vlan = line_list[2]
            arp_dict = {
                "ip_address": arp_ip,
                "mac": arp_mac,
                "port": [arp_vlan],
            }

            arp[arp_mac] = arp_dict

        cache_lldp(switch_json, lldp_dict, arp)

    except (
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
        Exception,
    ) as err:
        if return_error:
            raise err

        exception_type = type(err).__name__

        if exception_type == "NetmikoTimeoutException":
            error_message = f"Timeout error connecting to switch {ip}, check the entered username, IP address and password."
        elif exception_type == "NetmikoAuthenticationException":
            error_message = f"Authentication error connecting to switch {ip}, check the credentials or IP address and try again."
        else:
            error_message = f"{exception_type}, {err}."

        click.secho(
            error_message,
            fg="white",
            bg="red",
        )

        return None, None, None

    return switch_json, lldp_dict, arp


def get_lldp_mellanox(ip, credentials, return_error):
    """Get lldp of a Mellanox switch using the API.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: Bool if the error show be printed or returned

    Returns:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary

    Raises:
        HTTPError: IP not Mellanox switch, or credentials bad.
        ConnectionError: Bad IP address.
    """
    session = requests.Session()

    # Login
    login = session.post(
        f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
        json=credentials,
        verify=False,
    )

    if login.status_code == 404:
        if return_error:
            raise requests.exceptions.ConnectionError

        click.secho(
            f"Error connecting to switch {ip}, check the entered username, IP address and password.",
            fg="white",
            bg="red",
        )
        return None, None, None
    if login.json()["status"] != "OK":
        if return_error:
            raise requests.exceptions.HTTPError

        click.secho(
            f"Error connecting to switch {ip}, check the username or password.",
            fg="white",
            bg="red",
        )
        return None, None, None

    try:
        lldp_remote = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show lldp interfaces ethernet remote"},
            verify=False,
        )

        lldp_json = lldp_remote.json()

        neighbors_dict = defaultdict(dict)
        for x in lldp_json["data"]:
            for port in x:
                neighbor_dict = defaultdict()

                if x.get("Lines") == ["", "No lldp remote information.", ""]:
                    break
                local_port_id = "1/" + port.strip("Eth").split()[0]

                neighbor_dict["local_port_id"] = local_port_id
                for prop in x[port]:
                    if "Remote chassis id" in prop:
                        chassis_id = prop.get("Remote chassis id")
                        if chassis_id == "Not Advertised":
                            chassis_id = ""
                        neighbor_dict["chassis_id"] = chassis_id
                        neighbor_dict["mac_addr"] = chassis_id
                    if "Remote system description" in prop:
                        chassis_description = prop.get("Remote system description")
                        if chassis_description == "Not Advertised":
                            chassis_description = ""
                        if chassis_description == "":
                            chassis_description = find_mac(
                                neighbor_dict["mac_addr"],
                            )
                        neighbor_dict["chassis_description"] = chassis_description
                    if "Remote system name" in prop:
                        chassis_name = prop.get("Remote system name")
                        if chassis_name == "Not Advertised":
                            chassis_name = ""
                        neighbor_dict["chassis_name"] = chassis_name
                    if "Remote port description" in prop:
                        port_description = prop.get("Remote port description")
                        if port_description == "Not Advertised":
                            port_description = ""
                        neighbor_dict["port_description"] = port_description
                    if "Remote port-id" in prop:
                        port_id = prop.get("Remote port-id")
                        if port_id == "Not Advertised":
                            port_id = ""
                        if port_id.startswith("Eth"):
                            port_id = "1/" + port_id[3:]
                        if port_id.startswith("ethernet"):
                            port_id = port_id[8:]
                        neighbor_dict["port_id"] = port_id

                neighbors_dict[port] = neighbor_dict

        lldp_dict = defaultdict(list)
        for _port_number, port_info in neighbors_dict.items():
            if "chassis_id" not in port_info.keys():
                port_info["chassis_id"] = ""
            if "mac_addr" not in port_info.keys():
                port_info["mac_addr"] = port_info.get("chassis_id", "")
            if "chassis_description" not in port_info.keys():
                port_info["chassis_description"] = ""
            if "port_description" not in port_info.keys():
                port_info["port_description"] = ""
            if "chassis_name" not in port_info.keys():
                port_info["chassis_name"] = ""
            port_info["port_id_subtype"] = "if_name"
            interface = port_info["local_port_id"]
            lldp_dict[interface].append(port_info)

        # Get the mac-address-table to help fill in port data if not reported over LLDP
        # On Mellanox this is a two step process,
        # First get the mlags and what port each one is associated with
        mlag_remote = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show interfaces mlag-port-channel summary | include LACP"},
            verify=False,
        )

        mlag_json = mlag_remote.json()

        mlag_dict = defaultdict()
        for entry in list(mlag_json["data"][0].items())[0][1]:
            mlag_line = entry.split()
            mpo_line = mlag_line[1].split("(")[0]
            port_line = mlag_line[3].split("(")[0].replace("Eth", "1/")
            mlag_dict[mpo_line] = port_line

        # Second get the mac-address-table and use the associated ports
        mat_remote = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show mac-address-table"},
            verify=False,
        )

        mat_json = mat_remote.json()

        address_table_dict = defaultdict(list)
        for _vlan, info in mat_json["data"].items():
            for x in info:
                try:
                    port_mat = x.get("Port\\Next Hop").replace("Eth", "1/")
                    mac_mat = x.get("Mac Address")
                    if "Mpo" in port_mat:
                        port = mlag_dict[port_mat]
                        address_table_dict[port].append(mac_mat)
                except AttributeError:
                    pass

        # Add the mac-address-table data to the lldp_dict
        for device_port, mac_list in address_table_dict.items():
            if device_port not in lldp_dict.keys():
                for mac in mac_list:
                    lldp_dict[device_port] = [
                        {
                            "chassis_id": "",
                            "mac_addr": mac,
                            "chassis_description": find_mac(mac),
                            "port_description": "",
                            "chassis_name": "",
                            "port_id": mac,
                            "port_id_subtype": "link_local_addr",
                        },
                    ]

        # Order the ports in natural order
        lldp_dict = OrderedDict(natsort.natsorted(lldp_dict.items()))

        # Switch Hostname
        switch_hostname = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show hosts | include Hostname"},
            verify=False,
        )
        switch_hostname.raise_for_status()

        hostname = switch_hostname.json()["data"][0]["Hostname"]

        # Switch Model
        system_type = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": "show system type"},
            verify=False,
        )
        system_type.raise_for_status()

        platform_name = system_type.json()["data"]["value"]

        switch_info = {
            "platform_name": platform_name[0],
            "hostname": hostname,
        }

        # Cache switch values
        switch_json = {
            "ip_address": ip,
            "ip": ip,
            "hostname": switch_info["hostname"],
            "platform_name": switch_info["platform_name"],
            "vendor": "mellanox",
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # ARP
        arp_response = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"cmd": 'show ip arp | exclude "Total number of entries"'},
            verify=False,
        )
        arp_response.raise_for_status()
        arp_response = arp_response.json()["data"]

        for entry in arp_response:
            if "VRF Name default" in entry:
                arp_json = entry

        arp = defaultdict(dict)
        for arp_ip, arp_info in arp_json.items():
            arp_mac = arp_info[0].get("Hardware Address")
            arp_port = arp_info[0].get("Interface")
            arp_dict = {
                "ip_address": arp_ip,
                "mac": arp_mac,
                "port": arp_port,
            }

            arp[arp_mac] = arp_dict

        logout = session.post(
            f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-logout",
            verify=False,
        )
        logout.raise_for_status()

        cache_lldp(switch_json, lldp_dict, arp)

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ) as error:
        if return_error:
            raise error

        exception_type = type(error).__name__
        click.secho(
            f"{exception_type} {error} while connecting to {ip}.  Check the entered username, IP address and password.",
            fg="white",
            bg="red",
        )
        return None, None, None
    except decoder.JSONDecodeError:
        click.secho(
            "The switch LLDP query returned successfully, but the result is not valid JSON. "
            "Often this is a faulted web API process on the switch.\n"
            'As an administrator on the switch running: "no web enable" and then "web enable" may repair the problem.\n'
            "Otherwise create a ticket for administrators.",
            fg="red",
        )
        sys.exit(1)

    return switch_json, lldp_dict, arp


def cache_lldp(switch_info, lldp_dict, arp):
    """Format LLDP info and cache it.

    Args:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary
    """
    switch = {
        "ip_address": switch_info["ip"],
        "cabling": defaultdict(list),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": switch_info["hostname"],
        "platform_name": switch_info["platform_name"],
        "vendor": switch_info["vendor"],
    }

    for port_number, port in lldp_dict.items():

        for index, _entry in enumerate(port):
            arp_list = []
            if port[index]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == port[index]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)
            neighbor_description = (
                f"{port[index]['chassis_description'][:54]} {str(arp_list)}"
            )
            port_info = {
                "neighbor": port[index]["chassis_name"],
                "neighbor_description": neighbor_description,
                "neighbor_port": port[index]["port_id"],
                "neighbor_port_description": re.sub(
                    r"(Interface\s+[0-9]+ as )",
                    "",
                    port[index]["port_description"],
                ),
                "neighbor_chassis_id": port[index]["chassis_id"],
            }

            switch["cabling"][port_number].append(port_info)
    switch["cabling"] = dict(switch["cabling"])
    cache_switch(switch)


def print_lldp(switch_info, lldp_dict, arp, out="-"):
    """Print summary of the switch LLDP data.

    Args:
        switch_info: Dictionary with switch platform_name, hostname and IP address
        lldp_dict: Dictionary with LLDP information
        arp: ARP dictionary
        out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 150
    heading = [
        "PORT",
        "",
        "NEIGHBOR",
        "NEIGHBOR PORT",
        "PORT DESCRIPTION",
        "DESCRIPTION",
    ]

    table = []
    for port_number, port in lldp_dict.items():
        for index, _entry in enumerate(port):

            # If the device cannot be discovered by lldp, look it up in the ARP.
            arp_list = []
            if port[index]["chassis_name"] == "":
                arp_list = [
                    f"{arp[mac]['ip_address']}:{list(arp[mac]['port'])[0]}"
                    for mac in arp
                    if arp[mac]["mac"] == port[index]["mac_addr"]
                ]
            arp_list = ", ".join(arp_list)
            description = port[index]["port_description"]
            if description == port[index]["port_id"]:
                neighbor_port = port[index]["port_id"]
                neighbor_description = ""
            else:
                neighbor_port = port[index]["port_id"]
                neighbor_description = re.sub(
                    r"(Interface\s+[0-9]+ as )",
                    "",
                    description,
                )
            if len(arp_list) > 0 and neighbor_description == "":
                neighbor_description = "No LLDP data, check ARP vlan info."
            duplicate = False
            if len(lldp_dict[port_number]) > 1:
                duplicate = True

            table.append(
                [
                    port_number,
                    port[index]["chassis_name"],
                    neighbor_port,
                    neighbor_description,
                    port[index]["chassis_description"][:54] + str(arp_list),
                    port[index]["port_id_subtype"],
                    duplicate,
                ],
            )

    click.secho(
        f"Switch: {switch_info['hostname']} ({switch_info['ip']})                       ",
        fg="bright_white",
        file=out,
    )
    click.secho(
        f"{switch_info['vendor'].capitalize()} {switch_info['platform_name']}",
        fg="bright_white",
        file=out,
    )

    click.echo(dash, file=out)
    click.echo(
        "{:<7s}{:^5s}{:<15s}{:<19s}{:<54s}{}".format(
            heading[0],
            heading[1],
            heading[2],
            heading[3],
            heading[4],
            heading[5],
        ),
        file=out,
    )
    click.echo(dash, file=out)

    for i, _value in enumerate(table):
        row = table[i]
        text_color = ""
        if row[5] == "if_name":
            text_color = "green"
        elif "ncn" in row[1]:
            text_color = "blue"
        if row[6] is True:
            text_color = "bright_white"

        click.secho(
            "{:<7s}{:^5s}{:<15s}{:<19s}{:<54s}{}".format(
                row[0],
                "==>",
                row[1],
                row[2],
                row[3],
                row[4],
            ),
            fg=text_color,
            file=out,
        )
    click.echo("\n")
