"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import pathlib

from cfnlint.helpers import load_plugins


def test_cfn_lint_rules_have_validate_function():
    root_dir = pathlib.Path(__file__).parent.parent.parent.parent / "src/cfnlint/rules"
    rules = load_plugins(
        str(root_dir),
        "CfnLintKeyword",
        "cfnlint.rules.jsonschema.CfnLintKeyword",
    )
    rules.extend(
        load_plugins(
            str(root_dir),
            "CfnLintJsonSchema",
            "cfnlint.rules.jsonschema.CfnLintJsonSchema",
        )
    )
    rules.extend(
        load_plugins(
            str(root_dir),
            "CfnLintJsonSchemaRegional",
            "cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional",
        )
    )

    parent_rules = [
        "E1010",
        "E1101",
        "E1020",
    ]

    for rule in rules:
        assert hasattr(rule, "validate")
        assert callable(rule.validate)
        assert all(
            r in parent_rules for r in rule._parent_rules
        ), f"{rule._parent_rules!r} not in {parent_rules!r}"
