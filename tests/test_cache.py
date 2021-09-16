# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Test CANU cache."""
import json
from unittest.mock import patch

from click import testing
import pytest
import responses

from canu.cache import (
    firmware_cached_recently,
    get_switch_from_cache,
    remove_switch_from_cache,
)
from canu.cli import cli


username = "admin"
password = "admin"
ip = "192.168.1.1"
credentials = {"username": username, "password": password}
shasta = "1.4"
cache_minutes = 10
runner = testing.CliRunner()


@patch("canu.report.switch.firmware.firmware.switch_vendor")
@responses.activate
def test_switch_caching(switch_vendor):
    """Test that the `canu switch firmware` command caches the switch info."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
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

        runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--shasta",
                shasta,
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

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "report",
                "switch",
                "firmware",
                "--shasta",
                shasta,
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

        result_json = json.loads(result.output)

        cached_switch = get_switch_from_cache(ip)

        assert (
            cached_switch["firmware"]["current_version"]
            == result_json["firmware"]["current_version"]
        )
        assert cached_switch["platform_name"] == result_json["platform_name"]
        assert cached_switch["hostname"] == result_json["hostname"]


def test_get_switch_from_cache_exception():
    """Test the get_switch_from_cache fails."""
    bad_ip = "999.999.999.999"

    with pytest.raises(Exception) as error:
        get_switch_from_cache(bad_ip)

    assert "IP address 999.999.999.999 not in cache." in str(error.value)


def test_firmware_cached_recently():
    """Test the firmware_cached_recently function."""
    # Cached less than 999 minutes ago?
    assert firmware_cached_recently(ip, 999) is True
    # Cached less than 0 minutes ago?
    assert firmware_cached_recently(ip, 0) is False

    # Remove test switch from cache
    remove_switch_from_cache(ip)
