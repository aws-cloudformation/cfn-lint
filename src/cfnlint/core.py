"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import logging
import sys
import os
import argparse
import six
from cfnlint import RulesCollection
import cfnlint.formatters
import cfnlint.decode
import cfnlint.maintenance
from cfnlint.version import __version__
from cfnlint.helpers import REGIONS

LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')


class ArgumentParser(argparse.ArgumentParser):
    """ Override Argument Parser so we can control the exit code"""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(32, '%s: error: %s\n' % (self.prog, message))


def run_cli(filename, template, rules, regions, override_spec, formatter):
    """Process args and run"""

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    matches = run_checks(filename, template, rules, regions)

    formatter.print_matches(matches)

    return get_exit_code(matches)


def get_exit_code(matches):
    """ Determine exit code """
    exit_code = 0
    for match in matches:
        if match.rule.id[0] == 'W':
            exit_code = exit_code | 4
        elif match.rule.id[0] == 'E':
            exit_code = exit_code | 2

    return exit_code


def configure_logging(debug_logging):
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if debug_logging:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def comma_separated_arg(string):
    """ Split a comma separated string """
    return string.split(',')


class ExtendAction(argparse.Action):
    """Support argument types that are lists and can be specified multiple times."""
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, [])
        for value in values:
            items.extend(value)
        setattr(namespace, self.dest, items)


def create_parser():
    """Do first round of parsing parameters to set options"""
    parser = ArgumentParser(description='CloudFormation Linter')
    parser.register('action', 'extend', ExtendAction)

    standard = parser.add_argument_group('Standard')
    advanced = parser.add_argument_group('Advanced / Debugging')

    # Alllow the template to be passes as an optional or a positional argument
    standard.add_argument(
        'template', nargs='?', help='The CloudFormation template to be linted')
    standard.add_argument(
        '-t', '--template', metavar='TEMPLATE', dest='template_alt', help='The CloudFormation template to be linted')

    standard.add_argument(
        '-b', '--ignore-bad-template', help='Ignore failures with Bad template',
        action='store_true'
    )
    advanced.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )
    standard.add_argument(
        '-f', '--format', help='Output Format', choices=['quiet', 'parseable', 'json']
    )

    standard.add_argument(
        '-l', '--list-rules', dest='listrules', default=False,
        action='store_true', help='list all the rules'
    )
    standard.add_argument(
        '-r', '--regions', dest='regions', nargs='+', default=[],
        type=comma_separated_arg, action='extend',
        help='list the regions to validate against.'
    )
    advanced.add_argument(
        '-a', '--append-rules', dest='append_rules', nargs='+', default=[],
        type=comma_separated_arg, action='extend',
        help='specify one or more rules directories using '
             'one or more --append-rules arguments. '
    )
    standard.add_argument(
        '-i', '--ignore-checks', dest='ignore_checks', nargs='+', default=[],
        type=comma_separated_arg, action='extend',
        help='only check rules whose id do not match these values'
    )

    advanced.add_argument(
        '-o', '--override-spec', dest='override_spec',
        help='A CloudFormation Spec override file that allows customization'
    )

    standard.add_argument(
        '-v', '--version', help='Version of cfn-lint', action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    advanced.add_argument(
        '-u', '--update-specs', help='Update the CloudFormation Specs',
        action='store_true'
    )
    advanced.add_argument(
        '--update-documentation', help=argparse.SUPPRESS,
        action='store_true'
    )
    return parser


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
    else:
        formatter = cfnlint.formatters.Formatter()

    return formatter


def get_rules(rulesdir, ignore_rules):
    """Get rules"""
    rules = RulesCollection(ignore_rules)
    rules_dirs = [DEFAULT_RULESDIR] + rulesdir
    try:
        for rules_dir in rules_dirs:
            rules.extend(
                RulesCollection.create_from_directory(rules_dir))
    except OSError as e:
        LOGGER.error('Tried to append rules but got an error: %s', str(e))
        exit(1)

    return rules


def get_template_args_rules(cli_args):
    """ Get Template Configuration items and set them as default values"""
    template = {}
    parser = create_parser()

    args, _ = parser.parse_known_args(cli_args)

    configure_logging(args.debug)

    fmt = args.format
    formatter = get_formatter(fmt)

    # Filename can be speficied as positional or optional argument. Positional
    # is leading
    if args.template:
        filename = args.template
    elif args.template_alt:
        filename = args.template_alt
    else:
        filename = None

    if filename:
        (template, matches) = cfnlint.decode.decode(filename, args.ignore_bad_template)

        if matches:
            formatter.print_matches(matches)
            sys.exit(get_exit_code(matches))

    # If the template has cfn-lint Metadata but the same options are set on the command-
    # line, ignore the template's configuration. This works because these are all appends
    # that have default values of empty arrays or none.  The only one that really doesn't
    # work is ignore_bad_template but you can't override that back to false at this point.
    for section, values in get_default_args(template).items():
        if not getattr(args, section):
            setattr(args, section, values)

    # Set default regions if none are specified.
    if not args.regions:
        setattr(args, 'regions', ['us-east-1'])

    if args.update_specs:
        cfnlint.maintenance.update_resource_specs()
        exit(0)

    rules = cfnlint.core.get_rules(args.append_rules, args.ignore_checks)

    if args.update_documentation:
        cfnlint.maintenance.update_documentation(rules)
        exit(0)

    if args.listrules:
        print(rules)
        exit(0)

    if not filename:
        # Not specified, print the help
        parser.print_help()
        exit(1)

    return(args, filename, template, rules, formatter)


def get_default_args(template):
    """ Parse and validate default args """
    defaults = {}
    if isinstance(template, dict):
        configs = template.get('Metadata', {}).get('cfn-lint', {}).get('config', {})

        if isinstance(configs, dict):
            for config_name, config_value in configs.items():
                if config_name == 'ignore_checks':
                    if isinstance(config_value, list):
                        defaults['ignore_checks'] = config_value
                if config_name == 'regions':
                    if isinstance(config_value, list):
                        defaults['regions'] = config_value
                if config_name == 'append_rules':
                    if isinstance(config_value, list):
                        defaults['override_spec'] = config_value
                if config_name == 'override_spec':
                    if isinstance(config_value, (six.string_types, six.text_type)):
                        defaults['override_spec'] = config_value
                if config_name == 'ignore_bad_template':
                    if isinstance(config_value, bool):
                        defaults['ignore_bad_template'] = config_value

    return defaults


def run_checks(filename, template, rules, regions):
    """Run Checks against the template"""
    if regions:

        for region in regions:
            if region not in REGIONS:
                LOGGER.error('Supported regions are %s', REGIONS)
                exit(32)

    matches = []

    runner = cfnlint.Runner(rules, filename, template, regions)
    matches.extend(runner.transform())
    # Only do rule analysis if Transform was successful
    if not matches:
        try:
            matches.extend(runner.run())
        except Exception as err:  # pylint: disable=W0703
            LOGGER.error('Tried to process rules on file %s but got an error: %s', filename, str(err))
            exit(1)
    matches.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

    return(matches)
