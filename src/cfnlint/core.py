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
import json
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
import argparse
import six
from yaml.parser import ParserError, ScannerError
from cfnlint import RulesCollection, Match
import cfnlint.formatters as formatters
import cfnlint.cfn_yaml
import cfnlint.cfn_json
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


def run_cli(filename, template, rules, fmt, regions, override_spec, formatter):
    """Process args and run"""

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    matches = run_checks(filename, template, rules, regions)

    print_matches(matches, fmt, formatter)

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


def create_parser():
    """Do first round of parsing parameters to set options"""
    parser = ArgumentParser(description='CloudFormation Linter')

    # Alllow the template to be passes ad an optional or a positional argument
    parser.add_argument(
        'template', nargs='?', help='The CloudFormation template to be linted')
    parser.add_argument(
        '-t', '--template', dest='template_alt', help='The CloudFormation template to be linted')

    parser.add_argument(
        '-b', '--ignore-bad-template', help='Ignore failures with Bad template',
        action='store_true'
    )
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )
    parser.add_argument(
        '-f', '--format', help='Output Format', choices=['quiet', 'parseable', 'json']
    )

    parser.add_argument(
        '-l', '--list-rules', dest='listrules', default=False,
        action='store_true', help='list all the rules'
    )
    parser.add_argument(
        '-r', '--regions', dest='regions', default=['us-east-1'], nargs='*',
        help='list the regions to validate against.'
    )
    parser.add_argument(
        '-a', '--append-rules', dest='append_rules', default=[], nargs='*',
        help='specify one or more rules directories using '
             'one or more --append-rules arguments. '
    )
    parser.add_argument(
        '-i', '--ignore-checks', dest='ignore_checks', default=[], nargs='*',
        help='only check rules whose id do not match these values'
    )

    parser.add_argument(
        '-o', '--override-spec', dest='override_spec',
        help='A CloudFormation Spec override file that allows customization'
    )

    parser.add_argument(
        '-v', '--version', help='Version of cfn-lint', action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    parser.add_argument(
        '-u', '--update-specs', help='Update the CloudFormation Specs',
        action='store_true'
    )
    parser.add_argument(
        '--update-documentation', help=argparse.SUPPRESS,
        action='store_true'
    )
    return parser


def get_formatter(fmt):
    """ Get Formatter"""
    formatter = {}
    if fmt:
        if fmt == 'quiet':
            formatter = formatters.QuietFormatter()
        elif fmt == 'parseable':
            # pylint: disable=bad-option-value
            formatter = formatters.ParseableFormatter()
    else:
        formatter = formatters.Formatter()

    return formatter


def get_rules(rulesdir, ignore_rules):
    """Get rules"""
    rules = RulesCollection(ignore_rules)
    rules_dirs = [DEFAULT_RULESDIR] + rulesdir
    for rules_dir in rules_dirs:
        rules.extend(
            RulesCollection.create_from_directory(rules_dir))

    return rules


def get_template_args_rules(cli_args):
    """ Get Template Configuration items and set them as default vales"""
    defaults = {}
    template = {}
    parser = create_parser()

    args = parser.parse_known_args(cli_args)

    configure_logging(vars(args[0])['debug'])

    fmt = vars(args[0])['format']
    formatter = get_formatter(fmt)

    # Filename can be speficied as positional or optiona argument. Positional
    # is leading
    if vars(args[0])['template']:
        filename = vars(args[0])['template']
    elif vars(args[0])['template_alt']:
        filename = vars(args[0])['template_alt']
    else:
        filename = None

    if filename:
        ignore_bad_template = vars(args[0])['ignore_bad_template']
        try:
            template = cfnlint.cfn_yaml.load(filename)
        except IOError as e:
            if e.errno == 2:
                LOGGER.error('Template file not found: %s', filename)
                sys.exit(1)
            elif e.errno == 21:
                LOGGER.error('Template references a directory, not a file: %s', filename)
                sys.exit(1)
            elif e.errno == 13:
                LOGGER.error('Permission denied when accessing template file: %s', filename)
                sys.exit(1)
        except cfnlint.cfn_yaml.CfnParseError as err:
            err.match.Filename = filename
            matches = [err.match]
            print_matches(matches, fmt, formatter)
            sys.exit(get_exit_code(matches))
        except ParserError as err:
            matches = [create_match_yaml_parser_error(err, filename)]
            print_matches(matches, fmt, formatter)
            sys.exit(get_exit_code(matches))
        except ScannerError as err:
            if err.problem == 'found character \'\\t\' that cannot start any token':
                try:
                    template = json.load(open(filename), cls=cfnlint.cfn_json.CfnJSONDecoder)
                except cfnlint.cfn_json.JSONDecodeError as json_err:
                    json_err.match.filename = filename
                    matches = [json_err.match]
                    print_matches(matches, fmt, formatter)
                    sys.exit(get_exit_code(matches))
                except JSONDecodeError as json_err:
                    matches = [create_match_json_parser_error(json_err, filename)]
                    print_matches(matches, fmt, formatter)
                    sys.exit(get_exit_code(matches))
                except Exception as json_err:  # pylint: disable=W0703
                    if ignore_bad_template:
                        LOGGER.info('Template %s is malformed: %s', filename, err.problem)
                        LOGGER.info('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                    else:
                        LOGGER.error('Template %s is malformed: %s', filename, err.problem)
                        LOGGER.error('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                        sys.exit(1)
            else:
                matches = [create_match_yaml_parser_error(err, filename)]
                print_matches(matches, fmt, formatter)
                sys.exit(get_exit_code(matches))

    defaults = get_default_args(template)
    parser.set_defaults(**defaults)

    args = parser.parse_args(cli_args)

    if vars(args)['update_specs']:
        cfnlint.maintenance.update_resource_specs()
        exit(0)

    rules = cfnlint.core.get_rules(vars(args)['append_rules'], vars(args)['ignore_checks'])

    if vars(args)['update_documentation']:
        cfnlint.maintenance.update_documentation(rules)
        exit(0)

    if vars(args)['listrules']:
        print(rules)
        exit(0)

    if not filename:
        # Not specified, print the help
        parser.print_help()
        exit(1)

    return(args, filename, template, rules, fmt, formatter)


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

    matches = list()

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


def print_matches(matches, fmt, formatter):
    """Print matches"""
    if fmt == 'json':
        print(json.dumps(matches, indent=4, cls=CustomEncoder))
    else:
        for match in matches:
            print(formatter.format(match))


def create_match_yaml_parser_error(parser_error, filename):
    """Create a Match for a parser error"""
    lineno = parser_error.problem_mark.line + 1
    colno = parser_error.problem_mark.column + 1
    msg = parser_error.problem
    return cfnlint.Match(
        lineno, colno, lineno, colno + 1, filename,
        cfnlint.ParseError(), message=msg)


def create_match_json_parser_error(parser_error, filename):
    """Create a Match for a parser error"""
    if sys.version_info[0] == 3:
        lineno = parser_error.lineno
        colno = parser_error.colno
        msg = parser_error.msg
    elif sys.version_info[0] == 2:
        lineno = 1
        colno = 1
        msg = parser_error.message
    return cfnlint.Match(
        lineno, colno, lineno, colno + 1, filename, cfnlint.ParseError(), message=msg)


class CustomEncoder(json.JSONEncoder):
    """Custom Encoding for the Match Object"""
    # pylint: disable=E0202
    def default(self, o):
        if isinstance(o, Match):
            if o.rule.id[0] == 'W':
                level = 'Warning'
            else:
                level = 'Error'

            return {
                'Rule': {
                    'Id': o.rule.id,
                    'Description': o.rule.description,
                    'ShortDescription': o.rule.shortdesc,
                },
                'Location': {
                    'Start': {
                        'ColumnNumber': o.columnnumber,
                        'LineNumber': o.linenumber,
                    },
                    'End': {
                        'ColumnNumber': o.columnnumberend,
                        'LineNumber': o.linenumberend,
                    }
                },
                'Level': level,
                'Message': o.message,
                'Filename': o.filename,
            }
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}
