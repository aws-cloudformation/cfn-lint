"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import os
import sys

from jsonschema.exceptions import ValidationError

import cfnlint.runner
from cfnlint.template import Template
from cfnlint.rules import RulesCollection, ParseError, TransformError
import cfnlint.config
import cfnlint.formatters
import cfnlint.decode
import cfnlint.maintenance
from cfnlint.helpers import REGIONS

LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')


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


def run_cli(filename, template, rules, regions, override_spec, build_graph, mandatory_rules=None):
    """Process args and run"""

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    if build_graph:
        template_obj = Template(filename, template, regions)
        template_obj.build_graph()

    return run_checks(filename, template, rules, regions, mandatory_rules)


def get_exit_code(matches):
    """ Determine exit code """
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
    formatter = {}
    if fmt:
        if fmt == 'quiet':
            formatter = cfnlint.formatters.QuietFormatter()
        elif fmt == 'parseable':
            # pylint: disable=bad-option-value
            formatter = cfnlint.formatters.ParseableFormatter()
        elif fmt == 'json':
            formatter = cfnlint.formatters.JsonFormatter()
        elif fmt == 'junit':
            formatter = cfnlint.formatters.JUnitFormatter()
    else:
        formatter = cfnlint.formatters.Formatter()

    return formatter


def get_rules(append_rules, ignore_rules, include_rules, configure_rules=None, include_experimental=False, mandatory_rules=None):
    """Get rules"""
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
    LOGGER.info('Update your integrations to use "cfnlint.config.configure_logging" instead')
    cfnlint.config.configure_logging(debug_logging, False)


def get_args_filenames(cli_args):
    """ Get Template Configuration items and set them as default values"""
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

    ignore_bad_template = False
    if args.ignore_bad_template:
        ignore_bad_template = True
    else:
        # There is no collection at this point so we need to handle this
        # check directly
        if not ParseError().is_enabled(
                include_experimental=False,
                ignore_rules=args.ignore_checks,
                include_rules=args.include_checks,
                mandatory_rules=args.mandatory_checks,
        ):
            ignore_bad_template = True

    (template, errors) = cfnlint.decode.decode(filename)

    if errors:
        if len(errors) == 1 and ignore_bad_template and errors[0].rule.id == 'E0000':
            return(template, [], [])
        return(template, [], errors)

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
    if regions:
        if not set(regions).issubset(set(REGIONS)):
            unsupported_regions = list(set(regions).difference(set(REGIONS)))
            msg = 'Regions %s are unsupported. Supported regions are %s' % (
                unsupported_regions, REGIONS)
            raise InvalidRegionException(msg, 32)

    errors = []

    runner = cfnlint.runner.Runner(rules, filename, template, regions,
                                   mandatory_rules=mandatory_rules)

    # Transform logic helps with handling serverless templates
    ignore_transform_error = False
    if not rules.is_rule_enabled(TransformError()):
        ignore_transform_error = True

    errors.extend(runner.transform())

    if errors:
        if ignore_transform_error:
            return([])   # if there is a transform error we can't continue

        return(errors)

    # Only do rule analysis if Transform was successful
    try:
        errors.extend(runner.run())
    except Exception as err:  # pylint: disable=W0703
        msg = 'Tried to process rules on file %s but got an error: %s' % (filename, str(err))
        UnexpectedRuleException(msg, 1)
    errors.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

    return(errors)
