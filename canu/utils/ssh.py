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
"""CANU ssh utils."""

from netmiko import ConnectHandler

device = {
    "aruba": "aruba_os",
    "dell": "dell_os10",
    "mellanox": "mellanox_mlnxos",
    "autodetect": "autodetect",
}


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
    switch = {
        "device_type": device[device_type],
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
    switch = {
        "device_type": device[device_type],
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
    }
    output = []
    with ConnectHandler(**switch) as net_connect:
        net_connect.enable()
        for command in commands:
            command_output = net_connect.send_command(command, read_timeout=60)
            output.append(command_output)
        net_connect.disconnect()

    return output
