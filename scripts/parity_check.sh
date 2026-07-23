#!/usr/bin/env bash
# Parity check: compare Python v1 cfn-lint output vs Rust v2 on same templates.
# Usage: ./scripts/parity_check.sh <template_dir_or_file>
#
# Requirements:
#   - Python cfn-lint v1 installed (pip install cfn-lint)
#   - Rust cfn-lint built (cargo build --release -p cfn-lint)
#
# Output: Shows findings that differ between v1 and v2.
# Exit 0 = parity, Exit 1 = differences found, Exit 2 = a linter crashed.
#
# C88: Previously both linters were run with `2>/dev/null | ... || true`, which
# discarded stderr and swallowed non-zero exits. A binary that crashed on every
# template produced empty stdout, which compared "equal" to the other's empty
# stdout and was scored as 100% parity. Now we capture each run's stderr to a
# per-template log, and REQUIRE valid JSON on stdout before comparing: a crash,
# a Python traceback, a segfault, or empty output is flagged as an error (with a
# pointer to its stderr log) and forces a non-zero exit — it can never masquerade
# as parity. `cfn-lint` legitimately exits non-zero when it *finds* issues, so a
# non-zero exit alone is not treated as failure; producing non-JSON/empty output
# (or dying from a signal) is.

set -euo pipefail

RUST_BIN="${RUST_BIN:-./target/release/cfn-lint}"
PY_BIN="${PY_BIN:-cfn-lint}"
TMPDIR=$(mktemp -d)
LOGDIR="$TMPDIR/logs"
mkdir -p "$LOGDIR"

trap 'rm -rf "$TMPDIR"' EXIT

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
ERRORS=0

# Run a linter, capturing stdout to $2 and stderr to $3. Returns the exit code.
# Does not abort the script on a non-zero exit (that is expected when issues are
# found, and a crash is handled explicitly by the caller).
run_tool() {
    local bin="$1" out="$2" err="$3" tmpl="$4"
    set +e
    "$bin" -f json "$tmpl" >"$out" 2>"$err"
    local rc=$?
    set -e
    return $rc
}

# Normalize a linter's JSON output to sorted "rule_id<TAB>path" lines.
# $2 selects the shape: "v1" (Python: Rule.Id / Location.Path) or "v2" (Rust:
# rule_id / path). Exits non-zero (leaving stdout empty) if the input is not
# valid JSON — the signal the caller uses to detect a crash.
normalize() {
    local file="$1" shape="$2"
    python3 - "$file" "$shape" <<'PY'
import json, sys
path, shape = sys.argv[1], sys.argv[2]
with open(path) as fh:
    raw = fh.read()
if not raw.strip():
    sys.exit(3)  # empty output -> treat as crash/error
data = json.loads(raw)  # raises (non-zero exit) on invalid JSON
rows = []
for item in data:
    if shape == "v1":
        rule_id = item.get("Rule", {}).get("Id", "")
        loc = "/".join(item.get("Location", {}).get("Path", []))
    else:
        rule_id = item.get("rule_id", "")
        loc = "/".join(item.get("path", []))
    rows.append(f"{rule_id}\t{loc}")
for row in sorted(rows):
    print(row)
PY
}

sanitize() { echo "$1" | tr '/ ' '__'; }

for tmpl in $TEMPLATES; do
    TOTAL=$((TOTAL + 1))
    tag=$(sanitize "$tmpl")
    v1_json="$TMPDIR/$tag.v1.json"
    v2_json="$TMPDIR/$tag.v2.json"
    v1_err="$LOGDIR/$tag.v1.err"
    v2_err="$LOGDIR/$tag.v2.err"

    run_tool "$PY_BIN" "$v1_json" "$v1_err" "$tmpl" || v1_rc=$?
    v1_rc=${v1_rc:-0}
    run_tool "$RUST_BIN" "$v2_json" "$v2_err" "$tmpl" || v2_rc=$?
    v2_rc=${v2_rc:-0}

    # Detect crashes: killed by a signal (rc >= 128), or output that is not
    # valid, non-empty JSON. Either way we cannot compare this template.
    tmpl_error=0
    if [ "$v1_rc" -ge 128 ] || ! normalize "$v1_json" v1 >"$TMPDIR/v1.txt" 2>/dev/null; then
        echo "ERROR: v1 (Python) crashed or produced no valid JSON on: $tmpl (exit $v1_rc)"
        echo "       stderr: $v1_err"
        sed 's/^/         | /' "$v1_err" | head -n 5
        tmpl_error=1
    fi
    if [ "$v2_rc" -ge 128 ] || ! normalize "$v2_json" v2 >"$TMPDIR/v2.txt" 2>/dev/null; then
        echo "ERROR: v2 (Rust) crashed or produced no valid JSON on: $tmpl (exit $v2_rc)"
        echo "       stderr: $v2_err"
        sed 's/^/         | /' "$v2_err" | head -n 5
        tmpl_error=1
    fi

    unset v1_rc v2_rc

    if [ "$tmpl_error" -eq 1 ]; then
        ERRORS=$((ERRORS + 1))
        echo ""
        continue
    fi

    # Compare (rule_id + path only — messages may differ)
    if diff -q "$TMPDIR/v1.txt" "$TMPDIR/v2.txt" >/dev/null 2>&1; then
        MATCH=$((MATCH + 1))
    else
        DIFF=$((DIFF + 1))
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
echo "Errors (linter crash / no valid JSON): $ERRORS"
echo "Findings in v1 missing from v2: $MISSING_V2"
echo "Findings in v2 not in v1 (false positives): $FALSE_POS_V2"

# A crash must never be reported as parity.
if [ "$ERRORS" -gt 0 ]; then
    exit 2
fi
if [ "$MISSING_V2" -gt 0 ] || [ "$FALSE_POS_V2" -gt 0 ]; then
    exit 1
fi
exit 0
