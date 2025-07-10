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
"""Test CANU generate switch config commands."""
from os import path
from pathlib import Path

from click import testing

from canu.cli import cli
from canu.generate.switch.config import config
from tests.lib.diff import diff_config_files

test_file_directory = Path(__file__).resolve().parent
data_directory = path.join(test_file_directory, "data")

# Set CSM version to test
csm = "1.7"

# SLS file to use
sls_file_name = "sls_input_file_csm_1.2.json"
sls_file = path.join(data_directory, sls_file_name)

# Full systems
test_ccj_name = "Full_Architecture_Golden_Config_1.1.5.json"
test_ccj_file = path.join(data_directory, test_ccj_name)
custom_file_name = "aruba_custom.yaml"
custom_file = path.join(data_directory, custom_file_name)
architecture = "full"

# TDS systems
test_shcd_name_tds = "TDS_Architecture_Golden_Config_1.1.5.xlsx"
test_shcd_file_tds = path.join(test_file_directory, "data", test_shcd_name_tds)
architecture_tds = "tds"
tabs_tds = "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES"
corners_tds = "J14,T30,J14,T53,J14,T32,J14,T27"

runner = testing.CliRunner()


def test_switch_config_acls(monkeypatch):
    """Test CANU generation of ACLs for full systems."""
    # Use sw-spine-001 as the switch even though we test only the ACL
    switch_name = "sw-spine-001"

    template_to_test = "acl.j2"
    config_file = f"{template_to_test}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/individual_templates_1.7/{config_file}")

    templates = {
        "sw-spine": {
            "primary": f"1.7/aruba/common/{template_to_test}",
        },
    }
    monkeypatch.setattr(config, "TEMPLATES", templates)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--ccj",
                test_ccj_file,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_services_acls(monkeypatch):
    """Test CANU generation of ACLs for full systems."""
    # Use sw-spine-001 as the switch even though we test only the ACL
    switch_name = "sw-spine-001"

    template_to_test = "services_acl.j2"
    config_file = f"{template_to_test}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/individual_templates_1.7/{config_file}")

    templates = {
        "sw-spine": {
            "primary": f"1.7/aruba/common/{template_to_test}",
        },
    }
    monkeypatch.setattr(config, "TEMPLATES", templates)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--ccj",
                test_ccj_file,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
                "--enable-nmn-isolation",
                "--nmn-pvlan",
                502,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_services_objects(monkeypatch):
    """Test CANU generation of ACLs for full systems."""
    # Use sw-spine-001 as the switch even though we test only the ACL
    switch_name = "sw-spine-001"

    template_to_test = "services_objects.j2"
    config_file = f"{template_to_test}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/individual_templates_1.7/{config_file}")

    templates = {
        "sw-spine": {
            "primary": f"1.7/aruba/common/{template_to_test}",
        },
    }
    monkeypatch.setattr(config, "TEMPLATES", templates)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--ccj",
                test_ccj_file,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
                "--enable-nmn-isolation",
                "--nmn-pvlan",
                502,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0


def test_mtn_acls(monkeypatch):
    """Test CANU generation of ACLs for full systems."""
    # Use sw-spine-001 as the switch even though we test only the ACL
    switch_name = "sw-spine-001"

    template_to_test = "mtn_acl.j2"
    config_file = f"{template_to_test}.cfg"
    golden_config_file = path.join(data_directory, f"golden_configs/individual_templates_1.7/{config_file}")

    templates = {
        "sw-spine": {
            "primary": f"1.7/aruba/common/{template_to_test}",
        },
    }
    monkeypatch.setattr(config, "TEMPLATES", templates)

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "generate",
                "switch",
                "config",
                "--csm",
                csm,
                "--architecture",
                architecture,
                "--ccj",
                test_ccj_file,
                "--sls-file",
                sls_file,
                "--name",
                switch_name,
                "--out",
                config_file,
                "--enable-nmn-isolation",
                "--nmn-pvlan",
                502,
            ],
        )
        assert result.exit_code == 0
        assert diff_config_files(golden_config_file, config_file) == 0
