"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from typing import Any, Iterable, List

from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn
from cfnlint.template.functions.value import Value, ValueType


class Ref(Fn):
    def __init__(self, instance: Any, template: Any = None) -> None:
        super().__init__(instance)
        self._supported_functions: List[str] = []
        if not isinstance(self._instance, str):
            return

        self._value = instance
        self._account_id = "123456789012"

        self._values: List[Value] = []
        if template is None:
            return
        v = template.get_parameters().get(self._value, {})
        p_type = v.get("Type")
        p_default = v.get("Default")
        p_allowed_values = v.get("AllowedValues")
        if not (p_allowed_values or p_default):
            return
        if p_default and isinstance(p_default, (str, int, float)):
            p_default = str(p_default)
            if p_type == "CommaDelimitedList":
                p_default = p_default.split(",")
            self._values.append(
                Value(
                    value=p_default,
                    value_type=ValueType.PATH,
                    path=deque(["Parameters", self._instance, "Default"]),
                )
            )
        if p_allowed_values and isinstance(p_allowed_values, list):
            for i, av in enumerate(p_allowed_values):
                if p_type == "CommaDelimitedList":
                    av = av.split(",")
                self._values.append(
                    Value(
                        value=av,
                        value_type=ValueType.PATH,
                        path=deque(["Resources", self._instance, "AllowedValues", i]),
                    )
                )

    @property
    def is_valid(self) -> bool:
        if not isinstance(self._instance, str):
            return False
        return True

    def _get_aws_partition(self, region: str) -> str:
        if region in ("us-gov-east-1", "us-gov-west-1"):
            return "aws-us-gov"
        if region in ("cn-north-1", "cn-northwest-1"):
            return "aws-cn"
        else:
            return "aws"

    def _get_url_suffix(self, region: str) -> str:
        if region in ("cn-north-1", "cn-northwest-1"):
            return "amazonaws.com.cn"

        return "amazonaws.com"

    def get_value(self, fns, region: str) -> Iterable[Value]:
        if not self.is_valid:
            raise Unpredictable(f"Ref is not valid {self._instance!r}")

        if self._value == "AWS::Region":
            yield Value(value=region, value_type=ValueType.PSEUDO_PARAMETER)
            return

        if self._value == "AWS::AccountId":
            yield Value(value=self._account_id, value_type=ValueType.PSEUDO_PARAMETER)
            return

        if self._value == "AWS::NotificationARNs":
            yield Value(
                value=[
                    f"arn:{self._get_aws_partition(region)}:sns:{region}:{self._account_id}:notification"
                ],
                value_type=ValueType.PSEUDO_PARAMETER,
            )
            return

        if self._value == "AWS::NoValue":
            return

        if self._value == "AWS::Partition":
            yield Value(
                value=self._get_aws_partition(region),
                value_type=ValueType.PSEUDO_PARAMETER,
            )
            return

        if self._value == "AWS::StackId":
            yield Value(
                value=(
                    f"arn:{self._get_aws_partition(region)}:cloudformation:"
                    f"{region}:{self._account_id}:"
                    "stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
                ),
                value_type=ValueType.PSEUDO_PARAMETER,
            )
            return

        if self._value == "AWS::StackName":
            yield Value(value="teststack", value_type=ValueType.PSEUDO_PARAMETER)
            return

        if self._value == "AWS::URLSuffix":
            yield Value(
                value=self._get_url_suffix(region),
                value_type=ValueType.PSEUDO_PARAMETER,
            )
            return

        if self._values:
            yield from iter(self._values)
