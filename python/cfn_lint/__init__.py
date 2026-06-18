"""cfn-lint v2 — CloudFormation template linter (Rust-backed)."""

from cfn_lint._cfn_lint_rs import lint, lint_file


def main():
    """Entry point for the cfn-lint CLI."""
    import sys

    from cfn_lint._cfn_lint_rs import cli_main

    sys.exit(cli_main())
