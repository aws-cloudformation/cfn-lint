"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import itertools
import operator

from cfnlint.formatters._utils import color, colored
from cfnlint.formatters.base import BaseFormatter


class PrettyFormatter(BaseFormatter):
    """Generic Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = "{0}{1}{2}"
        pos = f"{match.linenumber}:{match.columnnumber}:"
        return formatstr.format(
            colored(f"{pos:20}", color.reset),
            colored(f"{match.rule.id:10}", getattr(color, match.rule.severity.lower())),
            match.message,
        )

    def print_matches(self, matches, rules, config):
        results = self._format_matches(matches)

        # ruff: noqa: E501
        results.append(
            f"Cfn-lint scanned {colored(1 if config.templates is None else len(config.templates), color.bold_reset)}"
            " templates against "
            f"{colored(len(rules.used_rules), color.bold_reset)} rules and found "
            f'{colored(len([i for i in matches if i.rule.severity.lower() == "error"]), color.error)} '
            f'errors, {colored(len([i for i in matches if i.rule.severity.lower() == "warning"]), color.warning)} '
            f"warnings, and "
            f'{colored(len([i for i in matches if i.rule.severity.lower() == "informational"]), color.informational)} '
            f"informational violations"
        )
        return "\n".join(results)

    def _format_matches(self, matches):
        """Output all the matches"""
        output = []

        # This better be sorted
        for filename, file_matches in itertools.groupby(
            matches, key=operator.attrgetter("filename")
        ):
            levels = {"error": [], "warning": [], "informational": [], "unknown": []}

            output.append(colored(filename, color.underline_reset))
            for match in file_matches:
                level = match.rule.severity.lower()
                if level not in ["error", "warning", "informational"]:
                    level = "unknown"
                levels[level].append(match)
            for _, all_matches in levels.items():
                for match in all_matches:
                    output.extend([self._format(match)])

            output.append("")  # Newline after each group

        return output
