"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, Iterable

from cfnlint.context import Context
from cfnlint.helpers import FUNCTIONS


def value(obj: Any, context: Context) -> Iterable[Any]:
    if isinstance(obj, dict):
        if len(obj) == 1:
            k = next(iter(obj))
            if k in FUNCTIONS:
                if k == "Ref":
                    yield from ref.value(obj[k], context=context)
                return

    yield value


def ref(instance: Any, context: Context) -> Iterable[Any]:
    if isinstance(instance, dict):
        if len(instance) != 1:
            return

        k = next(iter(instance))
        for v in value(instance[k], context):
            yield from ref(v, context)

    if isinstance(instance, str):
        if instance in context.refs:
            yield from iter(context.refs[instance])
