"""CANU commands that report the firmware of the entire Shasta network."""
from collections import defaultdict
import datetime
import ipaddress
import json

import click
from click_help_colors import HelpColorsCommand
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from click_params import IPV4_ADDRESS, Ipv4AddressListParamType
import click_spinner
import emoji
import requests


from canu.cache import cache_switch
from canu.switch.firmware.firmware import get_firmware


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@optgroup.group(
    "Switch IPv4 input sources",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "--ips",
    help="Comma separated list of IPv4 addresses of switches",
    type=Ipv4AddressListParamType(),
)
@optgroup.option(
    "--ips-file",
    help="File with one IPv4 address per line",
    type=click.File("r"),
)
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option("--json", "json_", is_flag=True, help="Output JSON")
@click.option(
    "--out", help="Output results to a file", type=click.File("w"), default="-"
)
# @click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
@click.pass_context
def firmware(ctx, ips, ips_file, username, password, json_, out):
    """Report the firmware versions of all Aruba switches (API v10.04) on the network.

    Pass in either a comma separated list of IP addresses using the --ips option

    OR

    Pass in a file of IP addresses with one address per line
    There are three different statuses found in the report.

    🛶 Pass: Indicates that the switch passed the firmware verification.

    ❌ Fail: Indicates that the switch failed the firmware verification, in the generated table, a
    list of expected firmware versions for that switch is displayed.

    🔺 Error: Indicates that there was an error connecting to the switch, check the Errors table for the specific error.

    \f
    # noqa: D301

    Args:
        ctx: CANU context settings
        ips: Comma separated list of IPv4 addresses of switches
        ips_file: File with one IPv4 address per line
        username: Switch username
        password: Switch password
        json_: Bool indicating json output
        out: Name of the output file

    Returns:
        json_formatted: If JSON is selected, returns output
    """
    if ctx.obj["shasta"]:
        shasta = ctx.obj["shasta"]
        config = ctx.obj["config"]
        cache_minutes = ctx.obj["cache_minutes"]

    if ips_file:
        ips = []
        lines = [line.strip().replace(",", "") for line in ips_file]
        ips.extend([ipaddress.ip_address(line) for line in lines if IPV4_ADDRESS(line)])

    credentials = {"username": username, "password": password}
    data = []
    errors = []
    switch_json = {}
    ips_length = len(ips)
    if ips:
        with click_spinner.spinner():
            for i, ip in enumerate(ips, start=1):
                print(
                    f"  Connecting to {ip} - Switch {i} of {ips_length}        ",
                    end="\r",
                )
                try:
                    switch_firmware, switch_info = get_firmware(
                        str(ip), credentials, True, cache_minutes
                    )
                    firmware_range = config["shasta"][shasta]["aruba"][
                        switch_info["platform_name"]
                    ]
                    if switch_firmware["current_version"] in firmware_range:
                        match_emoji = emoji.emojize(":canoe:")
                        firmware_match = "Pass"
                        firmware_error = ""
                    else:
                        match_emoji = emoji.emojize(":cross_mark:")
                        firmware_match = "Fail"
                        firmware_error = f"Firmware should be in range {firmware_range}"
                    switch_json[str(ip)] = {
                        "ip_address": str(ip),
                        "status": firmware_match,
                        "hostname": switch_info["hostname"],
                        "platform_name": switch_info["platform_name"],
                        "firmware": switch_firmware,
                        "updated_at": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    data.append(
                        [
                            match_emoji,
                            firmware_match,
                            str(ip),
                            switch_info["hostname"],
                            switch_firmware["current_version"],
                            firmware_error,
                        ]
                    )
                    cache_switch(switch_json[str(ip)])

                except requests.exceptions.HTTPError:
                    switch_json[str(ip)] = {
                        "ip_address": str(ip),
                        "status": "Error",
                        "updated_at": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    error_emoji = emoji.emojize(":red_triangle_pointed_up:")
                    data.append(
                        [
                            error_emoji,
                            "Error",
                            str(ip),
                            "",
                            "",
                            "",
                        ]
                    )
                    errors.append(
                        [
                            str(ip),
                            "HTTP Error. Check that this IP is an Aruba switch, or check the username and password",
                        ]
                    )
                except requests.exceptions.ConnectionError:
                    switch_json[str(ip)] = {
                        "ip_address": str(ip),
                        "status": "Error",
                        "updated_at": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    error_emoji = emoji.emojize(":red_triangle_pointed_up:")
                    data.append(
                        [
                            error_emoji,
                            "Error",
                            str(ip),
                            "",
                            "",
                            "",
                        ]
                    )
                    errors.append(
                        [
                            str(ip),
                            "Connection Error. Check that the IP address is valid",
                        ]
                    )
                except requests.exceptions.RequestException:  # pragma: no cover
                    switch_json[str(ip)] = {
                        "ip_address": str(ip),
                        "status": "Error",
                        "updated_at": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    error_emoji = emoji.emojize(":red_triangle_pointed_up:")
                    data.append(
                        [
                            error_emoji,
                            "Error",
                            str(ip),
                            "",
                            "",
                            "",
                        ]
                    )
                    errors.append(
                        [
                            str(ip),
                            "RequestException Error. Error connecting to switch.",
                        ]
                    )
                except Exception:  # pragma: no cover
                    switch_json[str(ip)] = {
                        "ip_address": str(ip),
                        "status": "Error",
                        "updated_at": datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    }
                    data.append(
                        [
                            error_emoji,
                            "Error",
                            str(ip),
                            "",
                            "",
                            "",
                        ]
                    )
                    errors.append([str(ip), "Unknown error connecting to switch."])

        if json_:
            json_formatted = json.dumps(switch_json, indent=2)
            click.echo("\n")
            click.echo(json_formatted, file=out)
            return json_formatted
        firmware_table(data, out)
        dash = "-" * 66
        if len(errors) > 0:
            click.echo("\n", file=out)
            click.secho("Errors", fg="red", file=out)
            click.echo(dash, file=out)
            for error in errors:
                click.echo("{:<15s} - {}".format(error[0], error[1]), file=out)
        summary_table(data, out)


def firmware_table(data, out="-"):
    """Print a table with switch information.

    Args:
        data: An array of switch information to be printed
            [Status emoji, Status text, Switch IP, Switch Hostname, Current firmware, Error]
        out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 66
    heading = ["", "STATUS", "IP", "HOSTNAME", "FIRMWARE", ""]

    click.echo(dash, file=out)
    click.echo(
        "{:^4s}{:<8s}{:<16s}{:<20s}{:<20s}{}".format(
            heading[0], heading[1], heading[2], heading[3], heading[4], heading[5]
        ),
        file=out,
    )
    click.echo(dash, file=out)

    for i in range(len(data)):
        click.echo(
            "{:^3s}{:<8s}{:<16s}{:<20s}{:20s}{}".format(
                str(data[i][0]),
                str(data[i][1]),
                str(data[i][2]),
                str(data[i][3]),
                str(data[i][4]),
                str(data[i][5]),
            ),
            file=out,
        )


def summary_table(data, out="-"):
    """Print summary of the switch data.

    Args:
        data: An array of switch information to be printed
            [Status emoji, Status text, Switch IP, Switch Hostname, Current firmware, Error]
        out: Defaults to stdout, but will print to the file name passed in
    """
    dash = "-" * 66

    click.echo("\nSummary", file=out)
    click.echo(dash, file=out)

    firmware_versions = defaultdict(int)
    network_summary = defaultdict(int)
    for firmware in data:
        network_summary[firmware[1]] += 1

        if firmware[4] != "":
            firmware_versions[firmware[4]] += 1

    for status, number in network_summary.items():
        if status == "Error":
            status_emoji = emoji.emojize(":red_triangle_pointed_up:")
        elif status == "Fail":
            status_emoji = emoji.emojize(":cross_mark:")
        elif status == "Pass":
            status_emoji = emoji.emojize(":canoe:")

        click.echo(f"{status_emoji} {status} - {number} switches", file=out)

    for version, number in firmware_versions.items():
        click.echo(f"{version} - {number} switches", file=out)
