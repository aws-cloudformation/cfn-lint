"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from cfnlint.helpers import is_custom_resource
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

    def _filter_schema(
        self, validator: Validator, type_name: str, id: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        if type_name != "AWS::EC2::SecurityGroup":
            return schema

        items = list(
            validator.cfn.get_cfn_path(
                ["Resources", id, "Properties", "VpcId"], validator.context
            )
        )
        if items:
            # VpcId is specified and will have a value which means the returned value is
            # "AWS::EC2::SecurityGroup.Id"
            schema = deepcopy(schema)
            schema.pop("anyOf")
            schema["format"] = "AWS::EC2::SecurityGroup.Id"
            return schema

        # VpcId being None means it wasn't specified and the value is a Name
        schema = deepcopy(schema)
        schema.pop("anyOf")
        schema["format"] = "AWS::EC2::SecurityGroup.Name"
        return schema

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        if instance in validator.context.parameters:
            return

        if instance not in validator.context.resources:
            return
        t = validator.context.resources[instance].type

        # When using a custom resource you can set the physical ID
        # which results in a usable Ref
        if is_custom_resource(t):
            return

        for (
            regions,
            resource_schema,
        ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
            t, validator.context.regions
        ):
            region = regions[0]
            ref_schema = validator.context.resources[instance].ref(region)
            ref_schema = self._filter_schema(validator, t, instance, ref_schema)

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
