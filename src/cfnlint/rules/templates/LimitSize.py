"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os
from pathlib import Path

from cfnlint._typing import RuleMatches
from cfnlint.helpers import LIMITS
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class LimitSize(CloudFormationLintRule):
    """Check Template Size"""

    id = "E1002"
    shortdesc = "Validate if a template size is too large"
    description = "Check the size of the template is less than the upper limit"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["limits"]

    def __init__(self):
        """Init"""
        super().__init__()
        # Defaults to the limit for a template read from S3. Templates that are
        # always passed inline can set this to LIMITS["template"]["inline_body"]
        self.config_definition = {
            "max_size": {
                "default": LIMITS["template"]["body"],
                "type": "integer",
            },
        }
        self.configure()

    def match(self, cfn: Template) -> RuleMatches:
        matches = []
        # Only check if the file exists. The template could be passed in using stdIn
        if cfn.filename:
            if Path(cfn.filename).is_file():
                statinfo = os.stat(cfn.filename)
                if statinfo.st_size > self.config["max_size"]:
                    message = (
                        "The template file size ({0} bytes) exceeds the limit ({1}"
                        " bytes)"
                    )
                    matches.append(
                        RuleMatch(
                            ["Template"],
                            message.format(statinfo.st_size, self.config["max_size"]),
                        )
                    )
        return matches
