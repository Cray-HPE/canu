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
"""heuristic_loookups: Table of educated guesses about normal configurations."""

# TODO add more Dell, Mellanox, Gigabyte and Intel heuristics
heuristic_lookup = {
    "14:02:ec": {
        "sw-spine-0": {
            "hint": "OCP Port",
            "port": "ocp:[12]",
        },
        "leaf-0": {
            "hint": "OCP Port",
            "port": "ocp:[12]",
        },
    },
    "94:40:c9": {
        "sw-spine-0": {
            "hint": "PCIe Port",
            "port": "pcie:[12]",
        },
        "leaf-0": {
            "hint": "PCIe Port",
            "port": "pcie:[12]",
        },
        "leaf-bmc-0": {
            "hint": "iLO Port",
            "port": "bmc:1",
        },
    },
    "ec:eb:b8": {
        "leaf-bmc-0": {
            "hint": "PDU",
            "port": "bmc:1",
        },
    },
    "b4:2e:99": {
        "leaf-bmc-0": {
            "hint": "River Compute",
            "port": "onboard:1",
        },
    },
    "00:40:a6": {
        "leaf-bmc-0": {
            "hint": "Slingshot Switch",
            "port": "mgmt:1",
        },
    },
}
