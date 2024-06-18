"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.formatters.base import BaseFormatter


class JUnitFormatter(BaseFormatter):
    """JUnit-style Reports"""

    def _failure_format(self, match):
        """Format output of a failure"""
        formatstr = "{0} at {1}:{2}:{3}"
        return formatstr.format(
            match.message, match.filename, match.linenumber, match.columnnumber
        )

    def print_matches(self, matches, rules, config):
        """Output all the matches"""

        try:
            from junit_xml import TestCase, TestSuite, to_xml_report_string
        except ImportError as e:
            raise ImportError("Missing optional dependencies junit") from e

        if not rules:
            return None

        test_cases = []
        for rule in rules.values():
            if rule.id not in rules.used_rules:
                if not rule.id:
                    continue
                test_case = TestCase(name=f"{rule.id} {rule.shortdesc}")

                if rule.experimental:
                    test_case.add_skipped_info(
                        message="Experimental rule - not enabled"
                    )
                else:
                    test_case.add_skipped_info(message="Ignored rule")
                test_cases.append(test_case)
            else:
                test_case = TestCase(
                    name=f"{rule.id} {rule.shortdesc}",
                    allow_multiple_subelements=True,
                    url=rule.source_url,
                )
                for match in matches:
                    if match.rule.id == rule.id:
                        test_case.add_failure_info(
                            message=self._failure_format(match),
                            failure_type=match.message,
                        )
                test_cases.append(test_case)

        test_suite = TestSuite("CloudFormation Lint", test_cases)

        return to_xml_report_string([test_suite], prettyprint=True)
