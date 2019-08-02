"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
import logging
import sys
import warnings
from jsonschema.exceptions import ValidationError
from cfnlint.rules import RulesCollection
import cfnlint.config
import cfnlint.formatters
import cfnlint.decode
import cfnlint.maintenance
from cfnlint.helpers import REGIONS
from cfnlint import CfnLintExitException as _CfnLintExitException
from cfnlint import InvalidRegionException as _InvalidRegionException
from cfnlint import UnexpectedRuleException as _UnexpectedRuleException
from cfnlint import refactored

LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')
LINTER = None


@refactored('CfnLintExitException is refactored and deprecated. Please use cfnlint.CfnLintExitException')
class CfnLintExitException(_CfnLintExitException):
    """ Refactored class RuleMatch """


@refactored('InvalidRegionException is refactored and deprecated. Please use cfnlint.InvalidRegionException')
class InvalidRegionException(_InvalidRegionException):
    """ Refactored class RuleMatch """


@refactored('UnexpectedRuleException is refactored and deprecated. Please use cfnlint.UnexpectedRuleException')
class UnexpectedRuleException(_UnexpectedRuleException):
    """ Refactored class RuleMatch """


def run_cli(filename, template, rules, regions, override_spec, mandatory_rules=None):
    """Process args and run"""
    warnings.warn('get_exit_code is refactored and deprecated. Please use cfnlint.Linter')
    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    return run_checks(filename, template, rules, regions, mandatory_rules)


def get_exit_code(matches):
    """ Determine exit code """
    warnings.warn('get_exit_code is refactored and deprecated. Please use cfnlint.Linter')
    exit_code = 0
    for match in matches:
        if match.rule.id[0] == 'I':
            exit_code = exit_code | 8
        elif match.rule.id[0] == 'W':
            exit_code = exit_code | 4
        elif match.rule.id[0] == 'E':
            exit_code = exit_code | 2

    return exit_code


def get_formatter(fmt):
    """ Get Formatter"""
    warnings.warn('get_formatter is refactored and deprecated. Please use cfnlint.Linter')
    formatter = {}
    if fmt:
        if fmt == 'quiet':
            formatter = cfnlint.formatters.QuietFormatter()
        elif fmt == 'parseable':
            # pylint: disable=bad-option-value
            formatter = cfnlint.formatters.ParseableFormatter()
        elif fmt == 'json':
            formatter = cfnlint.formatters.JsonFormatter()
    else:
        formatter = cfnlint.formatters.Formatter()

    return formatter


def get_rules(append_rules, ignore_rules, include_rules, configure_rules=None, include_experimental=False, mandatory_rules=None):
    """Get rules"""
    warnings.warn('get_rules is refactored and deprecated. Please use cfnlint.Linter')
    rules = RulesCollection(ignore_rules, include_rules, configure_rules,
                            include_experimental, mandatory_rules)
    rules_paths = [DEFAULT_RULESDIR] + append_rules
    try:
        for rules_path in rules_paths:
            if rules_path and os.path.isdir(os.path.expanduser(rules_path)):
                rules.create_from_directory(rules_path)
            else:
                rules.create_from_module(rules_path)
    except (OSError, ImportError) as e:
        raise UnexpectedRuleException('Tried to append rules but got an error: %s' % str(e), 1)
    return rules


def configure_logging(debug_logging):
    """ Backwards compatibility for integrators """
    warnings.warn('configure_logging is refactored and deprecated. Please use cfnlint.Linter')
    LOGGER.info('Update your integrations to use "cfnlint.config.configure_logging" instead')
    cfnlint.config.configure_logging(debug_logging, False)


def get_args_filenames(cli_args):
    """ Get Template Configuration items and set them as default values"""
    warnings.warn('get_args_filenames is refactored and deprecated. Please use cfnlint.Linter')
    try:
        config = cfnlint.config.ConfigMixIn(cli_args)
    except ValidationError as e:
        LOGGER.error('Error parsing config file: %s', str(e))
        sys.exit(1)

    fmt = config.format
    formatter = get_formatter(fmt)

    if config.update_specs:
        cfnlint.maintenance.update_resource_specs()
        sys.exit(0)

    if config.update_documentation:
        # Get ALL rules (ignore the CLI settings))
        documentation_rules = cfnlint.core.get_rules([], [], ['I', 'E', 'W'], {}, True, [])
        cfnlint.maintenance.update_documentation(documentation_rules)
        sys.exit(0)

    if config.update_iam_policies:
        cfnlint.maintenance.update_iam_policies()
        sys.exit(0)

    if config.listrules:
        rules = cfnlint.core.get_rules(
            config.append_rules,
            config.ignore_checks,
            config.include_checks,
            config.configure_rules,
            config.mandatory_checks,
        )
        print(rules)
        sys.exit(0)

    if not sys.stdin.isatty() and not config.templates:
        return(config, [None], formatter)

    if not config.templates:
        # Not specified, print the help
        config.parser.print_help()
        sys.exit(1)

    return(config, config.templates, formatter)


def get_template_rules(filename, args):
    """ Get Template Configuration items and set them as default values"""
    warnings.warn('get_template_rules is refactored and deprecated. Please use cfnlint.Linter')
    (template, matches) = cfnlint.decode.decode(filename, args.ignore_bad_template)

    if matches:
        return(template, [], matches)

    args.template_args = template

    rules = cfnlint.core.get_rules(
        args.append_rules,
        args.ignore_checks,
        args.include_checks,
        args.configure_rules,
        args.include_experimental,
        args.mandatory_checks,
    )

    return(template, rules, [])


def run_checks(filename, template, rules, regions, mandatory_rules=None):
    """Run Checks against the template"""
    warnings.warn('run_checks is refactored and deprecated. Please use cfnlint.Linter')
    if regions:
        if not set(regions).issubset(set(REGIONS)):
            unsupported_regions = list(set(regions).difference(set(REGIONS)))
            msg = 'Regions %s are unsupported. Supported regions are %s' % (
                unsupported_regions, REGIONS)
            raise _InvalidRegionException(msg, 32)

    matches = []

    runner = cfnlint.Runner(rules, filename, template, regions, mandatory_rules=mandatory_rules)
    matches.extend(runner.transform())
    # Only do rule analysis if Transform was successful
    if not matches:
        try:
            matches.extend(runner.run())
        except Exception as err:  # pylint: disable=W0703
            msg = 'Tried to process rules on file %s but got an error: %s' % (
                filename, str(err))
            UnexpectedRuleException(msg, 1)
    matches.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

    return(matches)
