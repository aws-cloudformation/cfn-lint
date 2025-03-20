"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Mapping

from cfnlint.conditions import Conditions
from cfnlint.context import create_context_for_template
from cfnlint.graph import Graph
from cfnlint.helpers import (
    TRANSFORM_LANGUAGE_EXTENSION,
    TRANSFORM_SAM,
    format_json_string,
)
from cfnlint.match import Match
from cfnlint.template.transforms._language_extensions import language_extension
from cfnlint.template.transforms._sam import sam
from cfnlint.template.transforms._types import TransformResult

LOGGER = logging.getLogger("cfnlint")


class Transform:
    def __init__(self) -> None:
        self.transforms: Mapping[str, Callable[[Any], TransformResult]] = {
            TRANSFORM_SAM: sam,
            TRANSFORM_LANGUAGE_EXTENSION: language_extension,
        }

    def transform(self, cfn: Any) -> list[Match]:
        """Transform logic"""
        matches: list[Match] = []
        transform_declaration = cfn.template.get("Transform", [])
        transform_type = (
            transform_declaration
            if isinstance(transform_declaration, list)
            else [transform_declaration]
        )

        if not transform_type:
            return matches

        cfn.transform_pre["Globals"] = cfn.template.get("Globals", {})
        for name in transform_type:
            if not isinstance(name, str):
                continue
            transform = self.transforms.get(name)
            if not transform:
                continue

            matches, template = transform(cfn)
            LOGGER.debug(
                "Transformed template from %s: \n%s",
                name,
                format_json_string(cfn.template),
            )
            if matches:
                return matches
            cfn.template = template

        if len(transform_type) > 1:
            # SAM will erase the entire Transform section
            # this sets it back with all transforms except SAM
            cfn.template["Transform"] = [
                t for t in transform_type if t != TRANSFORM_SAM
            ]

        LOGGER.info("Transformed template: \n%s", format_json_string(cfn.template))
        cfn.graph = Graph(cfn)
        cfn.conditions = Conditions(cfn)
        cfn.context = create_context_for_template(cfn)
        return matches
