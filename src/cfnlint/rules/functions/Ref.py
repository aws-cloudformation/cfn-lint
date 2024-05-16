"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.helpers import VALID_PARAMETER_TYPES, VALID_PARAMETER_TYPES_LIST
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class Ref(BaseFn):
    """Check if Ref value is a string"""

    id = "E1020"
    shortdesc = "Ref validation of value"
    description = (
        "Making sure the Ref has a String value (no other functions are supported)"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html"
    tags = ["functions", "ref"]

    def __init__(self) -> None:
        super().__init__("Ref", all_types)
        self.keywords = {
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::Batch::ComputeEnvironment/Properties/ComputeResources/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::Cloud9::EnvironmentEC2/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::Instance/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::ImageBuilder::Image/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::DirectoryService::MicrosoftAD/Properties/Password": "W1011",  # noqa: E501
            "Resources/AWS::DirectoryService::SimpleAD/Properties/Password": "W1011",  # noqa: E501
            "Resources/AWS::ElastiCache::ReplicationGroup/Properties/AuthToken": "W1011",  # noqa: E501
            "Resources/AWS::IAM::User/Properties/LoginProfile/Password": "W1011",  # noqa: E501
            "Resources/AWS::KinesisFirehose::DeliveryStream/Properties/RedshiftDestinationConfiguration/Password": "W1011",  # noqa: E501
            "Resources/AWS::OpsWorks::App/Properties/AppSource/Password": "W1011",  # noqa: E501
            "Resources/AWS::OpsWorks::Stack/Properties/RdsDbInstances/DbPassword": "W1011",  # noqa: E501
            "Resources/AWS::OpsWorks::Stack/Properties/CustomCookbooksSource/Password": "W1011",  # noqa: E501
            "Resources/AWS::RDS::DBCluster/Properties/MasterUserPassword": "W1011",  # noqa: E501
            "Resources/AWS::RDS::DBInstance/Properties/MasterUserPassword": "W1011",  # noqa: E501
            "Resources/AWS::Redshift::Cluster/Properties/MasterUserPassword": "W1011",  # noqa: E501
        }
        self._all_refs = [
            "W2010",
        ]
        self.child_rules = dict.fromkeys(list(self.keywords.values()) + self._all_refs)

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": ["string"],
            "enum": validator.context.refs,
        }

    def validator(self, validator: Validator) -> Validator:
        if validator.context.transforms.has_language_extensions_transform():
            supported_functions = [
                "Ref",
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Sub",
                "Fn::ToJsonString",
            ]
        else:
            supported_functions = []
        return validator.evolve(
            context=validator.context.evolve(
                functions=supported_functions,
            ),
        )

    def ref(self, validator, subschema, instance, schema):
        yield from super().validate(validator, subschema, instance, schema)

        _, value = self.key_value(instance)
        if not validator.is_type(value, "string"):
            return

        if value not in validator.context.parameters:
            return

        parameter_type = validator.context.parameters[value].type
        schema_types = self.resolve_type(validator, subschema)
        if not schema_types:
            return
        reprs = ", ".join(repr(type) for type in schema_types)

        if all(
            st not in ["string", "boolean", "integer", "number"] for st in schema_types
        ):
            if parameter_type not in VALID_PARAMETER_TYPES_LIST:
                yield ValidationError(f"{instance!r} is not of type {reprs}")
                return
        elif all(st not in ["array"] for st in schema_types):
            if parameter_type not in [
                x for x in VALID_PARAMETER_TYPES if x not in VALID_PARAMETER_TYPES_LIST
            ]:
                yield ValidationError(f"{instance!r} is not of type {reprs}")
                return

        for rule_id in self._all_refs:
            rule = self.child_rules.get(rule_id)
            if rule:
                yield from rule.validate(validator, {}, instance, schema)

        keyword = validator.context.path.cfn_path_string
        rule_id = self.keywords.get(keyword)
        if rule_id:
            rule = self.child_rules.get(rule_id)
            if rule:
                yield from rule.validate(validator, keyword, instance, schema)
