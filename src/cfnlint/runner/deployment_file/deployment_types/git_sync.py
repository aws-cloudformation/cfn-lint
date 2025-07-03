"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.deployment_files
from cfnlint._typing import RuleMatches
from cfnlint.helpers import load_resource
from cfnlint.rules.deployment_files.Configuration import Configuration
from cfnlint.runner.deployment_file.deployment import DeploymentFileData


def create_deployment_from_git_sync(
    data: dict[str, Any],
) -> tuple[DeploymentFileData | None, RuleMatches | None]:

    schema = load_resource(cfnlint.data.schemas.other.deployment_files, "git_sync.json")
    matches = Configuration().validate_deployment_file(data, schema)
    if matches:
        return None, matches

    template_file_path: str = data.get("template-file-path", "")
    parameters: dict[str, Any] = data.get("parameters", {})
    tags: dict[str, Any] = data.get("tags", {})
    return (
        DeploymentFileData(
            template_file_path=template_file_path, parameters=parameters, tags=tags
        ),
        None,
    )
