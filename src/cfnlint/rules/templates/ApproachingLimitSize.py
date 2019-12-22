"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS
try:  # pragma: no cover
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path



class LimitSize(CloudFormationLintRule):
    """Check Template Size"""
    id = 'I1002'
    shortdesc = 'Template size limit'
    description = 'Check the size of the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['limits']

    def match(self, cfn):
        """Basic Matching"""
        matches = []

        filename = cfn.filename

        # Only check if the file exists. The template could be passed in using stdIn
        if filename:
            if Path(filename).is_file():
                statinfo = os.stat(filename)
                if statinfo.st_size > 0.9 * LIMITS['template']['body'] and not statinfo.st_size > LIMITS['template']['body']:
                    message = 'The template file size ({0} bytes) is approaching the limit ({1} bytes)'
                    matches.append(RuleMatch(['Template'], message.format(statinfo.st_size, LIMITS['template']['body'])))

        return matches
