import click
from click_help_colors import HelpColorsCommand
import emoji
import requests
import urllib3


# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
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
@click.option("--json", is_flag=True, help="Output JSON")
@click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
@click.pass_context
def firmware(ctx, username, ip, password, json, verbose):
    """
    The switch FIRMWARE command will report the firmware of
    an Aruba switch using API v10.04 on the network

    There are two different statuses that might be indicated.\n
    🛶 - Pass: Indicates that the switch passed the firmware verification.\n
    ❌ - Fail: Indicates that the switch failed the firmware verification. A list of expected firmware versions will be displayed.\n
    """
    if ctx.obj["shasta"]:
        shasta = ctx.obj["shasta"]
        config = ctx.obj["config"]

    credentials = {"username": username, "password": password}
    switch_firmware, switch_info = get_firmware(ip, credentials)

    if switch_firmware is None:
        return

    # Get the firmware range from the canu.yaml file and the switch info
    firmware_range = config["shasta"][shasta]["aruba"][switch_info["platform_name"]]

    if switch_firmware["current_version"] in firmware_range:
        match_emoji = emoji.emojize(":canoe:")
        firmware_match = True
    else:
        match_emoji = emoji.emojize(":cross_mark:")
        firmware_match = False

    # If the JSON flag is enabled
    if json:
        if verbose:
            click.echo(switch_firmware)
            return switch_firmware
        else:
            click.echo(switch_firmware["current_version"])
            return switch_firmware["current_version"]

    if verbose:
        if firmware_match is True:
            click.secho(
                f"{match_emoji} - Pass - IP: {ip} Hostname:{switch_info['hostname']}",
            )
        else:
            click.secho(
                f"{match_emoji} - Fail - IP: {ip} Hostname:{switch_info['hostname']}",
            )
            click.secho(f"Firmware should be in: {firmware_range}", fg="red")

        click.echo(f"Current Version: {switch_firmware['current_version']}")
        click.echo(f"Primary Version: {switch_firmware['primary_version']}")
        click.echo(f"Secondary Version: {switch_firmware['secondary_version']}")
        click.echo(f"Default Image: {switch_firmware['default_image']}")
        click.echo(f"Booted Image: {switch_firmware['booted_image']}")
    else:
        if firmware_match is True:
            click.echo(
                f"{match_emoji} - Pass - IP: {ip} Hostname:{switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
            )
        if firmware_match is False:
            click.echo(
                f"{match_emoji} - Fail - IP: {ip} Hostname:{switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
            )
            click.secho(f"Firmware should be in: {firmware_range}", fg="red")


def get_firmware(ip, credentials, return_error=False):
    """
    Get the firmware of an Aruba switch using v10.04 API
    :param ip: IPv4 address of the switch
    :param credentials: Dictionary with username and password of the switch
    :return: Dictionary with a switches firmware
    """
    session = requests.Session()
    try:
        # Login
        login = session.post(
            f"https://{ip}/rest/v10.04/login", data=credentials, verify=False
        )
        login.raise_for_status()

    except requests.exceptions.HTTPError as http_error:
        if return_error:
            raise http_error
        else:
            click.secho(
                f"Error connecting to switch {ip}, check that this IP is an Aruba switch, or check the username or password",
                fg="white",
                bg="red",
            )
            return None, None
    except requests.exceptions.ConnectionError as connection_error:
        if return_error:
            raise connection_error
        else:
            click.secho(
                f"Error connecting to switch {ip}, check the IP address and try again",
                fg="white",
                bg="red",
            )
            return None, None
    except requests.exceptions.RequestException as error:  # pragma: no cover
        if return_error:
            raise error
        else:
            click.secho(
                f"Error connecting to switch  {ip}.",
                fg="white",
                bg="red",
            )
            return None, None

    try:
        # GET firmware version
        response = session.get(f"https://{ip}/rest/v10.04/firmware", verify=False)
        response.raise_for_status()

        switch_firmware = response.json()

        # GET switch platform
        response = session.get(
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
            verify=False,
        )
        response.raise_for_status()

        switch_info = response.json()

        # Logout
        session.post(f"https://{ip}/rest/v10.04/logout", verify=False)

        return switch_firmware, switch_info

    except requests.exceptions.RequestException as error:  # pragma: no cover
        if return_error:
            raise error
        else:
            click.secho(
                f"Error getting firmware version from switch {ip}",
                fg="white",
                bg="red",
            )
            return None, None
