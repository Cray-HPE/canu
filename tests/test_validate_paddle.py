# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
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
"""Test CANU validate shcd commands."""
import json
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli

test_file_directory = Path(__file__).resolve().parent
test_file_name = "Full_Architecture_Golden_Config_1.1.5.json"
test_file = path.join(test_file_directory, "data", test_file_name)
cache_minutes = 0
runner = testing.CliRunner()


def test_validate_paddle():
    """Test that the `canu validate paddle` command runs and returns valid cabling."""
    with runner.isolated_filesystem():

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "paddle",
                "--ccj",
                test_file,
            ],
        )
        assert result.exit_code == 0
        assert (
            "CCJ Node Connections\n"
            "------------------------------------------------------------\n"
            "0: sw-spine-001 connects to 11 nodes: [2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 1]\n"
            "1: sw-spine-002 connects to 11 nodes: [2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0]\n"
            "2: sw-leaf-001 connects to 13 nodes: [11, 12, 14, 17, 17, 18, 18, 10, 1, 0, 3, 3, 3]\n"
            "3: sw-leaf-002 connects to 13 nodes: [11, 12, 14, 17, 17, 18, 18, 10, 1, 0, 2, 2, 2]\n"
            "4: sw-leaf-003 connects to 14 nodes: [13, 15, 16, 19, 19, 20, 20, 21, 21, 1, 0, 5, 5, 5]\n"
            "5: sw-leaf-004 connects to 14 nodes: [13, 15, 16, 19, 19, 20, 20, 21, 21, 1, 0, 4, 4, 4]\n"
            "6: sw-cdu-001 connects to 10 nodes: [31, 32, 33, 34, 35, 7, 1, 0, 7, 7]\n"
            "7: sw-cdu-002 connects to 9 nodes: [32, 33, 34, 35, 6, 1, 0, 6, 6]\n"
            "8: sw-edge-001 connects to 2 nodes: [0, 1]\n"
            "9: sw-edge-002 connects to 2 nodes: [0, 1]\n"
            "10: sw-leaf-bmc-001 connects to 27 nodes: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 28, 29, 30, 22, 21, 23, 24, 25, 26, 22, 3, 2]\n"  # noqa: B950
            "11: ncn-m001 connects to 3 nodes: [10, 2, 3]\n"
            "12: ncn-m002 connects to 3 nodes: [10, 2, 3]\n"
            "13: ncn-m003 connects to 3 nodes: [10, 4, 5]\n"
            "14: ncn-w001 connects to 3 nodes: [10, 2, 3]\n"
            "15: ncn-w002 connects to 3 nodes: [10, 4, 5]\n"
            "16: ncn-w003 connects to 3 nodes: [10, 4, 5]\n"
            "17: ncn-s001 connects to 5 nodes: [10, 2, 2, 3, 3]\n"
            "18: ncn-s002 connects to 5 nodes: [10, 2, 2, 3, 3]\n"
            "19: ncn-s003 connects to 5 nodes: [10, 4, 4, 5, 5]\n"
            "20: uan001 connects to 5 nodes: [10, 4, 4, 5, 5]\n"
            "21: lm001 connects to 5 nodes: [10, 4, 4, 5, 5]\n"
            "22: gateway001 connects to 2 nodes: [10, 10]\n"
            "23: cn001 connects to 2 nodes: [10, 10]\n"
            "24: cn002 connects to 2 nodes: [10, 10]\n"
            "25: cn003 connects to 2 nodes: [10, 10]\n"
            "26: cn004 connects to 2 nodes: [10, 10]\n"
            "27: pdu-x3000-000 connects to 1 nodes: [10]\n"
            "28: pdu-x3000-001 connects to 1 nodes: [10]\n"
            "29: pdu-x3001-000 connects to 1 nodes: [10]\n"
            "30: pdu-x3001-001 connects to 1 nodes: [10]\n"
            "31: cec-x3002-000 connects to 1 nodes: [6]\n"
            "32: cmm-x3002-000 connects to 2 nodes: [6, 7]\n"
            "33: cmm-x3002-001 connects to 2 nodes: [6, 7]\n"
            "34: cmm-x3002-002 connects to 2 nodes: [6, 7]\n"
            "35: cmm-x3002-003 connects to 2 nodes: [6, 7]\n"
        ) in str(result.output)


def test_validate_paddle_no_architecture():
    """Test that the `canu validate paddle` command errors on bad architecture."""
    bad_ccj_file = "bad.json"
    with runner.isolated_filesystem():
        with open(bad_ccj_file, "w") as f:
            json.dump(bad_ccj, f)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "paddle",
                "--ccj",
                bad_ccj_file,
            ],
        )
        assert result.exit_code == 0
        assert (
            "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ."
            in str(result.output)
        )


bad_ccj = {
    "canu_version": "0.0.6",
    "shcd_file": "bad_ccj",
    "topology": [
        {
            "common_name": "sw-spine-001",
            "id": 0,
            "architecture": "spine",
            "model": "8325_JL627A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 1,
                    "speed": 100,
                    "slot": None,
                    "destination_node_id": 1,
                    "destination_port": 1,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u10"},
        },
        {
            "common_name": "sw-spine-002",
            "id": 1,
            "architecture": "spine",
            "model": "8325_JL627A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 1,
                    "speed": 100,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 1,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u11"},
        },
    ],
}
