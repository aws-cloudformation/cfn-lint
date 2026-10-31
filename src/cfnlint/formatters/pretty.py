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

        try:
            templates = config.templates
        except ValueError:
            # The template glob could not be resolved. That failure is
            # already reported as a match, so there are no templates to
            # count. Re-reading the property here must not raise again
            # and turn the error report itself into a crash.
            templates = []

        # ruff: noqa: E501
        results.append(
            "Cfn-lint scanned"
            f" {colored(1 if templates is None else len(templates), color.bold_reset)}"
            " templates against "
            f"{colored(len(rules.used_rules), color.bold_reset)} rules and found "
            f"{colored(len([i for i in matches if i.rule.severity.lower() == 'error']), color.error)} "
            "errors,"
            f" {colored(len([i for i in matches if i.rule.severity.lower() == 'warning']), color.warning)} "
            f"warnings, and "
            f"{colored(len([i for i in matches if i.rule.severity.lower() == 'informational']), color.informational)} "
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

            # A config-error match (e.g. E0003 for an unresolvable glob)
            # carries no filename. Render it as "None", matching the
            # parseable formatter, instead of appending a None that
            # breaks the join below when stdout is not a tty.
            output.append(colored(str(filename), color.underline_reset))
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
