"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._utils import Unset
from cfnlint.rules import CloudFormationLintRule


class CfnLint(CloudFormationLintRule):
    id = "E1101"
    shortdesc = "Validate an item against additional checks"
    description = "Use supplemental logic to validate properties against"
    tags = []

    # pylint: disable=unused-argument
    def cfnLint(self, validator, keywords, instance, schema):
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            )
        )

        for keyword in keywords:
            for rule in self.child_rules.values():
                if rule is None:
                    continue
                if not rule.id:
                    continue

                for rule_keyword in rule.keywords:
                    if rule_keyword == keyword:
                        for err in rule.validate(validator, keyword, instance, schema):
                            if err.rule is None:
                                if isinstance(err.validator, Unset):
                                    err.rule = rule
                            yield err
