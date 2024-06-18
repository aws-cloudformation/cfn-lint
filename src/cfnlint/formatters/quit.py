"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.formatters.base import BaseFormatter


class QuietFormatter(BaseFormatter):
    """Quiet Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = "{0} {1}:{2}"
        return formatstr.format(match.rule, match.filename, match.linenumber)
