"""CANU commands that report the firmware of an individual switch."""
import datetime
import json

import click
from click_help_colors import HelpColorsCommand
import emoji
import requests
import urllib3

from canu.cache import cache_switch, firmware_cached_recently, get_switch_from_cache

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
@click.option("--json", "json_", is_flag=True, help="Output JSON")
@click.option("--verbose", is_flag=True, help="Verbose mode")
@click.option(
    "--out", help="Output results to a file", type=click.File("w"), default="-"
)
@click.pass_context
def firmware(ctx, username, ip, password, json_, verbose, out):
    r"""Report the firmware of an Aruba switch (API v10.04) on the network.

    There are two different statuses that might be indicated.\n
    🛶 - Pass: Indicates that the switch passed the firmware verification.\n
    ❌ - Fail: Indicates that the switch failed the firmware verification. A list of expected firmware versions will be displayed.\n
    """
    if ctx.obj["shasta"]:
        shasta = ctx.obj["shasta"]
        config = ctx.obj["config"]
        cache_minutes = ctx.obj["cache_minutes"]

    credentials = {"username": username, "password": password}
    switch_firmware, switch_info = get_firmware(
        ip, credentials, False, cache_minutes=cache_minutes
    )

    if switch_firmware is None:
        return

    # Get the firmware range from the canu.yaml file and the switch info
    firmware_range = config["shasta"][shasta]["aruba"][switch_info["platform_name"]]

    if switch_firmware["current_version"] in firmware_range:
        match_emoji = emoji.emojize(":canoe:")
        firmware_match = "Pass"
    else:
        match_emoji = emoji.emojize(":cross_mark:")
        firmware_match = "Fail"

    # If the JSON flag is enabled
    if json_:
        if verbose:

            json_formatted = json.dumps(
                {
                    "ip_address": ip,
                    "status": firmware_match,
                    "hostname": switch_info["hostname"],
                    "platform_name": switch_info["platform_name"],
                    "firmware": switch_firmware,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                indent=2,
            )
            click.echo(json_formatted, file=out)
            return json_formatted
        else:
            json_formatted = json.dumps(
                {
                    "ip_address": ip,
                    "status": firmware_match,
                    "firmware": switch_firmware["current_version"],
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                indent=2,
            )
            click.echo(json_formatted, file=out)
            return switch_firmware["current_version"]

    if verbose:
        if firmware_match == "Pass":
            click.secho(
                f"{match_emoji} - Pass - IP: {ip} Hostname:{switch_info['hostname']}",
                file=out,
            )
        else:
            click.secho(
                f"{match_emoji} - Fail - IP: {ip} Hostname:{switch_info['hostname']}",
                file=out,
            )
            click.secho(f"Firmware should be in: {firmware_range}", fg="red", file=out)

        click.echo(f"Current Version: {switch_firmware['current_version']}", file=out)
        click.echo(f"Primary Version: {switch_firmware['primary_version']}", file=out)
        click.echo(
            f"Secondary Version: {switch_firmware['secondary_version']}", file=out
        )
        click.echo(f"Default Image: {switch_firmware['default_image']}", file=out)
        click.echo(f"Booted Image: {switch_firmware['booted_image']}", file=out)
    else:
        if firmware_match == "Pass":
            click.echo(
                f"{match_emoji} - Pass - IP: {ip} Hostname:{switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
                file=out,
            )
        if firmware_match == "Fail":
            click.echo(
                f"{match_emoji} - Fail - IP: {ip} Hostname:{switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
                file=out,
            )
            click.secho(f"Firmware should be in: {firmware_range}", fg="red", file=out)


def get_firmware(ip, credentials, return_error=False, cache_minutes=10):
    """Get the firmware of an Aruba switch using v10.04 API.

    :param ip: IPv4 address of the switch
    :param credentials: Dictionary with username and password of the switch
    :param return_error: If True, raises requests exceptions, if False prints error and returns None

    :return: Dictionary with a switches firmware and dictionary with platform_name and hostname
    """
    if firmware_cached_recently(ip, cache_minutes):
        cached_switch = get_switch_from_cache(ip)

        switch_info = {
            "platform_name": cached_switch["platform_name"],
            "hostname": cached_switch["hostname"],
        }

        return cached_switch["firmware"], switch_info

    else:
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

            # Cache switch values
            switch_json = {
                "ip_address": ip,
                "hostname": switch_info["hostname"],
                "platform_name": switch_info["platform_name"],
                "vendor": "aruba",
                "firmware": switch_firmware,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            cache_switch(switch_json)

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
