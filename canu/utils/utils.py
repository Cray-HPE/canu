"""CANU utils."""
import datetime
import re

import click
from netmiko import ConnectHandler, ssh_exception, SSHDetect
import requests

from canu.cache import (
    cache_switch,
    get_switch_from_cache,
)


def switch_vendor(
    ip,
    credentials,
    return_error=False,
):
    """Get a switch vendor. First try lookup from cache, then from the switch.

    Args:
        ip: Switch ip
        credentials: Switch credentials
        return_error: If True, raises requests exceptions, if False prints error and returns None

    Returns:
        vendor: The switch vendor.

    Raises:
        timeout: Bad IP address.
        auth_err: Bad credentials
        Exception: Unknown error
        NetmikoTimeoutException: Could not determine switch vendor
    """
    # Check if switch in cache
    try:
        cached_switch = get_switch_from_cache(str(ip))
        vendor = cached_switch["vendor"]

        if vendor is not None:
            return vendor

    # Switch not in cache
    except Exception:
        vendor = None

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
                ip, credentials, "show version", "autodetect"
            )

            aruba_match = re.search(r"ArubaOS", remote_version)
            dell_match = re.search(r"Dell EMC Networking", remote_version)
            mellanox_match = re.search(r"Mellanox", remote_version)

            if aruba_match:
                vendor = "aruba"
            if dell_match:
                vendor = "dell"
            if mellanox_match:
                vendor = "mellanox"
            # Could not determine switch vendor
            else:
                if return_error:
                    raise ssh_exception.NetmikoTimeoutException
                return None

        # Put vendor in cache
        switch_cache = {
            "ip_address": ip,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vendor": vendor,
        }

        cache_switch(switch_cache)
    except ssh_exception.NetmikoTimeoutException as timeout:
        if return_error:
            raise timeout
        else:
            click.secho(
                f"Timeout error connecting to switch {ip}, check the IP address and try again.",
                fg="white",
                bg="red",
            )
            return None
    except ssh_exception.NetmikoAuthenticationException as auth_err:
        if return_error:
            raise auth_err
        click.secho(
            f"Authentication error connecting to switch {ip}, check the credentials or IP address and try again.",
            fg="white",
            bg="red",
        )
        return None
    except Exception as error:  # pragma: no cover
        if return_error:
            raise error
        exception_type = type(error).__name__

        click.secho(
            f"{exception_type} {error}",
            fg="white",
            bg="red",
        )
        return None
    return vendor


def check_aruba(ip, credentials):
    """Check if a switch is an Aruba and cache the vendor if it is.

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
            f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
        )
        login.raise_for_status()
        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

        # Put vendor in cache
        switch_cache = {
            "ip_address": ip,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vendor": "aruba",
        }

        cache_switch(switch_cache)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    else:
        return True


def check_dell(ip, credentials):
    """Check if a switch is a Dell and cache the vendor if it is.

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

        # Put vendor in cache
        switch_cache = {
            "ip_address": ip,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vendor": "dell",
        }

        cache_switch(switch_cache)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    else:
        return True


def check_mellanox(ip, credentials):
    """Check if a switch is a Mellanox and cache the vendor if it is.

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

        # Put vendor in cache
        switch_cache = {
            "ip_address": ip,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vendor": "mellanox",
        }

        cache_switch(switch_cache)
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
    ):
        return False

    else:
        return True


def netmiko_command(ip, credentials, command, device_type="autodetect"):
    """Send a single command to a switch using netmiko.

    Args:
        ip: Switch ip
        credentials: Switch credentials
        command: Command to be run on the switch
        device_type: The switch type

    Returns:
        output: Text output from the command run.
    """
    type = {
        "aruba": "aruba_os",
        "dell": "dell_os10",
        "mellanox": "mellanox_mlnxos",
        "autodetect": "autodetect",
    }
    switch = {
        "device_type": type[device_type],
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
    }

    with ConnectHandler(**switch) as net_connect:
        output = net_connect.send_command(command)
        net_connect.disconnect()

    return output


def netmiko_commands(ip, credentials, commands, device_type="autodetect"):
    """Send a list of commands to a switch using netmiko.

    Args:
        ip: Switch ip
        credentials: Switch credentials
        commands: List of commands to be run on the switch
        device_type: The switch type

    Returns:
        output: Text output from the command run.
    """
    type = {
        "aruba": "aruba_os",
        "dell": "dell_os10",
        "mellanox": "mellanox_mlnxos",
        "autodetect": "autodetect",
    }
    switch = {
        "device_type": type[device_type],
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
        "session_log": "netmiko_session.log",
    }
    output = []
    with ConnectHandler(**switch) as net_connect:
        net_connect.enable()
        for command in commands:
            command_output = net_connect.send_command(command)
            output.append(command_output)
        net_connect.disconnect()

    return output
