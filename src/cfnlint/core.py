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
import argparse
import six
from yaml.parser import ParserError, ScannerError
from cfnlint import RulesCollection, TransformsCollection, Match
import cfnlint.formatters as formatters
import cfnlint.cfn_yaml
import cfnlint.cfn_json
from cfnlint.version import __version__


LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')
DEFAULT_TRANSFORMSDIR = os.path.join(os.path.dirname(__file__), 'transforms')


class ArgumentParser(argparse.ArgumentParser):
    """ Override Argument Parser so we can control the exit code"""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(32, '%s: error: %s\n' % (self.prog, message))


def run_cli(filename, template, rules, fmt, ignore_checks, regions, override_spec):
    """Process args and run"""

    formatter = get_formatter(fmt)

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    transforms = get_transforms()
    matches = run_checks(
        filename, template, rules, transforms, ignore_checks,
        regions)

    if fmt == 'json':
        print(json.dumps(matches, indent=4, cls=CustomEncoder))
    else:
        for match in matches:
            print(formatter.format(match))

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


def configure_logging(log_level):
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    if log_level == 'info':
        LOGGER.setLevel(logging.INFO)
    elif log_level == 'debug':
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.ERROR)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(log_formatter)
    LOGGER.addHandler(ch)


def create_parser():
    """Do first round of parsing parameters to set options"""
    parser = ArgumentParser(description='CloudFormation Linter')
    parser.add_argument(
        '--template', help='CloudFormation Template')
    parser.add_argument(
        '--ignore-bad-template', help='Ignore failures with Bad template',
        action='store_true'
    )
    parser.add_argument(
        '--log-level', help='Log Level', choices=['info', 'debug']
    )
    parser.add_argument(
        '--format', help='Output Format', choices=['quiet', 'parseable', 'json']
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


def get_rules(rulesdir):
    """Get rules"""
    rules = RulesCollection()
    rules_dirs = [DEFAULT_RULESDIR] + rulesdir
    for rules_dir in rules_dirs:
        rules.extend(
            RulesCollection.create_from_directory(rules_dir))

    return rules


def get_transforms():
    """Get Transforms"""
    transforms = TransformsCollection()
    transformdirs = [DEFAULT_TRANSFORMSDIR]
    for transformdir in transformdirs:
        transforms.extend(
            TransformsCollection.create_from_directory(transformdir))

    return transforms


def append_parser(parser, defaults):
    """Append arguments to parser"""
    parser.add_argument(
        '--list-rules', dest='listrules', default=False,
        action='store_true', help='list all the rules'
    )
    parser.add_argument(
        '--regions', dest='regions', default=['us-east-1'], nargs='*',
        help='list the regions to validate against.'
    )
    parser.add_argument(
        '--append-rules', dest='append_rules', default=[], nargs='*',
        help='specify one or more rules directories using '
             'one or more --append-rules arguments. '
    )
    parser.add_argument(
        '--ignore-checks', dest='ignore_checks', default=[], nargs='*',
        help='only check rules whose id do not match these values'
    )

    parser.add_argument(
        '--override-spec', dest='override_spec',
        help='A CloudFormation Spec override file that allows customization'
    )

    parser.add_argument(
        '--version', help='Version of cfn-lint', action='version',
        version='%(prog)s {version}'.format(version=__version__)
    )
    parser.add_argument(
        '--update-specs', help='Update the CloudFormation Specs',
        action='store_true'
    )

    parser.set_defaults(**defaults)


def get_template_args_rules(cli_args):
    """ Get Template Configuration items and set them as default vales"""
    defaults = {}
    template = {}
    parser = create_parser()

    args = parser.parse_known_args(cli_args)
    configure_logging(vars(args[0])['log_level'])

    if vars(args[0])['template']:
        filename = vars(args[0])['template']
        ignore_bad_template = vars(args[0])['ignore_bad_template']
        try:
            fp = open(filename)
            loader = cfnlint.cfn_yaml.MarkedLoader(fp.read())
            loader.add_multi_constructor('!', cfnlint.cfn_yaml.multi_constructor)
            template = loader.get_single_data()
            defaults = get_default_args(template)
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
        except cfnlint.cfn_yaml.DuplicateError as err:
            LOGGER.error('Template %s contains duplicates: %s', filename, err)
            sys.exit(1)
        except cfnlint.cfn_yaml.NullError as err:
            LOGGER.error('Template %s contains nulls: %s', filename, err)
            sys.exit(1)
        except (ParserError, ScannerError) as err:
            try:
                template = json.load(open(filename), cls=cfnlint.cfn_json.CfnJSONDecoder)
            except cfnlint.cfn_json.JSONDecodeError as json_err:
                if ignore_bad_template:
                    LOGGER.info('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.error('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                else:
                    LOGGER.error('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.error('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                sys.exit(1)
            except Exception as json_err:  # pylint: disable=W0703
                if ignore_bad_template:
                    LOGGER.info('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.info('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                else:
                    LOGGER.error('Template %s is malformed: %s', filename, err.problem)
                    LOGGER.error('Tried to parse %s as JSON but got error: %s', filename, str(json_err))
                    sys.exit(1)

    append_parser(parser, defaults)
    args = parser.parse_args(cli_args)

    if vars(args)['update_specs']:
        cfnlint.helpers.update_resource_specs()
        exit(0)

    rules = cfnlint.core.get_rules(vars(args)['append_rules'])

    if vars(args)['listrules']:
        print(rules)
        exit(0)

    if not vars(args)['template']:
        parser.print_help()
        exit(1)

    return(args, template, rules)


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
            if config_name == 'log_level':
                if isinstance(config_value, (six.string_types, six.text_type)):
                    defaults['log_level'] = config_value

    return defaults


def run_checks(filename, template, rules, transforms, ignore_checks, regions):
    """Run Checks against the template"""
    if regions:
        supported_regions = [
            'ap-south-1',
            'sa-east-1',
            'ap-northeast-1',
            'ap-northeast-2',
            'ap-southeast-1',
            'ap-southeast-2',
            'ca-central-1',
            'eu-central-1',
            'eu-west-1',
            'eu-west-2',
            'us-west-2',
            'us-east-1',
            'us-east-2',
            'us-west-1'
        ]
        for region in regions:
            if region not in supported_regions:
                LOGGER.error('Supported regions are %s', supported_regions)
                exit(32)

    matches = list()

    runner = cfnlint.Runner(
        rules, transforms, filename, template,
        ignore_checks, regions)
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
