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


class InlineLimitSize(CloudFormationLintRule):
    """Check if a Template is too large to pass inline"""

    id = "I1004"
    shortdesc = "Validate if a template is too large to deploy inline"
    description = (
        "Check if the template is larger than CloudFormation accepts in the "
        "TemplateBody request parameter, so it must be uploaded to S3 and "
        "deployed with TemplateURL or --s3-bucket"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["limits"]

    def match(self, cfn: Template) -> RuleMatches:
        matches = []
        # Only check if the file exists. The template could be passed in using stdIn
        if cfn.filename:
            if Path(cfn.filename).is_file():
                # TemplateBody is limited in characters, while `aws cloudformation
                # deploy` refuses a file over the same number of bytes. A UTF-8
                # file has at least as many bytes as characters, so measuring
                # bytes covers both. Past the S3 limit, E1002 reports the file.
                statinfo = os.stat(cfn.filename)
                if (
                    LIMITS["template"]["inline_body"]
                    < statinfo.st_size
                    <= LIMITS["template"]["body"]
                ):
                    # The message leaves out the file size, which grows with CRLF
                    # line endings, so a template reads the same on every platform
                    message = (
                        "The template file is larger than {0} bytes, the limit for"
                        " a template body passed inline. Upload it to S3 and deploy"
                        " it with 'TemplateURL' or '--s3-bucket'"
                    )
                    matches.append(
                        RuleMatch(
                            ["Template"],
                            message.format(LIMITS["template"]["inline_body"]),
                        )
                    )
        return matches
