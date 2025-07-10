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
"""Test CANU validate shcd-cabling commands."""
import unittest

import canu.validate.network.cabling.cabling as cabling

# Click commands do not expose their functions as attributes, so we need to
# import directly and bypass the click command structure.  This is akin to a
# regular unit test one might like to write.


class TestValidateShcdCablingFormatDstName(unittest.TestCase):
    """Unit tests for CANU validate shcd-cabling format_dst_name command."""

    def test_format_switch_dst_name(self):
        """Test the format_switch_dst_name function."""
        # Test case 1: Name starts with "sw-" and has a string with multiple digits
        dst_name = "sw-spine01"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-spine-001"
        self.assertEqual(result, expected_result)

        # Test case 2: Name starts with "sw-" has a string in the middle, followed by a dash and multiple digits
        dst_name = "sw-spine-002"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-spine-002"
        self.assertEqual(result, expected_result)

        # Test case 3: Name starts with "sw-" has a string in the middle, followed by a two dashes and multiple digits
        dst_name = "sw-leaf--bmc99"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-leaf-bmc-099"
        self.assertEqual(result, expected_result)

        # Test case 4: Name starts with "sw-" and has a string with multiple digits
        dst_name = "sw-smn04"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-smn-004"
        self.assertEqual(result, expected_result)

        # Test case 5: Name starts with "sw-" and has a string with multiple digits but has a trailing dash
        dst_name = "sw-25g06-"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-25g-006"
        self.assertEqual(result, expected_result)

        # Test case 6: Name starts with "sw-" and has a string that starts with digits but ends with all digits
        dst_name = "sw-100g01"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-100g-001"
        self.assertEqual(result, expected_result)

        # Test case 7: Name does not start with "sw-" and has only non-digit characters
        dst_name = "sw---=%$)"
        with self.assertRaises(cabling.FormatSwitchDestinationNameError):
            cabling.format_switch_dst_name(dst_name)

        # Test case 11: Name starts with "sw-" but has no digits
        dst_name = "sw-leaf"
        with self.assertRaises(cabling.FormatSwitchDestinationNameError):
            cabling.format_switch_dst_name(dst_name)

        # Test case 12: Name starts with "sw-" and has leaf-bmc and multiple digits
        dst_name = "sw-leaf-bmc99"
        result = cabling.format_switch_dst_name(dst_name)
        expected_result = "sw-leaf-bmc-099"
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
