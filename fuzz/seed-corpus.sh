#!/usr/bin/env bash
#
# Seed the cargo-fuzz corpora from the repo's existing template fixtures.
#
# The corpus directories (fuzz/corpus/<target>) are generated + git-ignored, so
# this script is the source of truth for the starting inputs. It is idempotent
# and safe to re-run. Run it before `cargo fuzz run <target>` locally and in CI.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Directories that contain real CloudFormation templates to seed from.
SOURCES=(
  "$REPO_ROOT/crates/cfn-lint/tests/fixtures/templates"
  "$REPO_ROOT/tests/integration"
)

seed_target() {
  local target="$1"
  local dest="$SCRIPT_DIR/corpus/$target"
  mkdir -p "$dest"

  local count=0
  for src in "${SOURCES[@]}"; do
    [ -d "$src" ] || continue
    while IFS= read -r -d '' f; do
      # Flatten the relative path into a unique, collision-free corpus filename.
      local rel="${f#"$REPO_ROOT"/}"
      cp -f "$f" "$dest/${rel//\//_}"
      count=$((count + 1))
    done < <(find "$src" -type f \
      \( -name '*.yaml' -o -name '*.yml' -o -name '*.json' -o -name '*.template' \) \
      -print0)
  done
  echo "Seeded $count files into $dest"
}

seed_target ast_parse
seed_target template_parse
