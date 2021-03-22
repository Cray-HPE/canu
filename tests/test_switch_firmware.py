"""
Test CANU.
"""
import click.testing
import pytest
import requests
import responses

from canu.cli import cli
from canu.switch.firmware.firmware import get_firmware


username = "admin"
password = "admin"
ip = "192.168.1.1"
credentials = {"username": username, "password": password}
shasta = "1.4"
runner = click.testing.CliRunner()


def test_switch_cli():

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
        ],
    )
    assert result.exit_code == 0


@responses.activate
def test_get_firmware_function():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    switch_firmware, switch_info = get_firmware(ip, credentials)

    assert switch_firmware["current_version"] == "Virtual.10.06.0001"
    assert switch_info["hostname"] == "test-switch"
    assert switch_info["platform_name"] == "X86-64"


@responses.activate
def test_get_firmware_function_bad_ip():
    bad_ip = "192.168.1.99"

    responses.add(
        responses.POST,
        f"https://{bad_ip}/rest/v10.04/login",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 60] Operation timed out'))"
        ),
    )

    with pytest.raises(requests.exceptions.ConnectionError) as connection_error:
        switch_firmware, switch_info = get_firmware(  # pylint: disable=unused-variable
            bad_ip, credentials, True
        )

    assert "Failed to establish a new connection" in str(connection_error.value)


@responses.activate
def test_get_firmware_function_bad_credentials():
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
        body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
    )

    bad_credentials = {"username": "foo", "password": "foo"}

    with pytest.raises(requests.exceptions.HTTPError) as http_error:
        switch_firmware, switch_info = get_firmware(  # pylint: disable=unused-variable
            ip, bad_credentials, True
        )
    assert "Unauthorized for url" in str(http_error.value)


@responses.activate
def test_switch_firmware():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_switch_firmware_verbose():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "Virtual.10.06.0001" in str(result.output)
    assert ip in str(result.output)


def test_switch_firmware_missing_ip():

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 2
    assert "Missing option '--ip'" in str(result.output)


def test_switch_firmware_invalid_ip():

    invalid_ip = "999.999.999.999"
    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            invalid_ip,
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_firmware_bad_ip():
    bad_ip = "192.168.1.99"

    responses.add(
        responses.POST,
        f"https://{bad_ip}/rest/v10.04/login",
        body=requests.exceptions.ConnectionError(
            "Failed to establish a new connection: [Errno 60] Operation timed out'))"
        ),
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "check the IP address and try again" in str(result.output)


@responses.activate
def test_switch_firmware_bad_password():
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
        body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
    )

    bad_password = "foo"
    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            bad_password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "check the username or password" in str(result.output)


@responses.activate
def test_switch_firmware_json():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert "Virtual.10.06.0001" in str(result.output)


@responses.activate
def test_switch_firmware_json_verbose():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "X86-64"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
            "--json",
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "'current_version': 'Virtual.10.06.0001', 'primary_version': '', " in str(
        result.output
    )


@responses.activate
def test_switch_firmware_mismatch():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "8320"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
        ],
    )
    assert result.exit_code == 0
    assert "Firmware should be in:" in str(result.output)


@responses.activate
def test_switch_firmware_mismatch_verbose():

    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/login",
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/firmware",
        json={
            "current_version": "Virtual.10.06.0001",
            "primary_version": "",
            "secondary_version": "",
            "default_image": "",
            "booted_image": "",
        },
    )
    responses.add(
        responses.GET,
        f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname",
        json={"hostname": "test-switch", "platform_name": "8320"},
    )
    responses.add(
        responses.POST,
        f"https://{ip}/rest/v10.04/logout",
    )

    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
            "firmware",
            "--ip",
            ip,
            "--username",
            username,
            "--password",
            password,
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    assert "Firmware should be in:" in str(result.output)
