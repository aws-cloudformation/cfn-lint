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
import logging
import json
import six
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from yaml.parser import ParserError, ScannerError
import cfnlint.decode.cfn_yaml
import cfnlint.decode.cfn_json


LOGGER = logging.getLogger(__name__)


def decode(filename, ignore_bad_template):
    """
        Decode filename into an object
    """
    template = None
    matches = []
    try:
        template = cfnlint.decode.cfn_yaml.load(filename)
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
    except cfnlint.decode.cfn_yaml.CfnParseError as err:
        err.match.Filename = filename
        matches = [err.match]

    except ParserError as err:
        matches = [create_match_yaml_parser_error(err, filename)]
    except ScannerError as err:
        if err.problem == 'found character \'\\t\' that cannot start any token':
            try:
                template = json.load(open(filename), cls=cfnlint.decode.cfn_json.CfnJSONDecoder)
            except cfnlint.decode.cfn_json.JSONDecodeError as json_err:
                json_err.match.filename = filename
                matches = [json_err.match]
            except JSONDecodeError as json_err:
                matches = [create_match_json_parser_error(json_err, filename)]
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

    return (template, matches)


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
