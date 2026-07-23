#!/usr/bin/env python3
"""Import + basic-call smoke test for the cfn-lint Python wheel.

Guards against a broken wheel shipping: exercises the public API surface
(`lint`, `lint_file`, `cli_main`) so a missing export, a mismatched module
init symbol, or an FFI panic is caught in CI before release.

Run after installing the wheel (e.g. `maturin develop` or `pip install`).
"""

import sys
import tempfile

TRIVIAL_TEMPLATE = """\
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"""


def main() -> int:
    # The import itself validates that the PyInit symbol matches and that every
    # name re-exported by cfn_lint/__init__.py exists in the compiled module.
    import cfn_lint
    from cfn_lint._cfn_lint_rs import cli_main, lint, lint_file, parse_template

    # lint(str) -> list[Match]
    matches = cfn_lint.lint(TRIVIAL_TEMPLATE)
    assert isinstance(matches, list), f"expected list, got {type(matches)!r}"
    print(f"cfn_lint.lint OK — {len(matches)} match(es)")

    # lint_file(path) -> list[Match]
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as fh:
        fh.write(TRIVIAL_TEMPLATE)
        path = fh.name
    file_matches = cfn_lint.lint_file(path)
    assert isinstance(file_matches, list), (
        f"expected list, got {type(file_matches)!r}"
    )
    print(f"cfn_lint.lint_file OK — {len(file_matches)} match(es)")

    # parse_template(str) -> str (JSON)
    info = parse_template(TRIVIAL_TEMPLATE)
    assert "Bucket" in info, info
    print("parse_template OK")

    # cli_main must be callable; --version exits 0 via clap.
    assert callable(cli_main), "cli_main is not callable"

    print("cfn-lint wheel smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
