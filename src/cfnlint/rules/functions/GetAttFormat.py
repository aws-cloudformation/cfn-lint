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


class GetAttFormat(CfnLintKeyword):
    id = "E1040"
    shortdesc = "Check if GetAtt matches destination format"
    description = (
        "Validate that if source and destination format exists that they match"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html#parmtypes"
    tags = ["functions", "getatt"]

    def __init__(self):
        super().__init__(["*"])
        self.parent_rules = ["E1010"]
        self._exceptions = [
            # Need to measure for completeness of automation
            # "AWS::EC2::SecurityGroup.GroupId",
            # "AWS::EC2::SecurityGroup.GroupIds",
        ]
        self._resource_type_exceptions = [
            "AWS::CloudFormation::CustomResource",
            "AWS::CloudFormation::Stack",
            "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
        ]

        self._resource_type_attribute_exceptions = [("AWS::SSM::Parameter", "Value")]

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        fmt = schema.get("format")
        if not fmt or fmt in self._exceptions:
            return

        resource, attr = instance[0:2]

        t = validator.context.resources[resource].type
        for (
            regions,
            resource_schema,
        ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
            t, validator.context.regions
        ):
            region = regions[0]

            if t in self._resource_type_exceptions:
                return

            if (t, attr) in self._resource_type_attribute_exceptions:
                return

            getatt_ptr = validator.context.resources[resource].get_atts(region)[attr]

            getatt_schema = resource_schema.resolver.resolve_cfn_pointer(getatt_ptr)

            err = compare_schemas(schema, getatt_schema)
            if err:
                if err.instance:
                    err.message = (
                        f"{{'Fn::GetAtt': {instance!r}}} with formats {err.instance!r} "
                        "does not match destination format of "
                        f"{err.schema.get('format')!r}"
                    )
                else:
                    err.message = (
                        f"{{'Fn::GetAtt': {instance!r}}} does not match "
                        f"destination format of {err.schema.get('format')!r}"
                    )

                err.instance = Unset()
                err.schema = Unset()
                err.rule = self
                yield err
