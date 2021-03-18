"""
Test CANU cli
"""

import click.testing

from canu.cli import cli


def test_cli():
    shasta = "1.4"
    runner = click.testing.CliRunner()

    # Run canu with no errors
    result = runner.invoke(cli)
    assert result.exit_code == 0

    # Error on Shasta flag required
    result = runner.invoke(
        cli,
        [
            "switch",
        ],
    )
    assert result.exit_code == 2
    assert "Error: Missing option '--shasta' / '-s'" in str(result.output)

    # Run with no errors
    result = runner.invoke(
        cli,
        [
            "--shasta",
            shasta,
            "switch",
        ],
    )
    assert result.exit_code == 0
