"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import itertools
import json
import operator
import re
import sys
from typing import List

import sarif_om as sarif
from jschema_to_python.to_json import to_json
from junit_xml import TestCase, TestSuite, to_xml_report_string

from cfnlint.version import __version__
from cfnlint.rules import (Match, ParseError, RuleError, RulesCollection,
                     TransformError)

Matches = List[Match]


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
        return f'{c}{s}{color.reset}'

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
        formatstr = '{0} {1}\n{2}:{3}:{4}\n'
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
        formatstr = '{0} at {1}:{2}:{3}'
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
            if not rule.id in rules.used_rules:
                if not rule.id:
                    continue
                test_case = TestCase(name=f'{rule.id} {rule.shortdesc}')

                if rule.experimental:
                    test_case.add_skipped_info(
                        message='Experimental rule - not enabled')
                else:
                    test_case.add_skipped_info(message='Ignored rule')
                test_cases.append(test_case)
            else:
                test_case = TestCase(
                    name=f'{rule.id} {rule.shortdesc}',
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
            return {f'__{o.__class__.__name__}__': o.__dict__}

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
        formatstr = '{0} {1}:{2}'
        return formatstr.format(
            match.rule,
            match.filename,
            match.linenumber
        )


class ParseableFormatter(BaseFormatter):
    """Parseable Formatter"""

    def _format(self, match):
        """Format output"""
        formatstr = '{0}:{1}:{2}:{3}:{4}:{5}:{6}'
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
        pos = f'{match.linenumber}:{match.columnnumber}:'
        return formatstr.format(
            colored(f'{pos:20}', color.reset),
            colored(f'{match.rule.id:10}', getattr(
                color, match.rule.severity.lower())),
            match.message,
        )

    def print_matches(self, matches, rules=None, filenames=None):
        results = self._format_matches(matches)

        results.append(
            f'Cfn-lint scanned {colored(len(filenames), color.bold_reset)} templates against '
            f'{colored(len(rules.used_rules), color.bold_reset)} rules and found '
            f'{colored(len([i for i in matches if i.rule.severity.lower() == "error"]), color.error)} '
            f'errors, {colored(len([i for i in matches if i.rule.severity.lower() == "warning"]), color.warning)} '
            f'warnings, and '
            f'{colored(len([i for i in matches if i.rule.severity.lower() == "informational"]), color.informational)} '
            f'informational violations')
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


class SARIFFormatter(BaseFormatter):
    """
    SARIF formatter

    This formatter outputs results according to the Static Analysis Results
    Interchange Format (SARIF) Version 2.1.0.

    https://docs.oasis-open.org/sarif/sarif/v2.1.0/csprd01/sarif-v2.1.0-csprd01.html
    """

    schema = 'https://docs.oasis-open.org/sarif/sarif/v2.1.0/cos02/schemas/sarif-schema-2.1.0.json'
    version = '2.1.0'

    # The spec defines error, note, warning, and none, see section 3.27.10.
    levelMap = {
        'error': 'error',
        'informational': 'note',
        'warning': 'warning',
    }

    uri_base_id = 'EXECUTIONROOT'

    def _to_sarif_level(self, severity):
        return self.levelMap.get(severity, 'none')

    def print_matches(self, matches, rules=None, filenames=None):
        """Output all the matches"""

        if not rules:
            rules = RulesCollection()

        # These "base" rules are not passed into formatters
        rules.extend([ParseError(), TransformError(), RuleError()])

        results = []
        for match in matches:
            results.append(
                sarif.Result(
                    rule_id=match.rule.id,
                    message=sarif.Message(text=match.message),
                    level=self._to_sarif_level(match.rule.severity),
                    locations=[
                        sarif.Location(
                            physical_location=sarif.PhysicalLocation(
                                artifact_location=sarif.ArtifactLocation(
                                    uri=match.filename,
                                    uri_base_id=self.uri_base_id,
                                ),
                                region=sarif.Region(
                                    start_column=match.columnnumber,
                                    start_line=match.linenumber,
                                    end_column=match.columnnumberend,
                                    end_line=match.linenumberend,
                                ),
                            )
                        )
                    ],
                )
            )

        # Output only the rules that have matches
        matched_rules = set(r.rule_id for r in results)
        rules_map = {r.id: r for r in list(rules)}

        rules = [
            sarif.ReportingDescriptor(
                id=rule_id,
                short_description=sarif.MultiformatMessageString(
                    text=rules_map[rule_id].shortdesc
                ),
                full_description=sarif.MultiformatMessageString(
                    text=rules_map[rule_id].description
                ),
                help_uri=rules_map[rule_id].source_url if rules_map[
                    rule_id] else 'https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md'
            )
            for rule_id in matched_rules
        ]

        run = sarif.Run(
            tool=sarif.Tool(
                driver=sarif.ToolComponent(
                    name='cfn-lint',
                    short_description=sarif.MultiformatMessageString(
                        text=('Validates AWS CloudFormation templates against'
                              ' the resource specification and additional'
                              ' checks.')
                    ),
                    information_uri='https://github.com/aws-cloudformation/cfn-lint',
                    rules=rules,
                    version=__version__,
                ),
            ),
            original_uri_base_ids={
                self.uri_base_id: sarif.ArtifactLocation(
                    description=sarif.MultiformatMessageString(
                        'The directory in which cfn-lint was run.'
                    )
                )
            },
            results=results,
        )

        log = sarif.SarifLog(version=self.version,
                             schema_uri=self.schema, runs=[run])

        # IMPORTANT: 'warning' is the default level in SARIF and will be
        # stripped by serialization.
        return to_json(log)
