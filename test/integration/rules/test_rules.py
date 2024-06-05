"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import pathlib

from cfnlint.helpers import load_plugins


def test_rule_descriptions():
    root_dir = pathlib.Path(__file__).parent.parent.parent.parent / "src/cfnlint/rules"
    rules = load_plugins(
        str(root_dir),
    )

    descriptions = set()
    shortdesc = set()

    for rule in rules:
        if not rule.id:
            continue
        assert (
            rule.description not in descriptions
        ), f"Duplicate description {rule.description!r}"
        assert (
            rule.shortdesc not in shortdesc
        ), f"Duplicate shortdesc {rule.shortdesc!r}"
        descriptions.add(rule.description)
        shortdesc.add(rule.shortdesc)
