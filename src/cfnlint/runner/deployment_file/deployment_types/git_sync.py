"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.runner.deployment_file.deployment import Deployment


def create_deployment_from_git_sync(data: dict[str, Any]) -> Deployment:

    template_file_path = data.get("template-file-path")
    if not template_file_path:
        raise ValueError("template-file-path is required")
    parameters = data.get("parameters", {})
    tags = data.get("tags", {})
    return Deployment(
        template_file_path=template_file_path, parameters=parameters, tags=tags
    )
