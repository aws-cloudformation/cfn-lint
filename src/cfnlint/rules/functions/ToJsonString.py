"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.helpers import PSEUDOPARAMS
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.languageExtensions import LanguageExtensions
from cfnlint.rules.functions._BaseFn import BaseFn


class ToJsonString(BaseFn):
    """Check if ToJsonString values are correct"""

    id = "E1031"
    shortdesc = "ToJsonString validation of parameters"
    description = "Making sure Fn::ToJsonString is configured correctly"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html"
    tags = ["functions", "toJsonString"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::ToJsonString",
            ("string",),
            (
                "Fn::FindInMap",
                "Fn::GetAtt",
                "Fn::GetAZs",
                "Fn::If",
                "Fn::Select",
                "Fn::Split",
                "Ref",
            ),
        )

    def match(self, cfn):
        has_language_extensions_transform = cfn.has_language_extensions_transform()
        unsupported_pseudo_parameters = ["AWS::NotificationARNs"]

        matches = []
        intrinsic_function = "Fn::ToJsonString"
        fn_toJsonString_objects = cfn.search_deep_keys(intrinsic_function)

        for fn_toJsonString_object in fn_toJsonString_objects:
            tree = fn_toJsonString_object[:-1]
            fn_toJsonString_object_value = fn_toJsonString_object[-1]
            LanguageExtensions.validate_transform_is_declared(
                self,
                has_language_extensions_transform,
                matches,
                tree,
                intrinsic_function,
            )
            LanguageExtensions.validate_type(
                self, fn_toJsonString_object_value, matches, tree, intrinsic_function
            )
            LanguageExtensions.validate_pseudo_parameters(
                self,
                fn_toJsonString_object_value,
                matches,
                tree,
                unsupported_pseudo_parameters,
                intrinsic_function,
            )
        return matches

    def schema(self, validator: Validator, instance: Any) -> Dict[str, Any]:
        return {
            "type": ["array", "object"],
            "minItems": 1,
            "minProperties": 1,
        }

    def validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(
                functions=self.functions,
                pseudo_parameters=set(
                    [sp for sp in PSEUDOPARAMS if sp != "AWS::NotificationARNs"]
                ),
            ),
        )

    def fn_tojsonstring(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                ),
                validator=self.fn.py,
            )
            return

        yield from super().validate(validator, s, instance, schema)
