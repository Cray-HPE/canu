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
            command_output = net_connect.send_command(command)
            output.append(command_output)
        net_connect.disconnect()

    return output
