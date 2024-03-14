"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pathlib

from cfnlint.helpers import load_plugins
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


class CfnLint(CloudFormationLintRule):
    id = "E1101"
    shortdesc = "Validate an item against additional checks"
    description = "Use supplemental logic to validate properties against"
    tags = []

    def __init__(self) -> None:
        super().__init__()
        # relative path to the parent of cfnlint.rules
        root_dir = pathlib.Path(__file__).parent.parent
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
        for rule in rules:
            self.child_rules[rule.id] = None

    # pylint: disable=unused-argument
    def cfnLint(self, validator, keywords, instance, schema):
        keywords = ensure_list(keywords)
        for keyword in keywords:
            for rule in self.child_rules.values():
                if rule is None:
                    continue
                if not rule.id:
                    continue

                for rule_keyword in rule.keywords:
                    if rule_keyword == keyword:
                        yield from rule.validate(validator, keyword, instance, schema)
