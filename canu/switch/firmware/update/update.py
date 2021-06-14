"""CANU commands that update the firmware of an individual switch."""
# import datetime
import json

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

# import emoji
from netmiko import ConnectHandler
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import urllib3

# from canu.cache import cache_switch, firmware_cached_recently, get_switch_from_cache

# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
1. Copy running-config into startup-config
PUT "https://192.0.2.5/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config"
2. Check how switch currently boots (Primary or Secondary)
    X2. Copy primary firmware version into secondary version.
3. Upload new firmware to OPPOSITE of current boot
4. Persist boot ot OPPOSITE of current
4. Reboot
5. Test


"""


# NO ? Do we need to be able to downgrade firmware?
# ? Do we copy the current firmware and config to secondary?
# Warn that the secondary config will be overwritten


# Make a backup of the config and image first
# If the upgrade is significant, might want to do incremental

# Determine where the firmware image is located?
# - in Artifactory?:
# http://172.29.30.61/artifactory/list/integration-firmware/aruba/
# How to determine it is the proper firmware in the folder?
# - In canu?

# POST the firmware image as the secondary image
# https://stash.us.cray.com/projects/CASMNET/repos/network_troubleshooting/browse/aruba/aruba_version.py
# line 45: session.put(f'https://{ip_add}/rest/v10.04/firmware?image=secondary&from=http%3A%2F%2F172.29.30.61%2Fartifactory%2Flist%2Fintegration-firmware%2Faruba%2FArubaOS-CX_6400-6300_10_05_0020.swi&vrf=default', verify=False)
# http://172.29.30.61/artifactory/list/integration-firmware/aruba/
# PDF says:
# $ curl --noproxy -k -b /tmp/auth_cookie \
# -H 'Content-Type: application/json' \
# -H 'Accept: application/json' \
# -F "fileupload=@/myfirmwarefiles/myswitchfirmware_2020020905.swi" \ https://192.0.2.5/rest/v1/firmware?image=secondary

# Then boot to the secondary image
# POST "https://192.0.2.5/rest/v1/boot?image=secondary"
# $ curl --noproxy -k -X POST -b /tmp/auth_cookie \ -H 'Content-Type: application/json' \
# -H 'Accept: application/json' \ "https://192.0.2.5/rest/v1/boot?image=secondary"


# curl --noproxy -k -b /tmp/auth_cookie -X PUT --header 'Content-Type: application/json' --header 'Accept: application/json' 'https://192.168.1.60/rest/v10.04/firmware?image=primary&from=secondary'

# curl -k -b /tmp/auth_cookie \
# -H 'Content-Type: application/json' \
# -H 'Accept: application/json' \
# -F "fileupload=@/ArubaOS-CX_8360_10_06_0010.stable.swi" \
# https://192.168.1.60/rest/v1/firmware?image=secondary


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@optgroup.group(
    "Firmware image input sources",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--image-local",
    help="Local file",
    # type=click.File("r"),
)
@optgroup.option(
    "--image-remote",
    help="Server address of the firmware",
)
@click.option("--ip", required=True, help="The IP address of the switch")
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
# @click.option("--json", "json_", is_flag=True, help="Output JSON")
# @click.option("--verbose", is_flag=True, help="Verbose mode")
# @click.option(
#     "--out", help="Output results to a file", type=click.File("w"), default="-"
# )
@click.pass_context
def update(ctx, image_local, image_remote, username, ip, password):
    r"""Report the firmware of an Aruba switch (API v10.04) on the network."""
    # command = "show ip route"
    credentials = {"username": username, "password": password}
    # send_command(ip, credentials, command)
    session = requests.Session()
    login = session.post(
        f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
    )
    print("login:", login)
    # running_config_to_startup_config(ip, session)
    image_dir = [image_local, image_remote]
    print("image_dir", image_dir)

    # Write Memory
    session.put(
        f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
        verify=False,
    )

    # update_firmware(ip, session, "primary", image_dir)
    # reboot_switch(ip, credentials, "primary")
    # if image_local:
    # Logout
    netmiko_test(ip, credentials)
    session.post(f"https://{ip}/rest/v10.04/logout", verify=False)


def netmiko_test(ip, credentials):
    # command = "show ip route"
    # command = "show interfaces brief"
    # command = "show interfaces config"
    # command = "show interfaces display"

    command1 = "show version"
    # command2 = "show flash"
    command2 = "show running-config"
    # aruba_os
    # aruba_osswitch
    aruba1 = {
        "device_type": "aruba_osswitch",
        "host": ip,
        "username": credentials["username"],
        "password": credentials["password"],
    }

    # net_connect = ConnectHandler(**aruba1)
    print("attempting to connect...")
    with ConnectHandler(**aruba1) as net_connect:
        output1 = net_connect.send_command(command1)
        print("output1")
        print(output1)
        if "Active Image : primary" in str(output1):
            click.secho("PRIMARY", fg="green")
        elif "Active Image : secondary" in str(output1):
            click.secho("SECONDARY", fg="green")
        output2 = net_connect.send_command(command2)
        print("output2")
        print(output2)
        net_connect.disconnect()


def running_config_to_startup_config(ip, session):
    # session = requests.Session()
    # Login
    # login = session.post(
    #     f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
    # )
    # login.raise_for_status()

    response = session.put(
        f"https://{ip}/rest/v10.04/fullconfigs/startup-config?from=/rest/v10.04/fullconfigs/running-config",
        verify=False,
    )
    # response.raise_for_status()
    print("response", response)
    print("response.text", response.text)
    # Logout
    # session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

    return


def reboot_switch(ip, credentials, image):
    if image not in ["primary", "secondary"]:
        print("NO NO NO NO")
        return
        # Login
    session = requests.Session()

    login = session.post(
        f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
    )
    # login.raise_for_status()

    response = session.post(
        f"https://{ip}/rest/v10.04/boot?image={image}",
        verify=False,
    )
    # response.raise_for_status()
    print("response", response)
    print("response.text", response.text)
    switch_boot = response.json()
    print("switch_boot", switch_boot)


def update_firmware(ip, session, image, image_dir):
    # When I send data = files -> 413 Request Entity Too Large

    # If the image comes from a local file
    # session = requests.Session()
    if image_dir[0]:
        # try:

        #     print("login")
        #     # login = session.post(
        #     #     f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
        #     # )
        #     # files = {"file": ("aaa.csv", open("aaa.csv", "rb"), "*/*")}
        #     # files = {"file": file_}
        #     files = {"file": open(image_dir[0], "rb")}

        #     print("upload firmware")
        #     m = MultipartEncoder(fields={"file": open(image_dir[0], "rb")})
        #     headers = {
        #         # "Content-Type": "application/json",
        #         # "Accept": "application/json",
        #         "Accept": "text/plain",
        #         # "Content-Type": "multipart/form-data",
        #         "Content-Type": m.content_type,
        #         "type": "formData",
        #     }
        #     # print("m.content_type", m.content_type)
        #     response = session.post(
        #         f"https://{ip}/rest/v10.04/firmware?image={image}",
        #         headers=headers,
        #         # files=files,
        #         data=m,
        #         # files=m,
        #         # data=files,
        #         # files=files,
        #         # data=image_dir[0],
        #         # headers={"Content-Type": m.content_type},
        #         verify=False,
        #     )
        #     # response = requests.post(url=URL, data=params, auth=(USER, PASSWORD),
        #     #                             files={"file": file_}, verify=False)
        # except TimeoutError:
        #     print("Connection timed out!")
        # else:
        #     print(response)
        #     #

        #     print("response", response)
        #     print("response.text", response.text)
        #     print("response.reason", response.reason)
        #     print("response.links", response.links)
        #     # print("response.Response()", response.Response())
        #     print("response.content", response.content)
        #     print("response.encoding", response.encoding)
        #     print("response.headers", response.headers)
        #     print("response.history", response.history)

        with open(image_dir[0], "rb") as file_:
            # try:

            m = MultipartEncoder(fields={"file": file_})
            headers = {
                "Content-Type": "multipart/form-data",
                # "Content-Type": m.content_type,
                # "Content-Type": "application/json",
                # "Accept": "application/json",
                "Accept": "text/plain",
                "type": "formData",
            }
            print("login")
            # login = session.post(
            #     f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
            # )
            # files = {"file": ("aaa.csv", open("aaa.csv", "rb"), "*/*")}
            files = {"file": file_}
            print("upload firmware")
            response = session.post(
                f"https://{ip}/rest/v10.04/firmware?image={image}",
                headers=headers,
                data=m,
                # files=files,
                # data=files,
                # files=files,
                # data=image_dir[0],
                verify=False,
            )
            # response = requests.post(url=URL, data=params, auth=(USER, PASSWORD),
            #                             files={"file": file_}, verify=False)
            print(response)

            print("response", response)
            print("response.text", response.text)
            print("response.reason", response.reason)
            print("response.links", response.links)
            # print("response.Response()", response.Response())
            print("response.content", response.content)
            print("response.encoding", response.encoding)
            print("response.headers", response.headers)
            print("response.history", response.history)
            # except TimeoutError:
            #     print("Connection timed out!")
            # else:

        pass
    # If the image comes from a remote directory
    else:
        print("else")
        # login = session.post(
        #     f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
        # )
        print(
            "url",
            f"https://{ip}/rest/v10.04/firmware?image={image}&from={image_dir[1]}&vrf=default",
        )
        response = session.put(
            f"https://{ip}/rest/v10.04/firmware?image={image}&from={image_dir[1]}&vrf=default",
            verify=False,
        )

        print("response", response)
        print("response.text", response.text)
        print("response.reason", response.reason)
        print("response.links", response.links)
        print("response.content", response.content)
        print("response.encoding", response.encoding)
        print("response.headers", response.headers)
        print("response.history", response.history)

        pass

    # After updating boot to the new firmware
    # reboot_switch(ip, credentials, image)
    pass


def send_command(ip, credentials, command):
    c = {"cmd": command}
    session = requests.Session()
    # Login
    login = session.post(
        f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
    )
    # login.raise_for_status()

    # GET firmware version
    response = session.post(
        f"https://{ip}/rest/v10.04/cli", data=json.dumps(c), verify=False
    )
    # response.raise_for_status()
    print("response", response)
    print("response.text", response.text)

    # switch_firmware = response.json()

    # print("switch_firmware", switch_firmware)

    # Logout
    session.post(f"https://{ip}/rest/v10.04/logout", verify=False)


# Good error message!
# curl: (3) URL using bad/illegal format or missing URL
# Firmware Image is invalid. Please enter a valid firmware image.
# curl -X POST --header 'Content-Type: multipart/form-data' --header 'Accept: text/plain' {"type":"formData"} 'https://192.168.1.60/rest/v1/firmware?image=primary' -k --cookie "cookies.txt" --cookie-jar "cookies.txt" -F "fileupload=@/Users/brooks/repos/canu/ArubaOS-CX_8360_10_06_0010.stable.swi"
