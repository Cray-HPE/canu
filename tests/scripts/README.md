# Test Helper Scripts

This directory contains utility scripts for maintaining CANU's test suite.

## Available Scripts

### regenerate_individual_templates_1.7.py

**Purpose:** Regenerate golden configs for individual CSM 1.7 Jinja2 templates used by unit tests.

**When to use:**
- After modifying individual templates like `acl.j2`, `services_acl.j2`, or `services_objects.j2`
- When adding or updating tests in `test_generate_switch_config_aruba_templates_csm_1_7.py`

**What it does:**
- Regenerates 3 template-specific golden configs in `tests/data/golden_configs/individual_templates_1.7/`:
  - `acl.j2.cfg`
  - `services_acl.j2.cfg` (with NMN isolation flags)
  - `services_objects.j2.cfg` (with NMN isolation flags)

**Usage:**
```bash
cd /path/to/canu
source ~/canu_venv/bin/activate  # or your virtualenv
python tests/scripts/regenerate_individual_templates_1.7.py
```

**Next steps after running:**
```bash
make unit
git diff tests/data/golden_configs/individual_templates_1.7/
```

---

### regenerate_golden_configs_1.7.sh

**Purpose:** Regenerate all CSM 1.7 golden configuration files used by unit tests.

**When to use:**
- After making changes to CSM 1.7 Jinja2 templates
- After ACL optimizations or security policy changes
- After bug fixes that affect generated config output
- When adding new object groups or changing ACL structure

**What it does:**
- Regenerates 59 golden config files across 4 categories:
  - Full architecture configs (11 standard + 7 isolation + 11 IPv6)
  - TDS architecture configs (5 standard + 5 IPv6)
  - Custom configs (9 standard + 9 IPv6)
  - Mountain/SLS-mismatch CDU configs (2 — CASMNET-2390 regression)

**Usage:**
```bash
cd /path/to/canu
source ~/canu_venv/bin/activate  # or your virtualenv
bash tests/scripts/regenerate_golden_configs_1.7.sh
```

**Runtime:** ~5-7 minutes

**Important:** Always review the diffs before committing:
```bash
git diff tests/data/golden_configs/full_configs_1.7/
```

## Golden Config Test Process

### What are Golden Configs?

Golden configs are "known good" switch configurations stored in `tests/data/golden_configs/`. Unit tests generate configs from test data and compare them line-by-line to these golden configs to ensure CANU produces consistent, correct output.

### Test File Locations

- `tests/test_generate_switch_config_aruba_configs_csm_1_7.py` - Standard configs
- `tests/test_generate_switch_config_aruba_configs_csm_1_7_isolation.py` - Isolation configs
- `tests/test_generate_switch_config_aruba_configs_csm_1_7_ipv6.py` - IPv6 configs

### When Tests Fail

If you see failures like:
```
AssertionError: assert 115 == 0
  where 115 = diff_config_files(...)
```

This means the generated config differs from the golden config in 115 places.

**Causes:**
1. ✅ **Intentional changes** (template improvements, ACL optimizations)
   - **Fix:** Regenerate golden configs with this script
2. ❌ **Unintentional changes** (bugs, regressions)
   - **Fix:** Fix the bug in the template/code, then verify tests pass

### Workflow for Template Changes

1. **Make your template changes**
   ```bash
   vim network_modeling/configs/templates/1.7/aruba/common/acl.j2
   ```

2. **Run tests to see what changed**
   ```bash
   python -m pytest tests/test_generate_switch_config_aruba_configs_csm_1_7_isolation.py::test_switch_config_spine_primary -xvs
   ```

3. **Review the diff in test output**
   - Look for your expected changes
   - Verify no unexpected changes

4. **If changes are correct, regenerate golden configs**
   ```bash
   bash tests/scripts/regenerate_golden_configs_1.7.sh
   ```

5. **Run tests again to verify**
   ```bash
   python -m pytest tests/test_generate_switch_config_aruba_configs_csm_1_7*.py -v
   ```

6. **Review git diff before committing**
   ```bash
   git diff tests/data/golden_configs/full_configs_1.7/sw-spine-001-isolation.cfg
   ```

7. **Commit both template and golden config changes**
   ```bash
   git add network_modeling/configs/templates/1.7/
   git add tests/data/golden_configs/
   git commit -m "Optimize CSM 1.7 ACLs: consolidate port groups

   - Add MGMT_TCP_PORTS and MGMT_UDP_PORTS object groups
   - Simplify mgmt ACL from 13 rules to 2
   - Update golden configs to match new output"
   ```

## Best Practices

### ✅ Do's

- **Always review diffs** before committing regenerated golden configs
- **Run full test suite** after regenerating
- **Document why** golden configs were regenerated in commit message
- **Spot check** a few generated configs manually
- **Test on real data** if possible before committing

### ❌ Don'ts

- **Don't regenerate** just because CANU version number changed (version is ignored in tests)
- **Don't commit** regenerated configs without reviewing diffs
- **Don't regenerate** to "fix" tests without understanding why they failed
- **Don't mix** unrelated changes with golden config updates

## Adding New Tests

If adding tests for a new CSM version:

1. Create test data files in `tests/data/`
2. Create golden config directory: `tests/data/golden_configs/full_configs_<version>/`
3. Create test file: `tests/test_generate_switch_config_aruba_configs_csm_<version>.py`
4. Generate initial golden configs using CANU
5. Create a regeneration script: `tests/scripts/regenerate_golden_configs_<version>.sh`

## Troubleshooting

### Script fails with "Must run from CANU root directory"

**Solution:** Run from CANU root:
```bash
cd /path/to/canu
bash tests/scripts/regenerate_golden_configs_1.7.sh
```

### Script fails with "command not found: canu"

**Solution:** Activate virtualenv first:
```bash
source ~/canu_venv/bin/activate
bash tests/scripts/regenerate_golden_configs_1.7.sh
```

### Tests still fail after regenerating

**Possible causes:**
1. Script didn't run to completion - check for errors
2. Template has non-deterministic output - fix template
3. Wrong test data files - verify SLS/SHCD files match test expectations

### Generated config shows unexpected changes

**Solution:** 
1. Check recent commits to templates
2. Run diff on template files: `git diff network_modeling/configs/templates/1.7/`
3. If unintended, revert template changes and investigate
4. If intended, review and commit

## Reference

### Golden Config Counts by Type

| Type | Standard | Isolation | IPv6 | Total |
|------|----------|-----------|------|-------|
| Full | 11 | 7 | 11 | 29 |
| TDS | 5 | - | 5 | 10 |
| Custom | 9 | - | 9 | 18 |
| Mtn SLS-mismatch | 2 | - | - | 2 |
| **Total** | **27** | **7** | **25** | **59** |

### Switches by Architecture

**Full Architecture:**
- Spines: sw-spine-001, sw-spine-002
- Leafs: sw-leaf-001, sw-leaf-002, sw-leaf-003, sw-leaf-004
- BMC Leaf: sw-leaf-bmc-001
- CDUs: sw-cdu-001, sw-cdu-002
- Edge: sw-edge-001, sw-edge-002

**TDS Architecture:**
- Spines: sw-spine-001, sw-spine-002
- BMC Leaf: sw-leaf-bmc-001
- CDUs: sw-cdu-001, sw-cdu-002

## Version History

- **2026-01-22:** Initial script created for CSM 1.7 ACL optimizations
  - Added regeneration script
  - Updated 57 golden configs
  - All 65 tests passing

---

**Maintainer:** CANU Development Team  
**Last Updated:** January 22, 2026
