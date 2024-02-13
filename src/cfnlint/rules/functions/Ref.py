"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.helpers import VALID_PARAMETER_TYPES, VALID_PARAMETER_TYPES_LIST
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.jsonschema._validators_cfn import Ref as RefValidator
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
        self._ref = RefValidator()
        self.keywords = {
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::Batch::ComputeEnvironment/Properties/ComputeResources/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::Cloud9::EnvironmentEC2/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::Instance/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::ImageBuilder::Image/Properties/ImageId": "W2506",  # noqa: E501
            "Resources/AWS::NimbleStudio::StreamingImage/Properties/Ec2ImageId": "W2506",  # noqa: E501
        }
        self.child_rules = dict.fromkeys(list(self.keywords.values()))

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

        keyword = self.get_keyword(validator)
        for rule in self.child_rules.values():
            if rule is None:
                continue
            if not rule.id:
                continue

            for rule_keyword in self.keywords:
                if rule_keyword == keyword:
                    yield from rule.validate(validator, keyword, instance, schema)
