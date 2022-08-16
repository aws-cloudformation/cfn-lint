"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging
import os
import sys
from typing import Iterator, Sequence, Optional, Tuple, List

from jsonschema.exceptions import ValidationError

import cfnlint.runner
from cfnlint.template import Template
from cfnlint.rules import Match, RulesCollection, ParseError, TransformError
import cfnlint.config
import cfnlint.formatters
import cfnlint.decode
import cfnlint.maintenance
from cfnlint.helpers import REGIONS, REGISTRY_SCHEMAS

LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')
__CACHED_RULES = None

Matches = List[Match]
RulesCollectionNone = Optional[RulesCollection]
ArgsFilename = Tuple[cfnlint.config.ConfigMixIn,
                     List[Optional[str]], cfnlint.formatters.BaseFormatter]
TemplateRules = Tuple[Optional[str], RulesCollectionNone, Optional[Matches]]


class CfnLintExitException(Exception):
    """Generic exception used when the cli should exit"""

    def __init__(self, msg=None, exit_code=1):
        if msg is None:
            msg = f'process failed with exit code {exit_code}'
        super(CfnLintExitException, self).__init__(msg)
        self.exit_code = exit_code


class InvalidRegionException(CfnLintExitException):
    """When an unsupported/invalid region is supplied"""


class UnexpectedRuleException(CfnLintExitException):
    """When processing a rule fails in an unexpected way"""


def run_cli(filename: str,
            template: str,
            rules: RulesCollectionNone,
            regions: Sequence[str],
            override_spec: dict,
            build_graph: bool,
            registry_schemas: Sequence[str],
            mandatory_rules: Optional[Sequence[str]] = None
            ) -> Matches:
    """Process args and run"""

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    if build_graph:
        template_obj = Template(filename, template, regions)
        template_obj.build_graph()

    if registry_schemas:
        for path in registry_schemas:
            if path and os.path.isdir(os.path.expanduser(path)):
                for f in os.listdir(path):
                    with open(os.path.join(path, f), encoding='utf-8') as schema:
                        REGISTRY_SCHEMAS.append(json.load(schema))

    return run_checks(filename, template, rules, regions, mandatory_rules)


def get_exit_code(matches: Matches) -> int:
    """ Determine exit code """
    exit_code = 0
    for match in matches:
        if match.rule.severity == 'informational':
            exit_code = exit_code | 8
        elif match.rule.severity == 'warning':
            exit_code = exit_code | 4
        elif match.rule.severity == 'error':
            exit_code = exit_code | 2

    return exit_code

# pylint: disable=too-many-return-statements


def get_formatter(fmt: str) -> cfnlint.formatters.BaseFormatter:
    if fmt:
        if fmt == 'quiet':
            return cfnlint.formatters.QuietFormatter()
        if fmt == 'parseable':
            # pylint: disable=bad-option-value
            return cfnlint.formatters.ParseableFormatter()
        if fmt == 'json':
            return cfnlint.formatters.JsonFormatter()
        if fmt == 'junit':
            return cfnlint.formatters.JUnitFormatter()
        if fmt == 'pretty':
            return cfnlint.formatters.PrettyFormatter()
        if fmt == 'sarif':
            return cfnlint.formatters.SARIFFormatter()

    return cfnlint.formatters.Formatter()


def get_rules(append_rules: List[str],
              ignore_rules: Sequence[str],
              include_rules: Sequence[str],
              configure_rules=None,
              include_experimental: bool = False,
              mandatory_rules: Sequence[str] = None,
              custom_rules: str = None
              ) -> RulesCollection:
    rules = RulesCollection(ignore_rules, include_rules, configure_rules,
                            include_experimental, mandatory_rules)
    rules_paths: List[str] = [DEFAULT_RULESDIR] + append_rules
    try:
        for rules_path in rules_paths:
            if rules_path and os.path.isdir(os.path.expanduser(rules_path)):
                rules.create_from_directory(rules_path)
            else:
                rules.create_from_module(rules_path)

        rules.create_from_custom_rules_file(custom_rules)
    except (OSError, ImportError) as e:
        raise UnexpectedRuleException(
            f'Tried to append rules but got an error: {str(e)}', 1)
    return rules


def get_matches(filenames: str, args: cfnlint.config.ConfigMixIn) -> Iterator[Match]:
    for filename in filenames:
        LOGGER.debug('Begin linting of file: %s', str(filename))
        (template, rules, errors) = get_template_rules(filename, args)
        # template matches may be empty but the template is still None
        # this happens when ignoring bad templates
        if not errors and template:
            matches = run_cli(filename, template, rules, args.regions, args.override_spec,
                              args.build_graph, args.registry_schemas, args.mandatory_checks)
            for match in matches:
                yield match
        else:
            if errors:
                for match in errors:
                    yield match
        LOGGER.debug('Completed linting of file: %s', str(filename))


def configure_logging(debug_logging):
    """ Backwards compatibility for integrators """
    LOGGER.info(
        'Update your integrations to use "cfnlint.config.configure_logging" instead')
    cfnlint.config.configure_logging(debug_logging, False)


def get_args_filenames(cli_args: Sequence[str]) -> ArgsFilename:
    """ Get Template Configuration items and set them as default values"""
    try:
        config = cfnlint.config.ConfigMixIn(cli_args)
    except ValidationError as e:
        LOGGER.error('Error parsing config file: %s', str(e))
        sys.exit(1)

    fmt = config.format
    formatter = get_formatter(fmt)

    if config.update_specs:
        cfnlint.maintenance.update_resource_specs(config.force)
        sys.exit(0)

    if config.update_documentation:
        # Get ALL rules (ignore the CLI settings))
        documentation_rules = cfnlint.core.get_rules(
            [], [], ['I', 'E', 'W'], {}, True, [])
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

def get_used_rules() -> Optional[RulesCollection]:
    return __CACHED_RULES

def _reset_rule_cache() -> None:
    """ Reset the rule cache. Used mostly for testing"""
    global __CACHED_RULES #pylint: disable=global-statement
    __CACHED_RULES = None

def get_template_rules(filename: str, args: cfnlint.config.ConfigMixIn) -> TemplateRules:
    """ Get Template Configuration items and set them as default values"""
    global __CACHED_RULES  # pylint: disable=global-statement

    ignore_bad_template: bool = False
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
            return(template, None, [])
        return(template, None, errors)

    args.template_args = template

    if __CACHED_RULES:
        __CACHED_RULES.configure(
            ignore_rules=args.ignore_checks,
            include_rules=args.include_checks,
            configure_rules=args.configure_rules,
            include_experimental=args.include_experimental,
            mandatory_rules=args.mandatory_checks,
        )
    else:
        __CACHED_RULES = cfnlint.core.get_rules(
            args.append_rules,
            args.ignore_checks,
            args.include_checks,
            args.configure_rules,
            args.include_experimental,
            args.mandatory_checks,
            args.custom_rules,
        )

    return(template, __CACHED_RULES, [])


def run_checks(filename: str, template: str,
               rules: RulesCollectionNone,
               regions: Sequence[str],
               mandatory_rules: Optional[Sequence[str]] = None
               ) -> Matches:
    """Run Checks and Custom Rules against the template"""
    if regions:
        if not set(regions).issubset(set(REGIONS)):
            unsupported_regions = list(set(regions).difference(set(REGIONS)))
            msg = f'Regions {unsupported_regions} are unsupported. Supported regions are {REGIONS}'
            raise InvalidRegionException(msg, 32)

    errors: Matches = []

    if not isinstance(rules, RulesCollection):
        return ([])

    runner = cfnlint.runner.Runner(rules, filename, template, regions,
                                   mandatory_rules=mandatory_rules)

    # Transform logic helps with handling serverless templates
    ignore_transform_error: bool = False
    if isinstance(rules, RulesCollection) and not rules.is_rule_enabled(TransformError()):
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
        msg = f'Tried to process rules on file {filename} but got an error: {str(err)}'
        UnexpectedRuleException(msg, 1)
    errors.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

    return(errors)
