"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

__all__ = [
    "run_template_by_file_path",
    "run_template_by_data",
    "run_template_by_pipe",
    "run_template_by_file_paths",
]

from cfnlint.runner.template.runner import (
    run_template_by_data,
    run_template_by_file_path,
    run_template_by_file_paths,
    run_template_by_pipe,
)
