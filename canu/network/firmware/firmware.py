from collections import defaultdict

import click
from click_help_colors import HelpColorsCommand
from click_params import Ipv4AddressListParamType
import click_spinner
import emoji
import requests


from canu.switch.firmware.firmware import get_firmware


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="blue",
)
@click.option(
    "--ips",
    required=True,
    help="Comma separated list of IP addresses of switches",
    type=Ipv4AddressListParamType(),
)
@click.option("--username", default="admin", show_default=True, help="Switch username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Switch password",
)
@click.option(
    "--out", help="Output results to a file", type=click.File("w"), default="-"
)
# @click.option("--json", is_flag=True, help="Output JSON")
# @click.option("--verbose", "-v", is_flag=True, help="Verbose mode")
@click.pass_context
def firmware(ctx, ips, username, password, out):
    """
    The network FIRMWARE command will report the firmware versions of all
    Aruba switches using API v10.04 on the network.

    Pass in either a comma separated list of IP addresses using the --ips option
    \n
    OR
    \n
    Pass in a file of IP addresses with one address per line
    There are three different statuses found in the report.\n
    🛶 Pass: Indicates that the switch passed the firmware verification.\n
    ❌ Fail: Indicates that the switch failed the firmware verification, in the generated table, a
    list of expected firmware versions for that switch is displayed.\n
    🔺 Error: Indicates that there was an error connecting to the switch, check the Errors table for the specific error.
    """
    if ctx.obj["shasta"]:
        shasta = ctx.obj["shasta"]
        config = ctx.obj["config"]

    credentials = {"username": username, "password": password}
    data = []
    errors = []
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
                        str(ip), credentials, True
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

                except requests.exceptions.HTTPError:
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
                        [str(ip), "RequestException Error. Error connecting to switch."]
                    )
                except Exception:  # pragma: no cover
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
                data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], data[i][5]
            ),
            file=out,
        )


def summary_table(data, out="-"):
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
