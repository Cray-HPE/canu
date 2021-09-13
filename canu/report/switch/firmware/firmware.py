"""CANU commands that report the firmware of an individual switch."""
import datetime
import json
import os.path
from pathlib import Path
import sys

import click
from click_help_colors import HelpColorsCommand
import emoji
from netmiko import ssh_exception
import requests
import ruamel.yaml
import urllib3

from canu.cache import cache_switch, firmware_cached_recently, get_switch_from_cache
from canu.utils.utils import netmiko_commands, switch_vendor

yaml = ruamel.yaml.YAML()


# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent

canu_config_file = os.path.join(project_root, "canu", "canu.yaml")

# Get Shasta versions from canu.yaml
with open(canu_config_file, "r") as file:
    canu_config = yaml.load(file)

shasta_options = canu_config["shasta_versions"]


# To disable warnings about unsecured HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--shasta",
    "-s",
    type=click.Choice(shasta_options),
    help="Shasta network version",
    prompt="Shasta network version",
    required=True,
    show_choices=True,
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
def firmware(ctx, shasta, ip, username, password, json_, verbose, out):
    """Report the firmware of an Aruba switch (API v10.04) on the network.

    There are two different statuses that might be indicated.\n
    🛶 - Pass: Indicates that the switch passed the firmware verification.\n
    ❌ - Fail: Indicates that the switch failed the firmware verification. A list of expected firmware versions will be displayed.\n

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        shasta: Shasta version
        ip: Switch IPv4 address
        username: Switch username
        password: Switch password
        json_: Bool indicating json output
        verbose: Bool indicating verbose output
        out: Name of the output file
    """
    config = ctx.obj["config"]
    cache_minutes = ctx.obj["cache_minutes"]

    credentials = {"username": username, "password": password}

    vendor = switch_vendor(ip, credentials)

    if vendor is None:
        return
    elif vendor == "aruba":
        switch_firmware, switch_info = get_firmware_aruba(
            ip, credentials, False, cache_minutes
        )
    elif vendor == "dell":
        switch_firmware, switch_info = get_firmware_dell(
            ip, credentials, False, cache_minutes
        )
    elif vendor == "mellanox":
        switch_firmware, switch_info = get_firmware_mellanox(
            ip, credentials, False, cache_minutes
        )

    if switch_firmware is None:
        return

    # Get the firmware range from the canu.yaml file and the switch info
    firmware_range = config["shasta"][shasta][vendor][switch_info["platform_name"]]

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
                f"{match_emoji} - Pass - IP: {ip} Hostname: {switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
                file=out,
            )
        if firmware_match == "Fail":
            click.echo(
                f"{match_emoji} - Fail - IP: {ip} Hostname: {switch_info['hostname']}"
                + f" Firmware: {switch_firmware['current_version']}",
                file=out,
            )
            click.secho(f"Firmware should be in: {firmware_range}", fg="red", file=out)


def get_firmware_aruba(ip, credentials, return_error=False, cache_minutes=10):
    """Get the firmware of an Aruba switch using v10.04 API.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: If True, raises requests exceptions, if False prints error and returns None
        cache_minutes: Age in minutes of cache before requesting new values

    Returns:
        Dictionary with a switches firmware and dictionary with platform_name and hostname

    Raises:
        http_error: IP not Aruba switch, or credentials bad.
        connection_error: Bad ip address.
        request_exception: Error
        error: Error
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
        except requests.exceptions.RequestException as request_exception:  # pragma: no cover
            if return_error:
                raise request_exception
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


def get_firmware_dell(ip, credentials, return_error=False, cache_minutes=10):
    """Get the firmware of a Dell switch using the API.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: If True, raises requests exceptions, if False prints error and returns None
        cache_minutes: Age in minutes of cache before requesting new values

    Returns:
        Dictionary with a switches firmware and dictionary with platform_name and hostname
    """
    switch_firmware = {
        "current_version": "",
        "primary_version": "",
        "secondary_version": "",
        "default_image": "",
        "booted_image": "",
    }
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
            # GET firmware version
            auth = (credentials["username"], credentials["password"])
            url = f"https://{ip}/restconf/data/system-sw-state/sw-version"

            response = session.get(url, auth=auth, verify=False)
            response.raise_for_status()
            switch_info = response.json()
            switch_firmware["current_version"] = switch_info[
                "dell-system-software:sw-version"
            ]["sw-version"]
            platform_name = switch_info["dell-system-software:sw-version"][
                "sw-platform"
            ]

            # GET hostname
            hostname_url = f"https://{ip}/restconf/data/dell-system:system/hostname"

            get_hostname = session.get(hostname_url, auth=auth, verify=False)
            get_hostname.raise_for_status()
            hostname = get_hostname.json()

            # Cache switch values
            switch_json = {
                "ip_address": ip,
                "hostname": hostname["dell-system:hostname"],
                "platform_name": platform_name,
                "vendor": "dell",
                "firmware": switch_firmware,
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            cache_switch(switch_json)
            return switch_firmware, switch_json

        except (
            requests.exceptions.HTTPError,
            requests.exceptions.RequestException,
            requests.exceptions.ConnectionError,
        ) as error:
            if return_error:
                raise error
            else:
                click.secho(
                    f"Error getting firmware version from Dell switch {ip}",
                    fg="white",
                    bg="red",
                )
                return None, None


def get_firmware_mellanox(ip, credentials, return_error=False, cache_minutes=10):
    """Get the firmware of a Mellanox switch using Netmiko.

    Args:
        ip: IPv4 address of the switch
        credentials: Dictionary with username and password of the switch
        return_error: If True, raises requests exceptions, if False prints error and returns None
        cache_minutes: Age in minutes of cache before requesting new values

    Returns:
        Dictionary with a switches firmware and dictionary with platform_name and hostname

    Raises:
        timeout: Switch timeout.
        auth_err: Auth error
        Exception: Error
    """
    if firmware_cached_recently(ip, cache_minutes):
        cached_switch = get_switch_from_cache(ip)

        switch_info = {
            "platform_name": cached_switch["platform_name"],
            "hostname": cached_switch["hostname"],
        }

        return cached_switch["firmware"], switch_info

    try:
        switch_firmware = {
            "current_version": "",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        }

        commands = [
            "show version concise",
            "show system type",
            "show running-config | include hostname",
        ]
        command_output = netmiko_commands(ip, credentials, commands, "mellanox")

        # Switch Firmware
        for line in command_output[0].splitlines():
            switch_firmware["current_version"] = line.split()[1]

        # Switch Model
        system_type = command_output[1].strip("\n")

        # Switch Hostname
        hostname = ""
        for line in command_output[2].splitlines():
            if line.startswith("   hostname"):
                hostname = command_output[2].split()[1]

        switch_info = {
            "platform_name": system_type,
            "hostname": hostname,
        }

        # Cache switch values
        switch_json = {
            "ip_address": ip,
            "hostname": switch_info["hostname"],
            "platform_name": switch_info["platform_name"],
            "vendor": "mellanox",
            "firmware": switch_firmware,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        cache_switch(switch_json)

    except ssh_exception.NetmikoTimeoutException as timeout:
        if return_error:
            raise timeout
        else:
            click.secho(
                f"Timeout error connecting to switch {ip}, check the IP address and try again.",
                fg="white",
                bg="red",
            )
            return None, None
    except ssh_exception.NetmikoAuthenticationException as auth_err:
        if return_error:
            raise auth_err
        click.secho(
            f"Authentication error connecting to switch {ip}, check the credentials or IP address and try again.",
            fg="white",
            bg="red",
        )
        return None, None
    except Exception as error:  # pragma: no cover
        if return_error:
            raise error
        exception_type = type(error).__name__
        click.secho(
            f"{exception_type} {error}",
            fg="white",
            bg="red",
        )
        return None, None

    return switch_firmware, switch_info
