"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import regex as re

from cfnlint.helpers import REGEX_DYN_REF
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class AllowedPattern(CloudFormationLintRule):
    """Check if properties have a valid value"""

    id = "E3031"
    shortdesc = "Check if property values adhere to a specific pattern"
    description = "Check if properties have a valid value in case of a pattern (Regular Expression)"
    source_url = "https://github.com/awslabs/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["resources", "property", "allowed pattern", "regex"]
    child_rules = {
        "W2031": None,
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.config_definition = {
            "exceptions": {
                "default": [],
                "type": "list",
                "itemtype": "string",
            }
        }
        self.configure()

    def _is_exception(self, instance: str) -> bool:
        for exception in self.config["exceptions"]:
            if re.match(exception, instance):
                return True
        return False

    # pylint: disable=unused-argument
    def pattern(self, validator, patrn, instance, schema):
        if isinstance(instance, dict):
            if len(instance) == 1:
                for k, v in instance.items():
                    if k == "Ref":
                        if self.child_rules.get("W2031"):
                            yield from self.child_rules["W2031"].validate(v, patrn)
                        return
        if validator.is_type(instance, "string"):
            # skip any dynamic reference strings
            if REGEX_DYN_REF.findall(instance):
                return
            if not re.search(patrn, instance):
                if not self._is_exception(instance):
                    yield ValidationError(f"{instance!r} does not match {patrn!r}")
