#!/usr/bin/env bash
# Parity check: compare Python v1 cfn-lint output vs Rust v2 on same templates.
# Usage: ./scripts/parity_check.sh <template_dir_or_file>
#
# Requirements:
#   - Python cfn-lint v1 installed (pip install cfn-lint)
#   - Rust cfn-lint built (cargo build --release -p cfn-lint)
#
# Output: Shows findings that differ between v1 and v2.
# Exit 0 = parity, Exit 1 = differences found.

set -euo pipefail

RUST_BIN="${RUST_BIN:-./target/release/cfn-lint}"
PY_BIN="${PY_BIN:-cfn-lint}"
TMPDIR=$(mktemp -d)

trap "rm -rf $TMPDIR" EXIT

if [ $# -lt 1 ]; then
    echo "Usage: $0 <template_dir_or_file>"
    exit 1
fi

INPUT="$1"

# Collect template files
if [ -d "$INPUT" ]; then
    TEMPLATES=$(find "$INPUT" -name "*.yaml" -o -name "*.yml" -o -name "*.json" | sort)
else
    TEMPLATES="$INPUT"
fi

TOTAL=0
MATCH=0
DIFF=0
MISSING_V2=0
FALSE_POS_V2=0

for tmpl in $TEMPLATES; do
    TOTAL=$((TOTAL + 1))

    # Run Python v1 (json output, sorted by rule+path)
    $PY_BIN -f json "$tmpl" 2>/dev/null | \
        python3 -c "
import json, sys
data = json.load(sys.stdin) if sys.stdin.readable() else []
for item in sorted(data, key=lambda x: (x.get('Rule',{}).get('Id',''), '/'.join(x.get('Location',{}).get('Path',[])))):
    rule_id = item.get('Rule',{}).get('Id','')
    path = '/'.join(item.get('Location',{}).get('Path',[]))
    print(f'{rule_id}\t{path}')
" > "$TMPDIR/v1.txt" 2>/dev/null || true

    # Run Rust v2 (json output, sorted by rule+path)
    $RUST_BIN -f json "$tmpl" 2>/dev/null | \
        python3 -c "
import json, sys
data = json.load(sys.stdin) if sys.stdin.readable() else []
for item in sorted(data, key=lambda x: (x.get('rule_id',''), '/'.join(x.get('path',[])))):
    rule_id = item.get('rule_id','')
    path = '/'.join(item.get('path',[]))
    print(f'{rule_id}\t{path}')
" > "$TMPDIR/v2.txt" 2>/dev/null || true

    # Compare (rule_id + path only — messages may differ)
    if diff -q "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" > /dev/null 2>&1; then
        MATCH=$((MATCH + 1))
    else
        DIFF=$((DIFF + 1))
        # Count specifics
        ONLY_V1=$(comm -23 "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" | wc -l | tr -d ' ')
        ONLY_V2=$(comm -13 "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" | wc -l | tr -d ' ')
        MISSING_V2=$((MISSING_V2 + ONLY_V1))
        FALSE_POS_V2=$((FALSE_POS_V2 + ONLY_V2))

        echo "DIFF: $tmpl"
        echo "  v1-only (missing in v2): $ONLY_V1"
        comm -23 "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" | sed 's/^/    /'
        echo "  v2-only (potential false positives): $ONLY_V2"
        comm -13 "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" | sed 's/^/    /'
        echo ""
    fi
done

echo "=== Parity Summary ==="
echo "Templates checked: $TOTAL"
echo "Exact match: $MATCH"
echo "Differences: $DIFF"
echo "Findings in v1 missing from v2: $MISSING_V2"
echo "Findings in v2 not in v1 (false positives): $FALSE_POS_V2"

if [ $MISSING_V2 -gt 0 ] || [ $FALSE_POS_V2 -gt 0 ]; then
    exit 1
fi
exit 0
