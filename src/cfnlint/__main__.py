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
import json
from yaml.parser import ParserError
import cfnlint.helpers
from cfnlint import RulesCollection
from cfnlint import Match
import cfnlint.formatters as formatters
from cfnlint.version import __version__

LOGGER = logging.getLogger('cfnlint')


def main():
    """Main Function"""
    parser = argparse.ArgumentParser(description='CloudFormation Linter')
    parser.add_argument(
        '--template', help='CloudFormation Template')
    parser.add_argument(
        '--ignore-bad-template', help='Ignore failures with Bad template',
        action='store_true'
    )

    defaults = {}
    args = parser.parse_known_args()
    template = {}
    if vars(args[0])['template']:
        try:
            filename = vars(args[0])['template']
            fp = open(filename)
            loader = cfnlint.parser.MarkedLoader(fp.read())
            loader.add_multi_constructor("!", cfnlint.parser.multi_constructor)
            template = loader.get_single_data()
            defaults = template.get('Metadata', {}).get('cfn-lint', {}).get('config', {})
        except ParserError as err:
            if vars(args)['ignore_bad_template']:
                LOGGER.info('Template %s is maflormed: %s', filename, err)
            else:
                LOGGER.error('Template %s is maflormed: %s', filename, err)
                sys.exit(1)

    parser.add_argument(
        '--format', help='Output Format', choices=['quiet', 'parseable', 'json']
    )
    parser.add_argument(
        '--list-rules', dest='listrules', default=False,
        action='store_true', help="list all the rules"
    )
    parser.add_argument(
        '--regions', dest='regions', default=['us-east-1'], nargs='*',
        help="list the regions to validate against."
    )
    parser.add_argument(
        '--append-rules', dest='rulesdir', default=[], nargs='*',
        help="specify one or more rules directories using "
             "one or more --append-rules arguments. "
    )
    parser.add_argument(
        '--ignore-checks', dest='ignore_checks', default=[], nargs='*',
        help="only check rules whose id do not match these values"
    )
    parser.add_argument(
        '--log-level', help='Log Level', choices=['info', 'debug']
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

    if vars(args)['format']:
        if vars(args)['format'] == 'quiet':
            formatter = formatters.QuietFormatter()
        elif vars(args)['format'] == 'parseable':
            # pylint: disable=bad-option-value
            formatter = formatters.ParseableFormatter()
    else:
        formatter = formatters.Formatter()

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    if vars(args)['log_level'] == 'info':
        LOGGER.setLevel(logging.INFO)
    elif vars(args)['log_level'] == 'debug':
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.ERROR)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(log_formatter)
    LOGGER.addHandler(ch)

    if vars(args)['update_specs']:
        cfnlint.helpers.update_resource_specs()
        exit(0)

    rules = RulesCollection()
    rulesdirs = [cfnlint.DEFAULT_RULESDIR] + vars(args)['rulesdir']
    for rulesdir in rulesdirs:
        rules.extend(
            RulesCollection.create_from_directory(rulesdir))

    if vars(args)['listrules']:
        print(rules)
        return 0

    if vars(args)['regions']:
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
        for region in vars(args)['regions']:
            if region not in supported_regions:
                LOGGER.error('Supported regions are %s', supported_regions)
                return(1)

    if vars(args)['template']:
        matches = list()
        runner = cfnlint.Runner(
            rules, vars(args)['template'], template, vars(args)['ignore_checks'],
            vars(args)['regions'])
        matches.extend(runner.run())
        matches.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

        if vars(args)['format'] == 'json':
            print(json.dumps(matches, indent=4, cls=CustomEncoder))
        else:
            for match in matches:
                print(formatter.format(match))
    else:
        parser.print_help()

    return 0


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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
