"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_replica_mode_engines = {"oracle", "custom-oracle", "db2"}


class DbInstanceReplicaModeIgnored(CfnLintKeyword):
    id = "W3699"
    shortdesc = "ReplicaMode is ignored for non-Oracle/Db2 engines"
    description = (
        "When ReplicaMode is specified with engines other than Oracle or Db2, "
        "the value is silently ignored. Remove ReplicaMode or use an engine "
        "that supports it."
    )
    source_url = "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-read-replicas.html"
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::RDS::DBInstance/Properties",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        if "ReplicaMode" not in instance:
            return

        engine = instance.get("Engine")
        if not isinstance(engine, str):
            return

        engine_lower = engine.lower()
        if any(engine_lower.startswith(e) for e in _replica_mode_engines):
            return

        yield ValidationError(
            f"'ReplicaMode' is ignored when 'Engine' is {engine!r}",
            path=["ReplicaMode"],
        )
