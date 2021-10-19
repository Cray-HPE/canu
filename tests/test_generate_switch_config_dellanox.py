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
"""Test CANU generate switch config commands."""
import json
from os import path
from pathlib import Path

from click import testing
import requests
import responses

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent

test_file_name = "Full_Architecture_Golden_Config_dellanox.xlsx"
test_file = path.join(test_file_directory, "data", test_file_name)
override_file_name = "override.yaml"
override_file = path.join(test_file_directory, "data", override_file_name)
architecture = "full"
tabs = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners = "J14,T30,J14,T48,J14,T28,J14,T27"
sls_file = "sls_file.json"
shasta = "1.4"
switch_name = "sw-spine-001"
cache_minutes = 0
sls_address = "api-gw-service-nmn.local"

runner = testing.CliRunner()

sls_input = {
    "Networks": {
        "CAN": {
            "Name": "CAN",
            "ExtraProperties": {
                "CIDR": "192.168.11.0/24",
                "Subnets": [
                    {
                        "Name": "bootstrap_dhcp",
                        "CIDR": "192.168.11.0/24",
                        "IPReservations": [
                            {"Name": "can-switch-1", "IPAddress": "192.168.11.2"},
                            {"Name": "can-switch-2", "IPAddress": "192.168.11.3"},
                        ],
                        "VlanID": 7,
                        "Gateway": "192.168.11.1",
                    },
                ],
            },
        },
        "HMN": {
            "Name": "HMN",
            "ExtraProperties": {
                "CIDR": "192.168.0.0/17",
                "Subnets": [
                    {
                        "Name": "network_hardware",
                        "CIDR": "192.168.0.0/17",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.0.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.0.3"},
                            {"Name": "sw-agg-001", "IPAddress": "192.168.0.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.0.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.0.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.0.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.0.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.0.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.0.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.0.15"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.0.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.0.17"},
                        ],
                        "VlanID": 4,
                        "Gateway": "192.168.0.1",
                    },
                ],
            },
        },
        "MTL": {
            "Name": "MTL",
            "ExtraProperties": {
                "CIDR": "192.168.1.0/16",
                "Subnets": [
                    {
                        "Name": "network_hardware",
                        "CIDR": "192.168.1.0/16",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.1.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.1.3"},
                            {"Name": "sw-agg-001", "IPAddress": "192.168.1.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.1.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.1.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.1.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.1.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.1.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.1.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.1.15"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.1.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.1.17"},
                        ],
                        "VlanID": 0,
                        "Gateway": "192.168.1.1",
                    },
                ],
            },
        },
        "NMN": {
            "Name": "NMN",
            "FullName": "Node Management Network",
            "ExtraProperties": {
                "CIDR": "192.168.3.0/17",
                "Subnets": [
                    {
                        "FullName": "NMN Management Network Infrastructure",
                        "CIDR": "192.168.3.0/17",
                        "IPReservations": [
                            {"Name": "sw-spine-001", "IPAddress": "192.168.3.2"},
                            {"Name": "sw-spine-002", "IPAddress": "192.168.3.3"},
                            {"Name": "sw-agg-001", "IPAddress": "192.168.3.4"},
                            {"Name": "sw-agg-002", "IPAddress": "192.168.3.5"},
                            {"Name": "sw-agg-003", "IPAddress": "192.168.3.6"},
                            {"Name": "sw-agg-004", "IPAddress": "192.168.3.7"},
                            {"Name": "sw-leaf-001", "IPAddress": "192.168.3.12"},
                            {"Name": "sw-leaf-002", "IPAddress": "192.168.3.13"},
                            {"Name": "sw-leaf-003", "IPAddress": "192.168.3.14"},
                            {"Name": "sw-leaf-004", "IPAddress": "192.168.3.15"},
                            {"Name": "sw-cdu-001", "IPAddress": "192.168.3.16"},
                            {"Name": "sw-cdu-002", "IPAddress": "192.168.3.17"},
                        ],
                        "Name": "network_hardware",
                        "VlanID": 2,
                        "Gateway": "192.168.3.1",
                    },
                    {
                        "FullName": "NMN Bootstrap DHCP Subnet",
                        "CIDR": "192.168.4.0/17",
                        "IPReservations": [
                            {"Name": "ncn-w001", "IPAddress": "192.168.4.4"},
                            {"Name": "ncn-w002", "IPAddress": "192.168.4.5"},
                            {"Name": "ncn-w003", "IPAddress": "192.168.4.6"},
                        ],
                        "Name": "bootstrap_dhcp",
                        "VlanID": 2,
                        "Gateway": "192.168.3.1",
                    },
                ],
            },
        },
        "NMN_MTN": {
            "Name": "NMN_MTN",
            "ExtraProperties": {
                "CIDR": "192.168.100.0/17",
                "Subnets": [
                    {
                        "FullName": "",
                        "CIDR": "192.168.100.0/22",
                        "Name": "cabinet_3002",
                        "VlanID": 2000,
                        "Gateway": "192.168.100.1",
                        "DHCPStart": "192.168.100.10",
                        "DHCPEnd": "192.168.3.254",
                    },
                ],
            },
        },
        "HMN_MTN": {
            "Name": "HMN_MTN",
            "ExtraProperties": {
                "CIDR": "192.168.200.0/17",
                "Subnets": [
                    {
                        "FullName": "",
                        "CIDR": "192.168.104.0/22",
                        "Name": "cabinet_3002",
                        "VlanID": 3000,
                        "Gateway": "192.168.104.1",
                        "DHCPStart": "192.168.104.10",
                        "DHCPEnd": "192.168.104.254",
                    },
                ],
            },
        },
    },
}
sls_networks = [
    network[x] for network in [sls_input.get("Networks", {})] for x in network
]
