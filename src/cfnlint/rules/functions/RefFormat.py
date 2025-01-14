"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER


class RefFormat(CfnLintKeyword):
    id = "E1041"
    shortdesc = "Check if Ref matches destination format"
    description = (
        "When source and destination format exists validate that they match in a Ref"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["functions", "ref"]

    def __init__(self):
        super().__init__(["*"])
        self.parent_rules = ["E1020"]

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        fmt = schema.get("format")
        if not fmt:
            return
        _, resource = is_function(instance)

        if resource not in validator.context.resources:
            return
        t = validator.context.resources[resource].type
        for (
            regions,
            resource_schema,
        ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
            t, validator.context.regions
        ):
            region = regions[0]

            ref_schema = validator.context.resources[resource].ref(region)

            ref_fmt = ref_schema.get("format")
            if ref_fmt != fmt:
                if ref_fmt is None:
                    yield ValidationError(
                        f"{instance!r} does not match destination format of {fmt!r}",
                        rule=self,
                    )
                else:
                    yield ValidationError(
                        (
                            f"{instance!r} with format {ref_fmt!r} does not "
                            f"match destination format of {fmt!r}"
                        ),
                        rule=self,
                    )
