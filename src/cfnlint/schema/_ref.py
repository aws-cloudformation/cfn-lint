"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cfnlint.schema import Schema


class Ref:

    def __init__(self, schema: "Schema") -> None:
        primary_ids = schema.schema.get("primaryIdentifier", [])
        if len(primary_ids) > 1:
            self._ref = {"type": "string"}
        else:
            for primary_id in primary_ids:
                self._ref = schema.resolver.resolve_cfn_pointer(primary_id)

    @property
    def ref(self) -> dict[str, Any]:
        return self._ref
