"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import logging
from typing import Any, Callable, List, Mapping

from cfnlint.conditions import Conditions
from cfnlint.graph import Graph
from cfnlint.match import Match
from cfnlint.template.transforms._sam import sam
from cfnlint.template.transforms._types import TransformResult

LOGGER = logging.getLogger("cfnlint")


class Transform:
    def __init__(self) -> None:
        self.transforms: Mapping[str, Callable[[Any], TransformResult]] = {
            "AWS::Serverless-2016-10-31": sam,
        }

    def transform(self, cfn: Any) -> List[Match]:
        """Transform logic"""
        matches: List[Match] = []
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
            if matches:
                return matches
            cfn.template = template

        LOGGER.info("Transformed template: %s", cfn.template)
        cfn.graph = Graph(cfn)
        cfn.conditions = Conditions(cfn)
        return matches
