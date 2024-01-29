"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations
import pathlib
from typing import Any, Sequence

from cfnlint.helpers import load_plugins, load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema._validators import type
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


class CfnLintKeyword(CloudFormationLintRule):

    def __init__(self, keywords: Sequence[str] | None = None) -> None:
        super().__init__()
        self.keywords = keywords

    def message(self, instance: Any, err: ValidationError) -> str:
        return self.shortdesc
