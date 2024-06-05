"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword
from cfnlint.schema.resolver import RefResolutionError


class ReadOnly(CfnLintKeyword):
    """Check Base Resource Configuration"""

    id = "E3040"
    shortdesc = "Validate we aren't configuring read only properties"
    description = (
        "Read only properties can be configured in a CloudFormation template but "
        "they aren't sent to the resource provider code and can cause drift."
    )
    source_url = "https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/resource-type-schema.html#schema-properties-readonlyproperties"
    tags = ["resources", "properties"]

    def __init__(self):
        """Init"""
        super().__init__(keywords=["*"])

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        if len(validator.context.path.cfn_path) < 3:
            return

        parent, _, section = list(validator.context.path.cfn_path)[0:3]
        if parent != "Resources" or section != "Properties":
            return

        p = "/properties/" + "/".join(list(validator.context.path.cfn_path)[3:])

        try:
            if p in validator.resolver.resolve_from_url("#/readOnlyProperties"):
                yield ValidationError(
                    "Read only properties are not allowed "
                    f"({validator.context.path.cfn_path[-1]!r})"
                )

        except RefResolutionError:
            pass
