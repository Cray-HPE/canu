# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Test CANU config network command."""
from pathlib import Path

from click.testing import CliRunner

from canu.cli import cli

# Get the path to the test data directory
test_file_directory = Path(__file__).resolve().parent


def test_config_network_help():
    """Test the --help option for the `config network` command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "network", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli config network [OPTIONS]" in result.output
    assert "Configure network features on switches using configuration profiles." in result.output


def test_config_network_dry_run():
    """Test `config network` command with --dry-run."""
    runner = CliRunner()
    sls_file = Path(test_file_directory, "data", "sls_input_file_csm_1.2.json")
    result = runner.invoke(
        cli,
        [
            "config",
            "network",
            "--sls-file",
            str(sls_file),
            "--csm",
            "1.7",
            "--architecture",
            "Full",
            "--profile",
            "nmn-isolation-1.7",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "Generated configuration for sw-leaf-001" in result.output
    assert "Generated configuration for sw-spine-001" in result.output
