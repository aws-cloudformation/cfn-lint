"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

import regex as re

from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

# CloudFormation resource type namespace (AWS::<Namespace>::...) to the
# ARN service prefix of the AWS services that EventBridge rules support as
# targets.
# https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html
_TARGET_NAMESPACES: dict[str, str] = {
    "ApiGateway": "execute-api",
    "AppSync": "appsync",
    "Batch": "batch",
    "CodeBuild": "codebuild",
    "CodePipeline": "codepipeline",
    "ECS": "ecs",
    # API destinations, event buses and the EC2/EBS API call targets
    # (arn:aws:events:<region>:<account>:target/...)
    "Events": "events",
    "Glue": "glue",
    "ImageBuilder": "imagebuilder",
    "Inspector": "inspector",
    "Kinesis": "kinesis",
    "KinesisFirehose": "firehose",
    "Lambda": "lambda",
    "Logs": "logs",
    "Redshift": "redshift",
    "RedshiftServerless": "redshift-serverless",
    "SageMaker": "sagemaker",
    "SNS": "sns",
    "SQS": "sqs",
    "SSM": "ssm",
    "SSMIncidents": "ssm-incidents",
    "StepFunctions": "states",
}

_TARGET_SERVICES = frozenset(_TARGET_NAMESPACES.values())

# Namespaces whose Ref/GetAtt values are pass through values that can
# resolve to anything (stack outputs, custom resource attributes, ...)
# or are expanded by a transform
_SKIP_NAMESPACES = frozenset(["CloudFormation", "Serverless"])

# Resource types outside those namespaces that have pass through attributes
# (GetAtt Outputs.<Name>)
_SKIP_TYPES = frozenset(["AWS::ServiceCatalog::CloudFormationProvisionedProduct"])

_SUB_VARIABLE = re.compile(r"\$\{[^}]*\}")
_SUB_SINGLE_VARIABLE = re.compile(r"^\$\{([^!}][^}]*)\}$")


class RuleTargetArnService(CfnLintKeyword):
    id = "E3730"
    shortdesc = "Validate EventBridge rule targets are supported services"
    description = (
        "EventBridge rules can only send events to a specific set of AWS "
        "services. Validate that each target 'Arn' of an AWS::Events::Rule "
        "is for a supported service, such as Lambda, SQS, SNS, or Step "
        "Functions, and not for a resource like an IAM role. Values that "
        "can't be resolved are not checked."
    )
    source_url = (
        "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets.html"
    )
    tags = ["resources", "events"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Events::Rule/Properties"],
        )

    def _resource_name(self, validator: Validator, instance: Any) -> str | None:
        """Return the logical ID of the resource a target Arn points to"""
        fn_k, fn_v = is_function(instance)
        if fn_k == "Ref":
            name = fn_v
        elif fn_k == "Fn::GetAtt":
            if validator.is_type(fn_v, "string"):
                fn_v = fn_v.split(".", 1)
            if not validator.is_type(fn_v, "array") or not fn_v:
                return None
            name = fn_v[0]
        elif fn_k == "Fn::Sub":
            # Only handle a Sub that is exactly one variable
            # e.g. !Sub "${MyRole.Arn}"
            sub_vars: Any = {}
            if validator.is_type(fn_v, "array") and len(fn_v) == 2:
                fn_v, sub_vars = fn_v
            if not validator.is_type(fn_v, "string"):
                return None
            match = _SUB_SINGLE_VARIABLE.match(fn_v)
            if not match:
                return None
            name = match.group(1).split(".", 1)[0]
            if validator.is_type(sub_vars, "object") and name in sub_vars:
                return None
        else:
            return None

        if not isinstance(name, str):
            return None
        if name not in validator.context.resources:
            return None
        return name

    @staticmethod
    def _arn_service(validator: Validator, instance: Any) -> str | None:
        """Return the service of a literal ARN or a Sub with a literal service"""
        fn_k, fn_v = is_function(instance)
        if fn_k == "Fn::Sub":
            if validator.is_type(fn_v, "array") and fn_v:
                fn_v = fn_v[0]
            instance = fn_v
        elif fn_k is not None:
            return None

        if not validator.is_type(instance, "string"):
            return None

        # Replace Sub variables (which can contain ':') so the ARN can be
        # split into its parts. ${AWS::Partition} is the only variable
        # allowed before the service, as any other variable could span
        # several parts (e.g. "arn:${PartitionAndService}:...")
        instance = instance.replace("${AWS::Partition}", "aws")
        parts = _SUB_VARIABLE.sub("\0", instance).split(":", 5)
        if len(parts) < 6 or parts[0] != "arn" or "\0" in parts[1]:
            return None

        service = parts[2]
        if not service or "\0" in service:
            return None
        return service

    def _target_arns(
        self, validator: Validator, instance: Any
    ) -> Iterator[tuple[Any, Validator]]:
        for target, target_validator in get_value_from_path(
            validator, instance, deque(["Targets", "*"])
        ):
            for arn, arn_validator in get_value_from_path(
                target_validator, target, deque(["Arn"])
            ):
                if arn is None:
                    continue
                yield arn, arn_validator

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for arn, arn_validator in self._target_arns(validator, instance):
            name = self._resource_name(arn_validator, arn)
            if name is not None:
                resource_type = arn_validator.context.resources[name].type
                parts = resource_type.split("::")
                if len(parts) != 3 or parts[0] != "AWS":
                    continue
                if parts[1] in _SKIP_NAMESPACES or resource_type in _SKIP_TYPES:
                    continue
                if parts[1] in _TARGET_NAMESPACES:
                    continue
                yield ValidationError(
                    (
                        f"Resource {name!r} of type {resource_type!r} is not a "
                        "supported target for an EventBridge rule"
                    ),
                    path_override=arn_validator.context.path.path,
                    rule=self,
                )
                continue

            service = self._arn_service(arn_validator, arn)
            if service is None or service in _TARGET_SERVICES:
                continue
            yield ValidationError(
                (
                    f"{service!r} is not a supported service for an "
                    "EventBridge rule target"
                ),
                path_override=arn_validator.context.path.path,
                rule=self,
            )
