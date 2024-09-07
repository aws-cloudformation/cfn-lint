"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ecs_service
from cfnlint.jsonschema import ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ServiceHealthCheckGracePeriodSeconds(CfnLintJsonSchema):
    id = "E3056"
    shortdesc = (
        "ECS service using HealthCheckGracePeriodSeconds "
        "must also have LoadBalancers specified"
    )
    description = (
        "When using a HealthCheckGracePeriodSeconds on an ECS "
        "service, the service must also have a LoadBalancers specified "
        "with at least one LoadBalancer in the array."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ecs-service.html#cfn-ecs-service-healthcheckgraceperiodseconds"
    tags = ["properties", "ecs", "service", "container"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ECS::Service/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ecs_service,
                filename="healthcheckgraceperiodseconds.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        cfn_validator = self.extend_validator(
            validator=validator.evolve(
                function_filter=validator.function_filter.evolve(
                    validate_dynamic_references=False,
                    add_cfn_lint_keyword=False,
                )
            ),
            schema=self._schema,
            context=validator.context.evolve(
                functions=["Fn::If", "Ref"],
                strict_types=True,
            ),
        )

        yield from self._iter_errors(cfn_validator, instance)
