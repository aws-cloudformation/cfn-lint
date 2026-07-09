#!/usr/bin/env bash
set -euo pipefail

AUTO_DISCOVER=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto-discover) AUTO_DISCOVER=true; shift ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Run from the project root so all relative paths below resolve consistently
# regardless of where the script was invoked from.
cd "$PROJECT_DIR"

TEMPLATES_DIR="test/fixtures/templates"
RESULTS_DIR="test/fixtures/results"

# Use local source code
export PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

# Files to track handled templates and written results
HANDLED=$(mktemp)
WRITTEN=$(mktemp)
trap 'rm -f "$HANDLED" "${HANDLED}.all" "$WRITTEN"' EXIT

# Performance tracking
TOTAL_START=$(python -c 'import time;print(time.time())')
TEMPLATE_COUNT=0

run_lint() {
    local template="$1"
    local result="$2"
    shift 2

    mkdir -p "$(dirname "$result")"

    local start end elapsed
    start=$(python -c 'import time;print(time.time())')
    python -c "
import sys
from cfnlint.runner import main
main()
" "$template" -e -c I --format json "$@" > "$result" 2>/dev/null || true
    end=$(python -c 'import time;print(time.time())')
    elapsed=$(python -c "print(f'{($end-$start)*1000:.2f}')")

    echo "[${elapsed}ms] $result"
    echo "$template" >> "$HANDLED"
    echo "$result" >> "$WRITTEN"
    TEMPLATE_COUNT=$((TEMPLATE_COUNT + 1))
}

# ============================================================================
# Manual entries: templates that need special flags or name mappings
# ============================================================================

# integration/
run_lint "$TEMPLATES_DIR/integration/dynamic-references.yaml" "$RESULTS_DIR/integration/dynamic-references_yaml.json"
run_lint "$TEMPLATES_DIR/integration/resources-cloudformation-init.yaml" "$RESULTS_DIR/integration/resources-cloudformation-init_yaml.json"
run_lint "$TEMPLATES_DIR/integration/ref-no-value.yaml" "$RESULTS_DIR/integration/ref-no-value_yaml.json"
run_lint "$TEMPLATES_DIR/integration/availability-zones.yaml" "$RESULTS_DIR/integration/availability-zones_yaml.json"
run_lint "$TEMPLATES_DIR/integration/getatt-types.yaml" "$RESULTS_DIR/integration/getatt-types_yaml.json"
run_lint "$TEMPLATES_DIR/integration/ref-types.yaml" "$RESULTS_DIR/integration/ref-types_yaml.json"
run_lint "$TEMPLATES_DIR/integration/formats.yaml" "$RESULTS_DIR/integration/formats_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-ec2-networkinterface.yaml" "$RESULTS_DIR/integration/aws-ec2-networkinterface_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-ec2-instance.yaml" "$RESULTS_DIR/integration/aws-ec2-instance_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-ec2-launchtemplate.yaml" "$RESULTS_DIR/integration/aws-ec2-launchtemplate_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-ec2-subnet.yaml" "$RESULTS_DIR/integration/aws-ec2-subnet_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-dynamodb-table.yaml" "$RESULTS_DIR/integration/aws-dynamodb-table_yaml.json"
run_lint "$TEMPLATES_DIR/integration/custom-resources.yaml" "$RESULTS_DIR/integration/custom-resources_yaml.json"
run_lint "$TEMPLATES_DIR/integration/cfn-gather.yaml" "$RESULTS_DIR/integration/cfn-gather_yaml.json"
run_lint "$TEMPLATES_DIR/integration/aws-lambda-function.yaml" "$RESULTS_DIR/integration/aws-lambda-function_yaml.json"
run_lint "$TEMPLATES_DIR/integration/module-sub-resources.yaml" "$RESULTS_DIR/integration/module-sub-resources_yaml.json"
run_lint "$TEMPLATES_DIR/integration/get-stack-output.yaml" "$RESULTS_DIR/integration/get-stack-output_yaml.json"

# integration/ special name mapping (template has typo: metdata)
run_lint "$TEMPLATES_DIR/integration/metdata.yaml" "$RESULTS_DIR/integration/metadata_yaml.json"

# public/ (watchmaker needs strict E3012)
run_lint "$TEMPLATES_DIR/public/lambda-poller.yaml" "$RESULTS_DIR/public/lambda-poller_yaml.json"
run_lint "$TEMPLATES_DIR/public/watchmaker.json" "$RESULTS_DIR/public/watchmaker_json.json" -x E3012:strict=true

# quickstart/non_strict/
run_lint "$TEMPLATES_DIR/quickstart/cis_benchmark.yaml" "$RESULTS_DIR/quickstart/non_strict/cis_benchmark_yaml.json"
run_lint "$TEMPLATES_DIR/quickstart/nist_application.yaml" "$RESULTS_DIR/quickstart/non_strict/nist_application_yaml.json"
run_lint "$TEMPLATES_DIR/quickstart/nist_high_main.yaml" "$RESULTS_DIR/quickstart/non_strict/nist_high_main_yaml.json"
run_lint "$TEMPLATES_DIR/quickstart/openshift.yaml" "$RESULTS_DIR/quickstart/non_strict/openshift_yaml.json"

# quickstart/ (strict E3012)
run_lint "$TEMPLATES_DIR/quickstart/cis_benchmark.yaml" "$RESULTS_DIR/quickstart/cis_benchmark_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_application.yaml" "$RESULTS_DIR/quickstart/nist_application_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_config_rules.yaml" "$RESULTS_DIR/quickstart/nist_config_rules_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_high_main.yaml" "$RESULTS_DIR/quickstart/nist_high_main_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_iam.yaml" "$RESULTS_DIR/quickstart/nist_iam_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_logging.yaml" "$RESULTS_DIR/quickstart/nist_logging_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_vpc_management.yaml" "$RESULTS_DIR/quickstart/nist_vpc_management_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/nist_vpc_production.yaml" "$RESULTS_DIR/quickstart/nist_vpc_production_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/openshift.yaml" "$RESULTS_DIR/quickstart/openshift_yaml.json" -x E3012:strict=true
run_lint "$TEMPLATES_DIR/quickstart/openshift_master.yaml" "$RESULTS_DIR/quickstart/openshift_master_yaml.json" -x E3012:strict=true

# ============================================================================
# Auto-discover remaining templates not handled above (requires --auto-discover)
# ============================================================================

if $AUTO_DISCOVER; then
find "$TEMPLATES_DIR" -type f \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) \
    ! -path '*/override_spec/*' \
    ! -path '*/bad/override/*' \
    ! -name '__init__.py' \
    ! -name 'README.md' \
    | sort > "${HANDLED}.all"

while read -r template; do
    # Skip templates already handled by manual entries
    if grep -qxF "$template" "$HANDLED"; then
        continue
    fi

    # Compute result path: replace templates/ with results/, fold the template
    # extension into the name as an underscore suffix so json/yaml/yml templates
    # with the same name don't clobber each other (e.g. foo.yaml -> foo_yaml.json).
    relative="${template#$TEMPLATES_DIR/}"
    result_file="$RESULTS_DIR/${relative%.*}_${relative##*.}.json"

    # Skip if another template already wrote this result file during this run
    if grep -qxF "$result_file" "$WRITTEN"; then
        echo "[SKIP] $template -> $result_file already written by another template"
        continue
    fi

    run_lint "$template" "$result_file"
done < "${HANDLED}.all"
rm -f "${HANDLED}.all"
fi

# ============================================================================
# Performance summary
# ============================================================================
TOTAL_END=$(python -c 'import time;print(time.time())')
WALL_TIME=$(python -c "print(f'{($TOTAL_END-$TOTAL_START)*1000:.2f}')")

echo ""
echo "=== Performance Summary ==="
echo "Templates processed: $TEMPLATE_COUNT"
echo "Wall clock time:     ${WALL_TIME}ms"
echo "Done."
