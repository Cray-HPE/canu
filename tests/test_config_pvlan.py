# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
"""Test CANU config pvlan command."""
from pathlib import Path

from click.testing import CliRunner

from canu.cli import cli

# Get the path to the test data directory
test_file_directory = Path(__file__).resolve().parent


def test_config_pvlan_help():
    """Test the --help option for the `config pvlan` command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "pvlan", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli config pvlan [OPTIONS]" in result.output
    assert "Configure PVLAN (VLAN) on network switches." in result.output


def test_config_pvlan_create_dry_run():
    """Test `config pvlan` command with --dry-run for VLAN creation."""
    runner = CliRunner()

    sls_file = Path(test_file_directory, "data", "sls_input_file_csm_1.2.json")
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "config",
                "pvlan",
                "--sls-file",
                str(sls_file),
                "--private-vlan",
                "2800",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN MODE" in result.output
        # The test SLS file has 10 switches in HMN
        assert "Generated configuration for 10 switches" in result.output
        assert "Base VLAN configuration" in result.output
        assert "vlan 2" in result.output
        assert "private-vlan primary" in result.output
        assert "vlan 2800" in result.output
        assert "private-vlan isolated 2" in result.output
