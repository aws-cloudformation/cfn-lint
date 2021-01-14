"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import itertools
import json
import operator
import re
import sys
from junit_xml import TestSuite, TestCase, to_xml_report_string
from cfnlint.rules import Match


class color(object):
    error = '\033[31m'
    warning = '\033[33m'
    informational = '\033[34m'
    unknown = '\033[37m'
    green = '\033[32m'
    reset = '\033[0m'
    bold_reset = '\033[1:0m'
    underline_reset = '\033[4m'


def colored(s, c):
    """ Takes in string s and outputs it with color """
    if sys.stdout.isatty():
        return '{}{}{}'.format(c, s, color.reset)

    return s


class BaseFormatter(object):
    """Base Formatter class"""

    def _format(self, match):
        """Format the specific match"""

    def print_matches(self, matches, rules=None, filenames=None):
        """Output all the matches"""
        # Unused argument http://pylint-messages.wikidot.com/messages:w0613
        del rules
        del filenames

        if not matches:
            return None

        # Output each match on a separate line by default
        output = []
        for match in matches:
            output.append(self._format(match))

        return '\n'.join(output)


class Formatter(BaseFormatter):
    """Generic Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = u'{0} {1}\n{2}:{3}:{4}\n'
        return formatstr.format(
            match.rule.id,
            match.message,
            match.filename,
            match.linenumber,
            match.columnnumber
        )


class JUnitFormatter(BaseFormatter):
    """JUnit-style Reports"""

    def _failure_format(self, match):
        """Format output of a failure"""
        formatstr = u'{0} at {1}:{2}:{3}'
        return formatstr.format(
            match.message,
            match.filename,
            match.linenumber,
            match.columnnumber
        )

    def print_matches(self, matches, rules=None, filenames=None):
        """Output all the matches"""

        if not rules:
            return None

        test_cases = []
        for rule in rules.all_rules:
            if not rules.is_rule_enabled(rule):
                if not rule.id:
                    continue
                test_case = TestCase(name='{0} {1}'.format(rule.id, rule.shortdesc))

                if rule.experimental:
                    test_case.add_skipped_info(message='Experimental rule - not enabled')
                else:
                    test_case.add_skipped_info(message='Ignored rule')
                test_cases.append(test_case)
            else:
                test_case = TestCase(
                    name='{0} {1}'.format(rule.id, rule.shortdesc),
                    allow_multiple_subelements=True,
                    url=rule.source_url
                )
                for match in matches:
                    if match.rule.id == rule.id:
                        test_case.add_failure_info(
                            message=self._failure_format(match),
                            failure_type=match.message
                        )
                test_cases.append(test_case)

        test_suite = TestSuite('CloudFormation Lint', test_cases)

        return to_xml_report_string([test_suite], prettyprint=True)


class JsonFormatter(BaseFormatter):
    """Json Formatter"""

    class CustomEncoder(json.JSONEncoder):
        """Custom Encoding for the Match Object"""
        # pylint: disable=E0202

        def default(self, o):
            if isinstance(o, Match):
                return {
                    'Rule': {
                        'Id': o.rule.id,
                        'Description': o.rule.description,
                        'ShortDescription': o.rule.shortdesc,
                        'Source': o.rule.source_url
                    },
                    'Location': {
                        'Start': {
                            'ColumnNumber': o.columnnumber,
                            'LineNumber': o.linenumber,
                        },
                        'End': {
                            'ColumnNumber': o.columnnumberend,
                            'LineNumber': o.linenumberend,
                        },
                        'Path': getattr(o, 'path', None),
                    },
                    'Level': o.rule.severity.capitalize(),
                    'Message': o.message,
                    'Filename': o.filename,
                }
            return {'__{}__'.format(o.__class__.__name__): o.__dict__}

    def print_matches(self, matches, rules=None, filenames=None):
        # JSON formatter outputs a single JSON object
        # Unused argument http://pylint-messages.wikidot.com/messages:w0613
        del rules

        return json.dumps(
            matches, indent=4, cls=self.CustomEncoder,
            sort_keys=True, separators=(',', ': '))


class QuietFormatter(BaseFormatter):
    """Quiet Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = u'{0} {1}:{2}'
        return formatstr.format(
            match.rule,
            match.filename,
            match.linenumber
        )


class ParseableFormatter(BaseFormatter):
    """Parseable Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = u'{0}:{1}:{2}:{3}:{4}:{5}:{6}'
        return formatstr.format(
            match.filename,
            match.linenumber,
            match.columnnumber,
            match.linenumberend,
            match.columnnumberend,
            match.rule.id,
            re.sub(r'(\r*\n)+', ' ', match.message)
        )


class PrettyFormatter(BaseFormatter):
    """Generic Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = '{0}{1}{2}'
        pos = '{0}:{1}:'.format(match.linenumber, match.columnnumber)
        return formatstr.format(
            colored('{:20}'.format(pos), color.reset),
            colored('{:10}'.format(match.rule.id), getattr(color, match.rule.severity.lower())),
            match.message,
        )

    def print_matches(self, matches, rules=None, filenames=None):
        results = self._format_matches(matches)

        results.append('Cfn-lint scanned {} templates against {} rules and found {} errors, {} warnings, and {} informational violations'.format(
            colored(len(filenames), color.bold_reset),
            colored(len(rules), color.bold_reset),
            colored(len([i for i in matches if i.rule.severity.lower() == 'error']), color.error),
            colored(len([i for i in matches if i.rule.severity.lower() == 'warning']), color.warning),
            colored(len([i for i in matches if i.rule.severity.lower()
                         == 'informational']), color.informational),
        ))
        return '\n'.join(results)

    def _format_matches(self, matches):
        """Output all the matches"""
        output = []

        # This better be sorted
        for filename, file_matches in itertools.groupby(
                matches,
                key=operator.attrgetter('filename')
        ):
            levels = {
                'error': [],
                'warning': [],
                'informational': [],
                'unknown': []
            }

            output.append(colored(filename, color.underline_reset))
            for match in file_matches:
                level = match.rule.severity.lower()
                if level not in ['error', 'warning', 'informational']:
                    level = 'unknown'
                levels[level].append(match)
            for _, all_matches in levels.items():
                for match in all_matches:
                    output.extend([self._format(match)])

            output.append('')  # Newline after each group

        return output
