"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema import ValidationError, _utils
from cfnlint.rules import CloudFormationLintRule


class UniqueItems(CloudFormationLintRule):
    """Check if duplicates exist in a List"""

    id = "E3037"
    shortdesc = "Check if a list has duplicate values"
    description = (
        "Certain lists don't support duplicate items. "
        "Check when duplicates are provided but not supported."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#uniqueitems"
    tags = ["resources", "property", "list"]
    child_rules = {
        "I3037": None,
    }

    # pylint: disable=unused-argument
    def uniqueItems(self, validator, uI, instance, schema):
        if not validator.is_type(instance, "array"):
            return
        if not _utils.uniq(instance):
            if uI:
                yield ValidationError(f"{instance!r} has non-unique elements")
            elif self.child_rules["I3037"]:
                yield ValidationError(
                    f"{instance!r} has non-unique elements",
                    rule=self.child_rules["I3037"],
                )
