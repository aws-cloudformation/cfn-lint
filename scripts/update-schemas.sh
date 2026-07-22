#!/usr/bin/env bash
#
# Refresh the vendored CloudFormation provider/resource schemas.
#
# The schemas under crates/cfn-lint/data/schemas/{providers,resources}/ are
# vendored into the repository (C85) rather than downloaded at build time from a
# mutable `releases/download/latest/` URL. This keeps builds reproducible and
# supply-chain changes reviewable. Run this script to intentionally update the
# vendored copy; commit the resulting diff so the change is reviewed.
#
# Usage: scripts/update-schemas.sh
set -euo pipefail

SCHEMAS_URL="https://github.com/aws-cloudformation/resource-provider-enhanced-schemas/releases/download/latest/schemas-cfn-lint.zip"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMAS_DIR="${SCRIPT_DIR}/../crates/cfn-lint/data/schemas"
TMP_ZIP="$(mktemp -t schemas-cfn-lint.XXXXXX.zip)"
trap 'rm -f "${TMP_ZIP}"' EXIT

echo "Downloading schemas from ${SCHEMAS_URL}"
curl -fsSL "${SCHEMAS_URL}" -o "${TMP_ZIP}"
echo "SHA256: $(sha256sum "${TMP_ZIP}" | awk '{print $1}')"

cd "${SCHEMAS_DIR}"
# Replace the vendored copies so removed upstream files don't linger.
rm -rf providers resources
unzip -qo "${TMP_ZIP}"

# Normalize provider filenames: '-' -> '_' to match the loader's expectations.
(
  cd providers
  for f in *-*.json; do
    [ -e "$f" ] && mv "$f" "$(echo "$f" | tr '-' '_')" || true
  done
)

echo "Updated: $(ls providers | wc -l) providers, $(ls resources | wc -l) resources"
echo "Review and commit the diff under ${SCHEMAS_DIR}"
