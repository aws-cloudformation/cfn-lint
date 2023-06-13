"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any

from cfnlint.template.functions.fn import Fn


class FnGetAtt(Fn):
    def __init__(self, instance: Any, template: Any = None) -> None:
        super().__init__(instance)
