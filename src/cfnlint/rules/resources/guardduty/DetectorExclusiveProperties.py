"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations
from typing import Any
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema

class DetectorExclusiveProperties(CfnLintJsonSchema):
    id = "E3063"
    shortdesc = "Validate GuardDuty Detector property exclusivity"
    description = (
        "The request failed because both DataSources and Features were provided. "
        "You can provide only one; it is recommended to use Features."
    )
    source_url = "https://docs.aws.amazon.com/pt_br/guardduty/latest/ug/guardduty-features-activation-model.html"
    tags = ["resources", "guardduty"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::GuardDuty::Detector/Properties",
            ],
            all_matches=True,
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if "DataSources" in instance and "Features" in instance:
            yield ValidationError(
                "Both 'DataSources' and 'Features' were provided. "
                "You can provide only one; it is recommended to use 'Features'.",
                rule=self,
            )