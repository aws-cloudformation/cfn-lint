"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from  dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class GitSync:

    template_file_path: str = field()
    parameters: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create_from_dict(cls, data: dict[str, Any]) -> "GitSync":

        template_file_path = data.get("template-file-path")
        if not template_file_path:
            raise ValueError("template-file-path is required")
        parameters = data.get("parameters", {})
        tags = data.get("tags", {})
        return cls(template_file_path=template_file_path, parameters=parameters, tags=tags)
