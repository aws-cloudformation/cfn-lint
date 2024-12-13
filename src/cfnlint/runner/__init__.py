"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

__all__ = ["main", "Runner", "TemplateRunner"]

from cfnlint.runner.cli import Runner, main
from cfnlint.runner.template import TemplateRunner
