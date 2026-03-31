#!/bin/bash
#
# Regenerate all CSM 1.7 golden configuration files for unit tests
#
# This script regenerates golden configs after template changes that affect
# generated output (e.g., ACL optimizations, bug fixes, etc.)
#
# Usage:
#   cd /path/to/canu
#   source ~/canu_venv/bin/activate  # or your venv path
#   bash tests/scripts/regenerate_golden_configs_1.7.sh
#
# What gets regenerated:
#   - Full architecture configs (standard, isolation, IPv6)
#   - TDS architecture configs (standard, IPv6)
#   - Custom configs (standard, IPv6)
#   Total: 57 golden config files
#
# After running:
#   1. Review changes: git diff tests/data/golden_configs/
#   2. Run tests: make unit (or pytest tests/test_*1_7*.py)
#   3. Commit if all tests pass
#

set -e  # Exit on any error

# Ensure we're in the CANU root directory
if [ ! -f "pyproject.toml" ] || [ ! -d "tests/data" ]; then
    echo "Error: Must run from CANU root directory"
    echo "Usage: cd /path/to/canu && bash tests/scripts/regenerate_golden_configs_1.7.sh"
    exit 1
fi

echo "========================================"
echo "Regenerating CSM 1.7 Golden Configs"
echo "========================================"
echo ""
echo "This will regenerate 57 golden config files."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read -r _

# Configuration
DATA_DIR="tests/data"
SHCD_FULL="$DATA_DIR/Full_Architecture_Golden_Config_1.1.5.xlsx"
SHCD_TDS="$DATA_DIR/TDS_Architecture_Golden_Config_1.1.5.xlsx"
SLS_FILE="$DATA_DIR/sls_input_file_csm_1.2.json"
SLS_IPV6_FILE="$DATA_DIR/sls_input_file_csm_1.2_ipv6.json"
CUSTOM_FILE="$DATA_DIR/aruba_custom.yaml"

GOLDEN_FULL="$DATA_DIR/golden_configs/full_configs_1.7"
GOLDEN_TDS="$DATA_DIR/golden_configs/tds_configs_1.7"
GOLDEN_CUSTOM="$DATA_DIR/golden_configs/full_configs_custom_1.7"

# Common arguments for full architecture
FULL_ARGS=(--csm 1.7 -a full --shcd "$SHCD_FULL")
FULL_TABS=(--tabs "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES")
FULL_CORNERS=(--corners "J14,T44,J14,T57,J14,T36,J14,T27")

# Common arguments for TDS architecture
TDS_ARGS=(--csm 1.7 -a tds --shcd "$SHCD_TDS")
TDS_TABS=(--tabs "SWITCH_TO_SWITCH,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES")
TDS_CORNERS=(--corners "J14,T30,J14,T57,J14,T34,J14,T27")

# Counter for progress
count=0
total=57

# Helper function to generate config
generate_config() {
    local name=$1
    local output=$2
    shift 2
    local args=("$@")

    count=$((count + 1))
    echo "[$count/$total] Generating: $name"

    canu generate switch config "${args[@]}" \
        --name "$name" \
        --out "$output" > /dev/null 2>&1
}

echo ""
echo "========================================="
echo "Part 1/5: Full Configs (no flags)"
echo "========================================="

for switch in sw-spine-001 sw-spine-002 sw-leaf-001 sw-leaf-002 sw-leaf-003 sw-leaf-004 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002 sw-edge-001 sw-edge-002; do
    generate_config "$switch" "$GOLDEN_FULL/${switch}.cfg" \
        "${FULL_ARGS[@]}" "${FULL_TABS[@]}" "${FULL_CORNERS[@]}" --sls-file "$SLS_FILE"
done

echo ""
echo "========================================="
echo "Part 2/5: Full Configs (WITH isolation)"
echo "========================================="

for switch in sw-spine-001 sw-spine-002 sw-leaf-001 sw-leaf-002 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002; do
    generate_config "$switch" "$GOLDEN_FULL/${switch}-isolation.cfg" \
        "${FULL_ARGS[@]}" "${FULL_TABS[@]}" "${FULL_CORNERS[@]}" --sls-file "$SLS_FILE" \
        --enable-nmn-isolation --nmn-pvlan 502
done

echo ""
echo "========================================="
echo "Part 3/5: Full Configs (WITH IPv6)"
echo "========================================="

for switch in sw-spine-001 sw-spine-002 sw-leaf-001 sw-leaf-002 sw-leaf-003 sw-leaf-004 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002 sw-edge-001 sw-edge-002; do
    generate_config "$switch" "$GOLDEN_FULL/${switch}-ipv6.cfg" \
        "${FULL_ARGS[@]}" "${FULL_TABS[@]}" "${FULL_CORNERS[@]}" --sls-file "$SLS_IPV6_FILE"
done

echo ""
echo "========================================="
echo "Part 4/5: TDS Configs"
echo "========================================="

# TDS configs (standard)
for switch in sw-spine-001 sw-spine-002 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002; do
    generate_config "$switch" "$GOLDEN_TDS/${switch}.cfg" \
        "${TDS_ARGS[@]}" "${TDS_TABS[@]}" "${TDS_CORNERS[@]}" --sls-file "$SLS_FILE"
done

# TDS configs (IPv6)
for switch in sw-spine-001 sw-spine-002 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002; do
    generate_config "$switch" "$GOLDEN_TDS/${switch}-ipv6.cfg" \
        "${TDS_ARGS[@]}" "${TDS_TABS[@]}" "${TDS_CORNERS[@]}" --sls-file "$SLS_IPV6_FILE"
done

echo ""
echo "========================================="
echo "Part 5/5: Custom Configs"
echo "========================================="

# Custom configs (standard)
for switch in sw-spine-001 sw-spine-002 sw-leaf-001 sw-leaf-002 sw-leaf-003 sw-leaf-004 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002; do
    generate_config "$switch" "$GOLDEN_CUSTOM/${switch}.cfg" \
        "${FULL_ARGS[@]}" "${FULL_TABS[@]}" "${FULL_CORNERS[@]}" --sls-file "$SLS_FILE" \
        --custom-config "$CUSTOM_FILE"
done

# Custom configs (IPv6)
for switch in sw-spine-001 sw-spine-002 sw-leaf-001 sw-leaf-002 sw-leaf-003 sw-leaf-004 sw-leaf-bmc-001 sw-cdu-001 sw-cdu-002; do
    generate_config "$switch" "$GOLDEN_CUSTOM/${switch}-ipv6.cfg" \
        "${FULL_ARGS[@]}" "${FULL_TABS[@]}" "${FULL_CORNERS[@]}" --sls-file "$SLS_IPV6_FILE" \
        --custom-config "$CUSTOM_FILE"
done

echo ""
echo "✅ All $total CSM 1.7 golden configs regenerated!"
echo ""
echo "Next steps:"
echo "  1. Review changes:"
echo "     git diff --stat tests/data/golden_configs/"
echo ""
echo "  2. View specific changes:"
echo "     git diff tests/data/golden_configs/full_configs_1.7/sw-spine-001-isolation.cfg"
echo ""
echo "  3. Run tests to verify:"
echo "     python -m pytest tests/test_generate_switch_config_aruba_configs_csm_1_7*.py -v"
echo ""
echo "  4. If all tests pass, commit the changes:"
echo "     git add tests/data/golden_configs/"
echo "     git commit -m 'Update CSM 1.7 golden configs for [reason]'"
echo ""
