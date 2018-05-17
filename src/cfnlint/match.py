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
import json

LOGGER = logging.getLogger(__name__)


class Match(object):
    """Match Classes"""

    def __init__(
            self, linenumber, columnnumber, linenumberend,
            columnnumberend, filename, rule, message=None):
        """Init"""
        self.linenumber = linenumber
        self.columnnumber = columnnumber
        self.linenumberend = linenumberend
        self.columnnumberend = columnnumberend
        self.filename = filename
        self.rule = rule
        self.message = message  # or rule.shortdesc

    def __repr__(self):
        """Represent"""
        formatstr = u'[{0}] ({1}) matched {2}:{3}'
        return formatstr.format(self.rule, self.message,
                                self.filename, self.linenumber)

    def __eq__(self, item):
        """Override equal to compare matches"""
        return (
            (
                self.linenumber, self.columnnumber, self.rule.id, self.message
            ) ==
            (
                item.linenumber, item.columnnumber, item.rule.id, item.message
            ))


def print_matches(frmt, matches, formatter):
    """Output the values"""
    exit_code = 0
    for match in matches:
        if match.rule.id[0] == 'W':
            exit_code = exit_code | 4
        elif match.rule.id[0] == 'E':
            exit_code = exit_code | 2
    if frmt == 'json':
        print(json.dumps(matches, indent=4, cls=CustomEncoder))
    else:
        for match in matches:
            print(formatter.format(match))

    return exit_code


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
