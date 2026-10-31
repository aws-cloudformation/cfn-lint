"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class TableInputTableType(CfnLintKeyword):
    id = "W3707"
    shortdesc = "Validate Glue table TableType is a recognized value"
    description = (
        "Glue stores any string in TableInput.TableType, so a misspelled value "
        "creates a catalog table whose type no query engine recognizes. "
        "Recognized values are the Hive table types and GOVERNED."
    )
    source_url = "https://docs.aws.amazon.com/glue/latest/webapi/API_Table.html"
    tags = ["resources", "glue"]

    _table_types = [
        "EXTERNAL_TABLE",
        "GOVERNED",
        "INDEX_TABLE",
        "MANAGED_TABLE",
        "MATERIALIZED_VIEW",
        "VIRTUAL_VIEW",
    ]

    def __init__(self) -> None:
        super().__init__(["Resources/AWS::Glue::Table/Properties/TableInput"])

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        for scenario in validator.cfn.get_object_without_conditions(
            instance, ["TableType"]
        ):
            table_type = scenario.get("Object").get("TableType")
            if not validator.is_type(table_type, "string"):
                continue
            if table_type in self._table_types:
                continue
            yield ValidationError(
                f"{table_type!r} is not a recognized TableType, Glue stores it "
                f"but query engines look for one of {self._table_types!r}",
                path=deque(["TableType"]),
                instance=table_type,
            )
