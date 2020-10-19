"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
import six
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
from yaml.parser import ParserError, ScannerError
from yaml import YAMLError
from cfnlint.decode import cfn_yaml, cfn_json
from cfnlint.rules import Match, ParseError


LOGGER = logging.getLogger(__name__)


def decode(filename):
    """
        Decode filename into an object
    """
    template = None
    matches = []
    try:
        template = cfn_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Template file not found: %s', filename)
            matches.append(create_match_file_error(
                filename, 'Template file not found: %s' % filename))
        elif e.errno == 21:
            LOGGER.error('Template references a directory, not a file: %s',
                         filename)
            matches.append(create_match_file_error(
                filename,
                'Template references a directory, not a file: %s' % filename))
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing template file: %s',
                         filename)
            matches.append(create_match_file_error(
                filename,
                'Permission denied when accessing template file: %s' % filename))

        if matches:
            return(None, matches)
    except UnicodeDecodeError as err:
        LOGGER.error('Cannot read file contents: %s', filename)
        matches.append(create_match_file_error(
            filename, 'Cannot read file contents: %s' % filename))
    except cfn_yaml.CfnParseError as err:
        err.match.Filename = filename
        matches = [err.match]
    except ParserError as err:
        matches = [create_match_yaml_parser_error(err, filename)]
    except ScannerError as err:
        if err.problem in [
                'found character \'\\t\' that cannot start any token',
                'found unknown escape character'] or err.problem.startswith(
                    'found unknown escape character'):
            try:
                template = cfn_json.load(filename)
            except cfn_json.JSONDecodeError as json_err:
                json_err.match.filename = filename
                matches = [json_err.match]
            except JSONDecodeError as json_err:
                if hasattr(json_err, 'message'):
                    if json_err.message == 'No JSON object could be decoded':  # pylint: disable=no-member
                        matches = [create_match_yaml_parser_error(err, filename)]
                    else:
                        matches = [create_match_json_parser_error(json_err, filename)]
                if hasattr(json_err, 'msg'):
                    if json_err.msg == 'Expecting value':  # pylint: disable=no-member
                        matches = [create_match_yaml_parser_error(err, filename)]
                    else:
                        matches = [create_match_json_parser_error(json_err, filename)]
            except Exception as json_err:  # pylint: disable=W0703
                LOGGER.error(
                    'Template %s is malformed: %s', filename, err.problem)
                LOGGER.error('Tried to parse %s as JSON but got error: %s',
                             filename, str(json_err))
                return (None, [create_match_file_error(
                    filename,
                    'Tried to parse %s as JSON but got error: %s' % (
                        filename, str(json_err)))])
        else:
            matches = [create_match_yaml_parser_error(err, filename)]
    except YAMLError as err:
        matches = [create_match_file_error(filename, err)]

    if not isinstance(template, dict) and not matches:
        # Template isn't a dict which means nearly nothing will work
        matches = [Match(1, 1, 1, 1, filename, ParseError(),
                         message='Template needs to be an object.')]
    return (template, matches)


def create_match_yaml_parser_error(parser_error, filename):
    """Create a Match for a parser error"""
    lineno = parser_error.problem_mark.line + 1
    colno = parser_error.problem_mark.column + 1
    msg = parser_error.problem
    return Match(
        lineno, colno, lineno, colno + 1, filename,
        ParseError(), message=msg)


def create_match_file_error(filename, msg):
    """Create a Match for a parser error"""
    return Match(
        linenumber=1, columnnumber=1, linenumberend=1, columnnumberend=2,
        filename=filename, rule=ParseError(), message=msg)


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
    return Match(
        lineno, colno, lineno, colno + 1, filename, ParseError(), message=msg)
