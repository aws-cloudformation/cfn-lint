"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import regex as re

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class DynamicReferenceSecretsManagerArn(CloudFormationLintRule):
    id = "W1051"
    shortdesc = (
        "Validate dynamic references to secrets manager "
        "are not used when a secrets manager ARN was expected"
    )
    description = (
        "Certain properties expect a secret manager ARN. This rule "
        "validates if you may be accidently using a secret in place "
        "of the ARN"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-secretsmanager"
    tags = ["functions", "dynamic reference"]

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):

        if "Fn::Sub" == validator.context.path.path[-1]:
            if not re.match(r"^(\\\")?{{resolve:secretsmanager:.*}}(\\\")?$", instance):
                return

        if len(validator.context.path.path) < 3:
            return

        if (
            validator.context.path.path[0] != "Resources"
            or validator.context.path.path[2] != "Properties"
        ):
            return

        fields = [
            "SecretArn",
            "SecretARN",
            "SecretsManagerSecretId",
            "SecretsManagerOracleAsmSecretId",
            "SecretsManagerSecurityDbEncryptionSecretId",
            "SecretsManagerConfiguration",
        ]

        for field in fields:
            if any(field == p for p in validator.context.path.path):
                yield ValidationError(
                    (
                        f"Dynamic reference {instance!r} to secrets manager when "
                        f"the field {field!r} expects the ARN to the secret and "
                        "not the secret"
                    ),
                    rule=self,
                )
