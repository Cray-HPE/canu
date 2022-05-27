
from netmiko import ConnectHandler
import requests

def get_running_version(driver, host, username="admin", password="admin"):
    device = requests.get(
        device_type=driver,
        host=host,
        username=username,
        password=password
    )
    version = device.send_command("show version", use_textfsm=False)
    return version[0]["version"]