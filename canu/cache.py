# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
"""Utilities to help CANU cache switch information to YAML."""

import datetime
from operator import itemgetter
from os import path
import sys

import ruamel.yaml


yaml = ruamel.yaml.YAML()

# To get the canu_cache.yaml file
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    parent_directory = sys._MEIPASS
else:
    parent_directory = path.abspath(path.dirname(path.dirname(__file__)))

canu_cache_file = path.join(parent_directory, "canu", "canu_cache.yaml")
canu_version_file = path.join(parent_directory, ".version")

file_exists = path.isfile(canu_cache_file)

# Open the Cache file, and generate it if it does not exist
if file_exists:  # pragma: no cover
    with open(canu_cache_file, "r+") as file:
        canu_cache = yaml.load(file)
    if canu_cache is None:
        with open(canu_version_file, "r") as version_file:
            version = version_file.read().replace("\n", "")

        with open(canu_cache_file, "w+") as f:
            f.write(f"version: {version}\n")
            f.write("switches:\n")

        with open(canu_cache_file, "r+") as file:
            canu_cache = yaml.load(file)
else:  # pragma: no cover
    with open(canu_version_file, "r") as version_file:
        version = version_file.read().replace("\n", "")

    with open(canu_cache_file, "w+") as f:
        f.write(f"version: {version}\n")
        f.write("switches:\n")

    with open(canu_cache_file, "r+") as file:
        canu_cache = yaml.load(file)


def cache_switch(switch):
    """Cache a switch.

    The switch that is passed in will either be added to the cache, or updated in the cache, depending on if it existed before.

    Args:
        switch: The JSON switch object to be added to the cache.

    The updated cache is immediately written to a file.
    """
    if ip_exists_in_cache(switch["ip_address"]):
        updated_cache = update_switch_in_cache(canu_cache, switch)
    else:
        updated_cache = add_switch_to_cache(canu_cache, switch)

    with open(canu_cache_file, "w") as f:
        yaml.dump(updated_cache, f)


def firmware_cached_recently(ip, max_cache_time=10):
    """Check if a switch has recently been cached and return True or False.

    Args:
        ip: The IPv4 address to check in the cache.
        max_cache_time: Optional parameter (defaults to 10) to determine the maximum cache time in minutes.

    Returns:
        True or False depending on if the IP address has been cached less than the max_cache_time parameter.
    """
    if ip_exists_in_cache(ip):
        index = list(map(itemgetter("ip_address"), canu_cache["switches"])).index(ip)
        time_now = datetime.datetime.now()

        cache_time = datetime.datetime.strptime(
            canu_cache["switches"][index]["updated_at"],
            "%Y-%m-%d %H:%M:%S",
        )

        time_difference = time_now - cache_time
        time_difference_minutes = time_difference.total_seconds() / 60

        # If cached recently the firmware, platform_name, and hostname keys exist
        if time_difference_minutes < max_cache_time and canu_cache["switches"][
            index
        ].keys() >= {"firmware", "platform_name", "hostname"}:
            return True

    return False


def get_switch_from_cache(ip):
    """Return an existing switch from the cache by IP lookup.

    Args:
        ip: The IPv4 address of the switch to be retrieved from the cache.

    Returns:
        The JSON switch from the cache.

    Raises:
        Exception: If ip address not in cache.
    """
    if ip_exists_in_cache(str(ip)):
        index = list(map(itemgetter("ip_address"), canu_cache["switches"])).index(ip)
        return canu_cache["switches"][index]
    else:
        raise Exception(f"IP address {ip} not in cache.")


def update_switch_in_cache(cache, switch):
    """Update an existing switch in the cache.

    Args:
        cache: The JSON representation of the current YAML cache file.
        switch: The JSON switch object to be added to the cache.

    Returns:
        The updated JSON cache with the switch updated.
    """
    index = list(map(itemgetter("ip_address"), cache["switches"])).index(
        switch["ip_address"],
    )
    for attribute in switch:
        cache["switches"][index].update({attribute: switch[attribute]})

    return cache


def add_switch_to_cache(cache, switch):
    """Add a switch to the cache.

    Args:
        cache: The JSON representation of the current YAML cache file.
        switch: The JSON switch object to be added to the cache.

    Returns:
        The updated JSON cache with the switch appended
    """
    # If there are no switches yet in the cache
    if cache["switches"] is None:  # pragma: no cover
        cache["switches"] = [switch]
    else:
        cache["switches"].append(switch)

    return cache


def remove_switch_from_cache(ip):
    """Remove a switch from the cache.

    This function is useful for removing a test switch from the cache.

    Args:
        ip: The IPv4 address to remove from the cache.

    Returns:
        The updated JSON cache with the switch appended
    """
    try:
        index = list(map(itemgetter("ip_address"), canu_cache["switches"])).index(ip)

        updated_cache = canu_cache
        updated_cache["switches"].pop(index)

        with open(canu_cache_file, "w") as f:
            yaml.dump(updated_cache, f)
    except ValueError:
        print(f"{ip} not in cache")
    return


def ip_exists_in_cache(ip):
    """Check if a switch already exists in the cache.

    Args:
        ip: The IPv4 address to check.

    Returns:
        True or False depending on if the IP address is in the cache.
    """
    if canu_cache["switches"] is not None and str(ip) in map(
        itemgetter("ip_address"),
        canu_cache["switches"],
    ):
        return True
    return False
