"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._utils import Unset
from cfnlint.rules.formats._schema_comparer import compare_schemas
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
        if instance in validator.context.parameters:
            return

        if instance not in validator.context.resources:
            return
        t = validator.context.resources[instance].type
        for (
            regions,
            resource_schema,
        ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
            t, validator.context.regions
        ):
            region = regions[0]

            ref_schema = validator.context.resources[instance].ref(region)

            err = compare_schemas(schema, ref_schema)
            if err:
                if err.instance:
                    err.message = (
                        f"{{'Ref': {instance!r}}} with formats {err.instance!r} "
                        "does not match destination format of "
                        f"{err.schema.get('format')!r}"
                    )
                else:
                    err.message = (
                        f"{{'Ref': {instance!r}}} does not match "
                        f"destination format of {err.schema.get('format')!r}"
                    )

                err.instance = Unset()
                err.schema = Unset()
                err.rule = self
                yield err
