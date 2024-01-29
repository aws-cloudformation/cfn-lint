"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pathlib
from typing import Any

import regex as re
from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._validators import type
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


_pattern = re.compile("[\W_]+")


class CfnLint(BaseJsonSchema):
    id = "E3017"
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
        rules.extend(load_plugins(
            str(root_dir),
            "CfnLintJsonSchema",
            "cfnlint.rules.jsonschema.CfnLintJsonSchema",
        ))
        for rule in rules:
            self.child_rules[rule.id] = rule

    # pylint: disable=unused-argument
    def cfnLint(self, validator, keywords, instance, schema):
        keywords = ensure_list(keywords)

        for keyword in keywords:
            for rule in self.child_rules.values():
                for keyword in rule.keywords:
                    if keyword == keyword:
                        fn_name = self._pattern.sub('', keyword)
                        fn = getattr(rule, fn_name)
                        if not fn:
                            raise ValueError(f"{fn!r} not found in ${rule.id}")
                        yield from fn(validator, keywords, instance, schema)

