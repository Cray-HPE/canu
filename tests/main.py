from netmiko import ConnectHandler

def get_running_version(driver, host, username="admin", password="admin"):
    with ConnectHandler(
        device_type=driver,
        host=host,
        username=username,
        password=password
    ) as device:
        version = device.send_command("show version", use_textfsm=True)
    return version[0]["version"]