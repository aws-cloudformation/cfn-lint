"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import regex as re

from cfnlint.formatters.base import BaseFormatter


class ParseableFormatter(BaseFormatter):
    """Parseable Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = "{0}:{1}:{2}:{3}:{4}:{5}:{6}"
        return formatstr.format(
            match.filename,
            match.linenumber,
            match.columnnumber,
            match.linenumberend,
            match.columnnumberend,
            match.rule.id,
            re.sub(r"(\r*\n)+", " ", match.message),
        )
