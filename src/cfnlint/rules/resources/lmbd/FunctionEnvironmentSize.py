"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import re
from typing import Any

from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_SCALAR_TYPES = (str, int, float, bool)
_SUB_TOKEN_RE = re.compile(r"\$\{([^}]+)\}")


def _json_str_len(value: str) -> int:
    return len(json.dumps(value, ensure_ascii=False).encode("utf-8"))


def _resolve_item_min_string(validator: Validator, value: Any) -> str:
    if isinstance(value, _SCALAR_TYPES):
        return str(value)
    if is_function(value)[0] is not None:
        return _resolve_min_string(validator, value)
    return ""


def _min_join_string(validator: Validator, fn_v: Any) -> str:
    if not isinstance(fn_v, list) or len(fn_v) != 2:
        return ""
    delimiter, values = fn_v
    delim_str = (
        delimiter
        if isinstance(delimiter, str)
        else (
            _resolve_min_string(validator, delimiter)
            if is_function(delimiter)[0] is not None
            else ""
        )
    )
    if not isinstance(values, list):
        return ""
    return delim_str.join(_resolve_item_min_string(validator, item) for item in values)


def _min_sub_string(validator: Validator, fn_v: Any) -> str:
    if isinstance(fn_v, str):
        pattern = fn_v
        local_map: dict[str, Any] = {}
    elif (
        isinstance(fn_v, list)
        and len(fn_v) == 2
        and isinstance(fn_v[0], str)
        and isinstance(fn_v[1], dict)
    ):
        pattern = fn_v[0]
        local_map = fn_v[1]
    else:
        return ""

    def _replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token.startswith("!"):
            return f"${{{token[1:]}}}"
        name = token.strip()
        if name in local_map:
            return _resolve_item_min_string(validator, local_map[name])
        if "." not in name:
            return _resolve_min_string(validator, {"Ref": name})
        return ""

    return _SUB_TOKEN_RE.sub(_replace, pattern)


def _min_if_string(validator: Validator, fn_v: Any) -> str:
    if not isinstance(fn_v, list) or len(fn_v) != 3:
        return ""
    cond_name = fn_v[0]
    branch_values: list[str] = []
    for idx, is_true in ((1, True), (2, False)):
        if isinstance(cond_name, str):
            try:
                conds = validator.context.conditions.evolve({cond_name: is_true})
            except Unsatisfiable:
                continue
            branch_validator = validator.evolve(
                context=validator.context.evolve(conditions=conds)
            )
        else:
            branch_validator = validator
        branch_values.append(_resolve_item_min_string(branch_validator, fn_v[idx]))
    if not branch_values:
        return ""
    return min(branch_values, key=_json_str_len)


def _resolve_min_string(validator: Validator, value: Any) -> str:
    if isinstance(value, str):
        return value

    candidates = [
        str(r_val)
        for r_val, _, r_err in validator.resolve_value(value)
        if r_err is None and isinstance(r_val, _SCALAR_TYPES)
    ]
    if candidates:
        return min(candidates, key=_json_str_len)

    fn_k, fn_v = is_function(value)
    if fn_k == "Fn::Join":
        return _min_join_string(validator, fn_v)
    if fn_k == "Fn::Sub":
        return _min_sub_string(validator, fn_v)
    if fn_k == "Fn::If":
        return _min_if_string(validator, fn_v)
    return ""


class FunctionEnvironmentSize(CfnLintKeyword):
    """Check Lambda environment variables total size does not exceed 4 KB"""

    id = "E3697"
    shortdesc = "Validate Lambda environment variables do not exceed 4 KB"
    description = (
        "AWS Lambda limits the total size of all environment variables "
        "to 4 KB. If this limit is exceeded, the deployment will fail. "
        "This rule measures the size of the compact JSON encoding of the "
        "variables and validates the total does not exceed 4096 bytes."
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html"
    )
    tags = ["resources", "lambda"]

    def __init__(self):
        """Init"""
        super().__init__(
            ["Resources/AWS::Lambda::Function/Properties/Environment/Variables"]
        )

    def validate(
        self,
        validator: Validator,
        keywords: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        max_size = 4096
        max_total_size = 0
        for (
            scenario,
            conds,
        ) in validator.context.conditions.evolve_from_instance(
            instance, context=validator.context
        ):
            if not isinstance(scenario, dict):
                continue

            scenario_validator = validator.evolve(
                context=validator.context.evolve(conditions=conds)
            )
            variables: dict[str, str] = {}
            for key, value in scenario.items():
                if not isinstance(key, str):
                    continue
                if isinstance(value, str):
                    variables[key] = value
                elif is_function(value)[0] is not None:
                    variables[key] = _resolve_min_string(scenario_validator, value)

            # Lambda measures the variables as compact JSON, so the structural
            # characters (quotes, colons, commas and braces) count toward the
            # limit. Measure the UTF-8 byte length of the compact encoding
            # instead of summing key and value lengths.
            total_size = len(
                json.dumps(variables, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
            )
            max_total_size = max(max_total_size, total_size)

        if max_total_size > max_size:
            yield ValidationError(
                f"Lambda environment variables total size ({max_total_size}) "
                f"exceeds the 4 KB ({max_size} bytes) limit",
                rule=self,
            )
