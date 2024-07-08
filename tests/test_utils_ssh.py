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
"""Test CANU validate shcd-cabling commands."""
import unittest
from unittest.mock import patch, MagicMock

from canu.utils.ssh import netmiko_command, netmiko_commands

class TestNetmikoCommand(unittest.TestCase):
    @patch('canu.utils.ssh.ConnectHandler')
    def test_netmiko_command(self, MockConnectHandler):
        """Test that the netmiko command is called with the correct arguments."""
        # Create a mock ConnectHandler instance
        mock_connection = MockConnectHandler.return_value
        mock_connection.send_command.return_value = 'output from switch'
        
        # Set the __enter__ method to return the mock_connection
        # this is needed because the ConnectHandler is used as a context manager
        MockConnectHandler.return_value.__enter__.return_value = mock_connection

        # Define the test parameters
        host = "127.0.0.1"
        credentials = {"username": "username", "password": "password"}
        command = "show mac-address-table"
        device_type = "autodetect"
        
        # Call the function to test
        result = netmiko_command(host, credentials, command, device_type)
        
        # Assert that the ConnectHandler was called with the correct arguments
        MockConnectHandler.assert_called_with(
            device_type=device_type,
            host=host,
            username=credentials["username"],
            password=credentials["password"]
        )

        # Assert that the send_command method was called with the correct command
        mock_connection.send_command.assert_called_with(command)
        
        # Assert that the disconnect method was called once
        mock_connection.disconnect.assert_called_once()

        # Assert that the result matches the expected output
        self.assertEqual(result, 'output from switch')








