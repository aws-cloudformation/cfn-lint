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
import sys
import argparse
import logging
import cfnlint.helpers
import cfnlint.formatters as formatters
import cfnlint
from cfnlint.version import __version__

LOGGER = logging.getLogger('cfnlint')


class ArgumentParser(argparse.ArgumentParser):
    """ Override Argument Parser so we can control the exit code"""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(32, '%s: error: %s\n' % (self.prog, message))


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


def main():
    """Main Function"""
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

    defaults = {}
    args = parser.parse_known_args()
    template = {}

    configure_logging(vars(args[0])['log_level'])

    if vars(args[0])['format']:
        if vars(args[0])['format'] == 'quiet':
            formatter = formatters.QuietFormatter()
        elif vars(args[0])['format'] == 'parseable':
            # pylint: disable=bad-option-value
            formatter = formatters.ParseableFormatter()
        else:
            formatter = {}
    else:
        formatter = formatters.Formatter()

    if vars(args[0])['template']:
        (defaults, template) = cfnlint.get_template_default_args(
            vars(args[0])['template'],
            vars(args[0])['ignore_bad_template'],
            vars(args[0])['format'], formatter)

    parser.add_argument(
        '--list-rules', dest='listrules', default=False,
        action='store_true', help='list all the rules'
    )
    parser.add_argument(
        '--regions', dest='regions', default=['us-east-1'], nargs='*',
        help='list the regions to validate against.'
    )
    parser.add_argument(
        '--append-rules', dest='rulesdir', default=[], nargs='*',
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
    args = parser.parse_args()

    if vars(args)['override_spec']:
        cfnlint.helpers.override_specs(vars(args)['override_spec'])

    if vars(args)['update_specs']:
        cfnlint.helpers.update_resource_specs()
        exit(0)

    rules = cfnlint.RulesCollection()
    rulesdirs = [cfnlint.DEFAULT_RULESDIR] + vars(args)['rulesdir']
    for rulesdir in rulesdirs:
        rules.extend(
            cfnlint.RulesCollection.create_from_directory(rulesdir))

    if vars(args)['listrules']:
        print(rules)
        return 0

    transforms = cfnlint.TransformsCollection()
    transformdirs = [cfnlint.DEFAULT_TRANSFORMSDIR]
    for transformdir in transformdirs:
        transforms.extend(
            cfnlint.TransformsCollection.create_from_directory(transformdir))

    if not vars(args)['template']:
        parser.print_help()
        exit(1)

    matches = cfnlint.run_checks(
        vars(args)['template'], template, rules, transforms, vars(args)['ignore_checks'],
        vars(args)['regions'])

    exit_code = cfnlint.match.print_matches(vars(args)['format'], matches, formatter)

    return exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
