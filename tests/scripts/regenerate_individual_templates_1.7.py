#!/usr/bin/env python3
"""
Regenerate individual template golden configs for CSM 1.7

This script regenerates the golden configs used by test_generate_switch_config_aruba_templates_csm_1_7.py
"""

import os
import sys
from pathlib import Path
from click.testing import CliRunner
from canu.cli import cli
from canu.generate.switch.config import config

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test data
test_ccj_file = str(project_root / "tests/data/Full_Architecture_Golden_Config_1.1.5.json")
sls_file = str(project_root / "tests/data/sls_input_file_csm_1.2.json")
output_dir = project_root / "tests/data/golden_configs/individual_templates_1.7"

# Templates to test
templates_to_test = [
    ("acl.j2", {}),
    ("services_acl.j2", {"flags": ["--enable-nmn-isolation", "--nmn-pvlan", "502"]}),
    ("services_objects.j2", {"flags": ["--enable-nmn-isolation", "--nmn-pvlan", "502"]}),
]

def regenerate_template(template_name, extra_flags=None):
    """Regenerate a single template golden config"""
    config_file = f"{template_name}.cfg"
    output_file = output_dir / config_file
    
    # Monkeypatch TEMPLATES
    original_templates = config.TEMPLATES.copy()
    config.TEMPLATES = {
        "sw-spine": {
            "primary": f"1.7/aruba/common/{template_name}",
        },
    }
    
    try:
        runner = CliRunner()
        args = [
            "generate",
            "switch",
            "config",
            "--csm",
            "1.7",
            "--architecture",
            "Full",
            "--ccj",
            test_ccj_file,
            "--sls-file",
            sls_file,
            "--name",
            "sw-spine-001",
            "--out",
            str(output_file),
        ]
        
        if extra_flags:
            args.extend(extra_flags.get("flags", []))
        
        result = runner.invoke(cli, args)
        
        if result.exit_code != 0:
            print(f"❌ Failed to generate {config_file}")
            print(result.output)
            return False
        
        print(f"✅ Generated: {config_file}")
        return True
        
    finally:
        # Restore original templates
        config.TEMPLATES = original_templates


def main():
    print("=" * 50)
    print("Regenerating Individual Template Golden Configs")
    print("=" * 50)
    print()
    
    success_count = 0
    for template_name, extra_config in templates_to_test:
        if regenerate_template(template_name, extra_config):
            success_count += 1
    
    print()
    print(f"✅ Regenerated {success_count}/{len(templates_to_test)} template golden configs!")
    print()
    print("Next steps:")
    print("  1. Run tests: make unit")
    print("  2. Review: git diff tests/data/golden_configs/individual_templates_1.7/")
    
    return 0 if success_count == len(templates_to_test) else 1


if __name__ == "__main__":
    sys.exit(main())
