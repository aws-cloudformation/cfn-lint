"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from ast import Call
import logging
from typing import Tuple, List, Union, Callable, Optional
from json.decoder import JSONDecodeError
from yaml.parser import ParserError
from yaml.scanner import ScannerError
from yaml import YAMLError
from cfnlint.decode import cfn_yaml, cfn_json
from cfnlint.rules import Match, ParseError


LOGGER = logging.getLogger(__name__)

Matches = List[Match]
Decode = Tuple[Union[str, None], Matches]

def decode_str(s: str) -> Decode:
    """Decode the string s into an object."""
    return _decode(cfn_yaml.loads, cfn_json.loads, s, None)

def decode(filename: str) -> Decode:
    """Decode filename into an object."""
    return _decode(cfn_yaml.load, cfn_json.load, filename, filename)

def _decode(yaml_f: Callable, json_f: Callable, payload: str, filename: Optional[str]) -> Decode:
    """Decode payload using yaml_f and json_f, using filename for log output."""
    template = None
    matches = []
    try:
        template = yaml_f(payload)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Template file not found: %s', filename)
            matches.append(create_match_file_error(
                filename, f'Template file not found: {filename}'))
        elif e.errno == 21:
            LOGGER.error('Template references a directory, not a file: %s',
                         filename)
            matches.append(create_match_file_error(
                filename,
                'Template references a directory, not a file: {filename}'))
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing template file: %s',
                         filename)
            matches.append(create_match_file_error(
                filename,
                'Permission denied when accessing template file: {filename}'))

        if matches:
            return(None, matches)
    except UnicodeDecodeError as _:
        LOGGER.error('Cannot read file contents: %s', filename)
        matches.append(create_match_file_error(
            filename, 'Cannot read file contents: {filename}'))
    except cfn_yaml.CfnParseError as err:
        matches = err.matches
    except ParserError as err:
        matches = [create_match_yaml_parser_error(err, filename)]
    except ScannerError as err:
        if err.problem and (err.problem in [
                'found character \'\\t\' that cannot start any token',
                'found unknown escape character'] or err.problem.startswith(
                    'found unknown escape character')):
            try:
                template = json_f(payload)
            except cfn_json.JSONDecodeError as json_errs:
                for json_err in json_errs.matches:
                    json_err.filename = filename
                matches = json_errs.matches
            except JSONDecodeError as json_err:
                if hasattr(json_err, 'msg'):
                    if json_err.msg == 'No JSON object could be decoded':  # pylint: disable=no-member
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
                    f'Tried to parse {filename} as JSON but got error: {str(json_err)}')])
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
    lineno = parser_error.lineno
    colno = parser_error.colno
    msg = parser_error.msg
    return Match(
        lineno, colno, lineno, colno + 1, filename, ParseError(), message=msg)
