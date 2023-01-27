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
"""CANU mac utils."""
from os import path
from pathlib import Path
import sys

from aiohttp import client_exceptions
from mac_vendor_lookup import BaseMacLookup, InvalidMacError, MacLookup

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent

# Mac vendors are stored so they can be looked up even when there is no network connectivity
mac_vendors_file = path.join(project_root, "network_modeling", "mac_vendors")

BaseMacLookup.cache_path = mac_vendors_file
mac = MacLookup()


def find_mac(mac_address):
    """Return the vendor of a mac address.

    Args:
        mac_address: Mac address to be looked up

    Returns:
        String containing the mac vendor name
    """
    try:
        mac_vendor = mac.lookup(str(mac_address))
    except (KeyError, ValueError, InvalidMacError):
        # When the vendor can't be found, send back an empty string
        mac_vendor = ""

    return mac_vendor


def update_mac_vendors():
    """Update the mac address vendor file.

    If the mac vendor file needs to get updated, run this function.
    """
    try:
        mac.update_vendors()  # This can take a few seconds for the download and it will be stored in the new path
    except (
        client_exceptions.ClientConnectorError,
        client_exceptions.ClientPayloadError,
    ):
        pass
