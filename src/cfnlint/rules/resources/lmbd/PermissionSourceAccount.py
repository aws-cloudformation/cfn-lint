"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class PermissionSourceAccount(CfnLintKeyword):

    id = "W3663"
    shortdesc = "Validate SourceAccount is required property"
    description = (
        "When configuration a Lambda permission with a SourceArn "
        "that doesn't have an AccountId you should also specify "
        "the SourceAccount"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-permission.html#cfn-lambda-permission-sourceaccount"
    tags = ["resources", "lambda", "permission"]

    def __init__(self):
        super().__init__(
            keywords=["Resources/AWS::Lambda::Permission/Properties"],
        )

    def _validate_is_gettatt_to_bucket(self, validator: Validator, value: Any) -> bool:
        value = ensure_list(value)[0].split(".")[0]

        resource = validator.context.resources[value]
        if resource.type == "AWS::S3::Bucket":
            return True
        return False

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        for scenario in validator.cfn.get_object_without_conditions(
            instance, ["SourceArn", "SourceAccount"]
        ):
            if scenario.get("Scenario"):
                scenario_validator = validator.evolve(
                    context=validator.context.evolve(
                        conditions=validator.context.conditions.evolve(
                            status=scenario.get("Scenario")
                        )
                    )
                )
            else:
                scenario_validator = validator.evolve()

            source_arn = scenario.get("Object").get("SourceArn")
            source_account = scenario.get("Object").get("SourceAccount")
            if not source_arn:
                continue

            if isinstance(source_arn, str):
                if re.search(r":\d{12}:", source_arn):
                    continue

            fn_k, fn_v = is_function(source_arn)
            if fn_k is not None:
                if fn_k == "Fn::GetAtt":
                    if not self._validate_is_gettatt_to_bucket(
                        scenario_validator, fn_v
                    ):
                        continue
                else:
                    continue

            if not source_account:
                yield ValidationError(
                    "'SourceAccount' is a required property",
                    validator="required",
                    rule=self,
                )
