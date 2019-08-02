"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import os
import re
import sys
import traceback
import warnings
from copy import deepcopy, copy
from datetime import datetime
import six
from yaml.parser import ParserError
from jsonschema.exceptions import ValidationError
import cfnlint.helpers
import cfnlint.conditions
import cfnlint.config
from cfnlint.transform import Transform
from cfnlint.decode.node import TemplateAttributeError
from cfnlint.rules import RuleMatch as _RuleMatch
from cfnlint.rules import Match as _Match
from cfnlint.rules import RulesCollection as _RulesCollection
from cfnlint.rules import CloudFormationLintRule as _CloudFormationLintRule
from cfnlint.rules import ParseError as _ParseError
from cfnlint.rules import TransformError as _TransformError
from cfnlint.rules import RuleError as _RuleError
from cfnlint.template import Template as _Template
from cfnlint.template import TemplateLinter
from cfnlint.helpers import REGIONS
import cfnlint.rules

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-lines
def refactored(message):
    """ Decoreate for refactoring classes """
    def cls_wrapper(cls):
        """ Wrapper Class """
        class Wrapped(cls, object):
            """ Wrapped Class """

            def __init__(self, *args, **kwargs):
                warnings.warn(message, FutureWarning)
                super(Wrapped, self).__init__(*args, **kwargs)
        return Wrapped
    return cls_wrapper


@refactored('RuleMatch is refactored and deprecated. '
            'Please use cfnlint.rules.RuleMatch')
class RuleMatch(_RuleMatch):
    """ Refactored class RuleMatch """


@refactored('Match is refactored and deprecated. '
            'Please use cfnlint.rules.Match')
class Match(_Match):
    """ Refactored class Match """


@refactored('RulesCollection is refactored and deprecated. '
            'Please use cfnlint.rules.RulesCollection')
class RulesCollection(_RulesCollection):
    """ Refactored class Rules Collection """


@refactored('CloudFormationLintRule is refactored and deprecated. '
            'Please use cfnlint.rules.CloudFormationLintRule')
class CloudFormationLintRule(_CloudFormationLintRule):
    """ Refactored class Rules CloudFormationLintRule """


@refactored('ParseError is refactored and deprecated. '
            'Please use cfnlint.rules.ParseError')
class ParseError(_ParseError):
    """ Refactored class Rules ParseError """


@refactored('TransformError is refactored and deprecated. '
            'Please use cfnlint.rules.TransformError')
class TransformError(_TransformError):
    """ Refactored class Rules TransformError """


@refactored('RuleError is refactored and deprecated. '
            'Please use cfnlint.rules.RuleError')
class RuleError(_RuleError):
    """ Refactored class Rules RuleError """


@refactored('Template is refactored and deprecated. '
            'Please use cfnlint.template.Template')
class Template(_Template):
    """ Refactored class Template """


class CfnLintExitException(Exception):
    """Generic exception used when the cli should exit"""

    def __init__(self, msg=None, exit_code=1):
        if msg is None:
            msg = 'process failed with exit code %s' % exit_code
        super(CfnLintExitException, self).__init__(msg)
        self.exit_code = exit_code


class InvalidRegionException(CfnLintExitException):
    """When an unsupported/invalid region is supplied"""


class UnexpectedRuleException(CfnLintExitException):
    """When processing a rule fails in an unexpected way"""


class InvalidConfiguation(CfnLintExitException):
    """Invalid configuration"""


class Linter(object):
    """ Linter Class for executing linting and confirming config """
    config = None
    all_rules = None
    matches = None

    def __init__(self):
        """ Initialize the class """
        self.matches = []
        if self.config is None:
            # Not using the Cli so assuming this is being used as a module
            try:
                self.config = cfnlint.config.ConfigMixIn()
            except ValidationError as e:
                LOGGER.error('Error parsing config file: %s', str(e))
                raise InvalidConfiguation

        self.config.append_rules = [os.path.join(
            os.path.dirname(__file__), 'rules')]
        self.all_rules = self.get_rules(
            self.config.append_rules, [],
            ['I', 'E', 'W'], {}, True)

    def lint(self):
        """ Lint all the templates in the config """
        filenames = self.config.templates

        if self.config.override_spec:
            cfnlint.helpers.override_specs(self.config.override_spec)

        for filename in filenames:
            LOGGER.debug('Begin linting of file: %s', str(filename))
            template = TemplateLinter(
                config=self.config,
                rules=self.all_rules,
                filename=filename)
            if not template.matches:
                self.matches.extend(template.lint())
            else:
                self.matches.extend(template.matches)
            LOGGER.debug('Completed linting of file: %s', str(filename))

    def get_rules(self, rules_dirs, ignore_rules, include_rules,
                  configure_rules=None, include_experimental=False):
        """Get rules"""
        rules = _RulesCollection(ignore_rules, include_rules,
                                 configure_rules, include_experimental)
        try:
            for rules_dir in rules_dirs:
                rules.create_from_directory(rules_dir)
        except OSError as e:
            raise UnexpectedRuleException(
                'Tried to append rules but got an error: %s' % str(e), 1)
        return rules


class CliLinter(Linter):
    """ Cli Specific Linting """
    formatter = None

    def __init__(self, cli_args):
        """ Initialize the class """
        try:
            self.config = cfnlint.config.ConfigMixIn(cli_args)
        except ValidationError as e:
            LOGGER.error('Error parsing config file: %s', str(e))
            raise InvalidConfiguation(
                'Error parsing config file: %s' % str(e), 1)
        super(CliLinter, self).__init__()
        self.formatter = self._get_formatter()

    def _get_formatter(self):
        """ Get Formatter"""
        fmt = self.config.format
        if fmt:
            if fmt == 'quiet':
                return cfnlint.formatters.QuietFormatter()
            if fmt == 'parseable':
                # pylint: disable=bad-option-value
                return cfnlint.formatters.ParseableFormatter()
            if fmt == 'json':
                return cfnlint.formatters.JsonFormatter()

        return cfnlint.formatters.Formatter()

    def run_cli(self):
        """ Run Commands """
        if self.config.update_specs:
            cfnlint.maintenance.update_resource_specs()
            return 0

        if self.config.update_documentation:
            # Get ALL rules (ignore the CLI settings))
            cfnlint.maintenance.update_documentation(self.all_rules)
            return 0

        if self.config.update_iam_policies:
            cfnlint.maintenance.update_iam_policies()
            return 0

        if self.config.listrules:
            rules = self.get_rules(
                self.config.append_rules,
                self.config.ignore_checks,
                self.config.include_checks,
                self.config.configure_rules
            )
            print(rules)
            return 0

        if not sys.stdin.isatty() and not self.config.templates:
            self.config.templates = ['']
        elif self.config.templates is None:
            # Not specified, print the help
            self.config.parser.print_help()
            return 1

        self.lint()
        matches_output = self.formatter.print_matches(self.matches)
        if matches_output:
            print(matches_output)
        return self.get_exit_code()

    def get_exit_code(self):
        """ Determine exit code """
        exit_code = 0
        for match in self.matches:
            if match.rule.id[0] == 'I':
                exit_code = exit_code | 8
            elif match.rule.id[0] == 'W':
                exit_code = exit_code | 4
            elif match.rule.id[0] == 'E':
                exit_code = exit_code | 2

        return exit_code


class Runner(object):
    """Run all the rules"""

    def __init__(
            self, rules, filename, template, regions, verbosity=0, mandatory_rules=None):
        warnings.warn('The \'Runner\' class will be removed. '
                      'Please convert to cfnlint.Linter',
                      DeprecationWarning)
        self.rules = rules
        self.filename = filename
        self.verbosity = verbosity
        self.mandatory_rules = mandatory_rules or []
        self.cfn = Template(filename, template, regions)

    def transform(self):
        """Transform logic"""
        LOGGER.debug('Transform templates if needed')
        sam_transform = 'AWS::Serverless-2016-10-31'
        matches = []
        transform_declaration = self.cfn.template.get('Transform', [])
        transform_type = transform_declaration if isinstance(
            transform_declaration, list) else [transform_declaration]
        # Don't call transformation if Transform is not specified to prevent
        # useless execution of the transformation.
        # Currently locked in to SAM specific
        if sam_transform not in transform_type:
            return matches
        # Save the Globals section so its available for rule processing
        self.cfn.transform_pre['Globals'] = self.cfn.template.get(
            'Globals', {})
        transform = Transform(
            self.filename, self.cfn.template, self.cfn.regions[0])
        matches = transform.transform_template()
        self.cfn.template = transform.template()
        return matches

    def run(self):
        """Run rules"""
        LOGGER.info('Run scan of template %s', self.filename)
        matches = []
        if self.cfn.template is not None:
            matches.extend(
                self.rules.run(
                    self.filename, self.cfn))

        # uniq the list of incidents and filter out exceptions
        # from the template
        directives = self.cfn.get_directives()
        return_matches = []
        for match in matches:
            if not any(match == u for u in return_matches):
                if match.rule.id not in directives:
                    return_matches.append(match)
                else:
                    for mandatory_rule in self.mandatory_rules:
                        if match.rule.id.startswith(mandatory_rule):
                            return_matches.append(match)
                            break
                    else:
                        for directive in directives.get(match.rule.id):
                            if directive.get('start') <= match.linenumber <= directive.get('end'):
                                break
                        else:
                            return_matches.append(match)
        return return_matches
