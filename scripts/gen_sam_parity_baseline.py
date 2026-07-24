#!/usr/bin/env python3
"""Regenerate crates/cfn-lint/tests/python_sam_results.json.

This is the FROZEN Python-cfn-lint baseline the SAM-translator parity test
(`crates/cfn-lint/tests/parity.rs::parity_sam_translator`) compares Rust v2
output against. The parity CI job does NOT run Python cfn-lint; it reads this
checked-in file, so it must be an accurate snapshot of the PINNED Python
cfn-lint version's output on the PINNED SAM-translator output templates.

Pins (keep in sync with parity_ratchet.json `fixture_refs`):
  * Python cfn-lint  : v1.53.1   (pip install cfn-lint==1.53.1)
  * SAM app model    : v1.100.0  (aws/serverless-application-model)

Reproduce:
  pip install 'cfn-lint==1.53.1'
  git clone --depth 1 --branch v1.100.0 \
    https://github.com/aws/serverless-application-model.git /tmp/sam
  SAM_TRANSLATOR_DIR=/tmp/sam python3 scripts/gen_sam_parity_baseline.py

Format contract (matches the original file):
  * key   = template path relative to SAM_TRANSLATOR_DIR
  * value = list of rule IDs in cfn-lint emission order, DUPLICATES KEPT
  * only templates with >=1 kept finding are recorded
  * rules in IGNORED_RULES and all informational ("I....") rules are dropped
    (the parity harness filters these on both sides; dropping them here keeps
    the baseline minimal and matches the pre-existing convention)
  * templates listed in sam_active_templates.json that do not exist in the
    pinned SAM checkout are skipped (they produce no comparable findings)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TESTS = REPO / "crates" / "cfn-lint" / "tests"
ACTIVE = TESTS / "sam_active_templates.json"
OUT = TESTS / "python_sam_results.json"

# Rules the parity harness ignores on both sides (see parity.rs `ignored_rules`).
# Kept out of the baseline for a minimal, stable diff.
IGNORED_RULES = {
    "E2531", "E2533", "W2531",  # time-dependent Lambda runtime EOL tables
    "E3001", "W2001", "E3006", "W3037",  # SAM-transform output divergences
}


def rule_ids(sam_dir: str, rel: str) -> tuple[str, list[str]]:
    path = os.path.join(sam_dir, rel)
    if not os.path.isfile(path):
        return rel, []
    proc = subprocess.run(
        ["cfn-lint", "-f", "json", "-t", path],
        capture_output=True,
        text=True,
    )
    out = proc.stdout.strip()
    if not out:
        return rel, []
    findings = json.loads(out)
    ids = [f["Rule"]["Id"] for f in findings]
    ids = [r for r in ids if r not in IGNORED_RULES and not r.startswith("I")]
    return rel, ids


def main() -> int:
    sam_dir = os.environ.get("SAM_TRANSLATOR_DIR")
    if not sam_dir or not os.path.isdir(sam_dir):
        print("SAM_TRANSLATOR_DIR is not set to a valid directory", file=sys.stderr)
        return 2

    active = json.loads(ACTIVE.read_text())
    results: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        for rel, ids in pool.map(lambda r: rule_ids(sam_dir, r), active):
            if ids:
                results[rel] = ids

    # Preserve sam_active_templates.json ordering for a stable, reviewable file.
    ordered = {rel: results[rel] for rel in active if rel in results}
    OUT.write_text(json.dumps(ordered, indent=1) + "\n")
    total = sum(len(v) for v in ordered.values())
    print(f"wrote {OUT} : {len(ordered)} templates, {total} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
