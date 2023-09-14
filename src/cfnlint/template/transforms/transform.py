"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

from cfnlint.conditions import Conditions
from cfnlint.graph import Graph
from cfnlint.template.transforms._language_extensions import language_extension
from cfnlint.template.transforms._protocols import Transformer
from cfnlint.template.transforms._sam import sam

LOGGER = logging.getLogger("cfnlint")


class Transform:
    def __init__(self) -> None:
        self.transforms: Mapping[str, Transformer] = {
            "AWS::Serverless-2016-10-31": sam,
            "AWS::LanguageExtensions": language_extension,
        }

    def transform(self, cfn: Any):
        """Transform logic"""
        matches = []
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
