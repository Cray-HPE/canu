# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""CANU vendor utils."""
import re

import click
import requests
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException, SSHDetect

from canu.utils.ssh import netmiko_command


def switch_vendor(
    ip,
    credentials,
    return_error=False,
):
    """Get a switch vendor by detecting it from the switch.

    Args:
        ip: Switch ip
        credentials: Switch credentials
        return_error: If True, raises requests exceptions, if False prints error and returns None

    Returns:
        vendor: The switch vendor.

    Raises:
        Exception: Unknown error
        NetmikoTimeoutException: Timeout error connecting to switch
        NetmikoAuthenticationException: Authentication error connecting to switch
    """
    # First try APIs (fast)
    is_aruba = check_aruba(ip, credentials)
    if is_aruba:
        return "aruba"

    is_dell = check_dell(ip, credentials)
    if is_dell:
        return "dell"

    is_mellanox = check_mellanox(ip, credentials)
    if is_mellanox:
        return "mellanox"

    # Could not determine vendor, Try to autodetect (slow)
    switch = {
        "device_type": "autodetect",
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
    }
    try:
        guesser = SSHDetect(**switch)
        best_match = guesser.autodetect()

        if best_match == "dell_os10":
            vendor = "dell"
        elif best_match == "mellanox_mlnxos":
            vendor = "mellanox"
        elif best_match is None:

            # could not determine, check if Aruba
            remote_version = netmiko_command(
                ip,
                credentials,
                "show version",
                "autodetect",
            )

            aruba_match = re.search("ArubaOS", remote_version)
            dell_match = re.search("Dell EMC Networking", remote_version)
            mellanox_match = re.search("Mellanox", remote_version)

            if aruba_match:
                vendor = "aruba"
            if dell_match:
                vendor = "dell"
            if mellanox_match:
                vendor = "mellanox"
            # Could not determine switch vendor
            else:
                if return_error:
                    raise NetmikoTimeoutException
                return None

        # Vendor detected successfully

    except (
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
        Exception,
    ) as err:
        if return_error:
            raise err

        exception_type = type(err).__name__

        if exception_type == "NetmikoTimeoutException":
            error_message = (
                f"Timeout error connecting to switch {ip}, check the entered username, IP address and password."
            )
        elif exception_type == "NetmikoAuthenticationException":
            error_message = (
                f"Authentication error connecting to switch {ip}, check the credentials or IP address and try again."
            )
        else:
            error_message = f"{exception_type}, {err}."

        click.secho(
            error_message,
            fg="white",
            bg="red",
        )
        return None
    return vendor


def check_aruba(ip, credentials):
    """Check if a switch is an Aruba.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch

    Returns:
        Bool if a switch is an Aruba
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
        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    return True


def check_dell(ip, credentials):
    """Check if a switch is a Dell.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch

    Returns:
        Bool if a switch is a Dell
    """
    session = requests.Session()
    try:
        url = f"https://{ip}/restconf/data/system-sw-state/sw-version/sw-build-version"
        auth = (credentials["username"], credentials["password"])
        response = session.get(url, auth=auth, verify=False)
        response.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    return True


def check_mellanox(ip, credentials):
    """Check if a switch is a Mellanox.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch

    Returns:
        Bool if a switch is a Mellanox
    """
    session = requests.Session()
    try:
        url = f"https://{ip}/admin/launch?script=rh&template=json-request&action=json-login"
        response = session.get(url, json=credentials, verify=False)
        response.raise_for_status()

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    return True
