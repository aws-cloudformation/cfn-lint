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
import json
from cfnlint import Match

class BaseFormatter(object):
    """Base Formatter class"""

    def _format(self, match):
        """Format the specific match"""

    def print_matches(self, matches):
        """Output all the matches"""
        # Output each match on a separate line by default
        for match in matches:
            print(self._format(match))

class Formatter(BaseFormatter):
    """Generic Formatter"""
    def _format(self, match):
        """Format output"""
        formatstr = u'{0} {1}\n{2}:{3}:{4}\n'
        return formatstr.format(
            match.rule.id,
            match.message,
            match.filename,
            match.linenumber,
            match.columnnumber
        )

class JsonFormatter(BaseFormatter):
    """Json Formatter"""

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
                        'Source': o.rule.source_url
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

    def print_matches(self, matches):
        # JSON formatter outputs a single JSON object
        print(json.dumps(matches, indent=4, cls=self.CustomEncoder))


class QuietFormatter(BaseFormatter):
    """Quiet Formatter"""
    def _format(self, match):
        """Format output"""
        formatstr = u'{0} {1}:{2}'
        return formatstr.format(
            match.rule,
            match.filename,
            match.linenumber
        )


class ParseableFormatter(BaseFormatter):
    """Parseable Formatter"""
    def _format(self, match):
        """Format output"""
        formatstr = u'{0}:{1}:{2}:{3}:{4}:{5}:{6}'
        return formatstr.format(
            match.filename,
            match.linenumber,
            match.columnnumber,
            match.linenumberend,
            match.columnnumberend,
            match.rule.id,
            match.message
        )
