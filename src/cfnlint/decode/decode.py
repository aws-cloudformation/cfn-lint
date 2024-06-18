"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from json.decoder import JSONDecodeError
from typing import Any, Callable, Dict, List, Tuple, Union

from yaml import YAMLError
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from cfnlint.decode import cfn_json, cfn_yaml
from cfnlint.match import Match

LOGGER = logging.getLogger(__name__)

Matches = List[Match]
Decode = Tuple[Union[Dict[str, Any], None], Matches]


def decode_str(s: str) -> Decode:
    """Decode the string s into an object."""
    return _decode(cfn_yaml.loads, cfn_json.loads, s, None)


def decode(filename: str | None) -> Decode:
    """Decode filename into an object."""
    return _decode(cfn_yaml.load, cfn_json.load, filename, filename)


def _decode(
    yaml_f: Callable, json_f: Callable, payload: str | None, filename: str | None
) -> Decode:
    """Decode payload using yaml_f and json_f, using filename for log output."""
    template = None
    matches = []
    try:
        template = yaml_f(payload)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error("Template file not found: %s", filename)
            matches.append(
                create_match_file_error(
                    filename, f"Template file not found: {filename}"
                )
            )
        elif e.errno == 21:
            LOGGER.error("Template references a directory, not a file: %s", filename)
            matches.append(
                create_match_file_error(
                    filename, f"Template references a directory, not a file: {filename}"
                )
            )
        elif e.errno == 13:
            LOGGER.error("Permission denied when accessing template file: %s", filename)
            matches.append(
                create_match_file_error(
                    filename,
                    f"Permission denied when accessing template file: {filename}",
                )
            )

        if matches:
            return (None, matches)
    except UnicodeDecodeError:
        LOGGER.error("Cannot read file contents: %s", filename)
        matches.append(
            create_match_file_error(filename, "Cannot read file contents: {filename}")
        )
    except cfn_yaml.CfnParseError as err:
        matches = err.matches
    except ParserError as err:
        matches = [create_match_yaml_parser_error(err, filename)]
    except ScannerError as err:
        if err.problem and (
            err.problem
            in [
                "found character '\\t' that cannot start any token",
                "found unknown escape character",
            ]
            or err.problem.startswith("found unknown escape character")
        ):
            try:
                template = json_f(payload)
            except cfn_json.JSONDecodeError as json_errs:
                for json_err in json_errs.matches:
                    matches.append(
                        Match(
                            message=json_err.message,
                            filename=filename,
                            linenumber=json_err.linenumber,
                            columnnumber=json_err.columnnumber,
                            linenumberend=json_err.linenumberend,
                            columnnumberend=json_err.columnnumberend,
                            rule=json_err.rule,
                            parent_id=json_err.parent_id,
                        )
                    )
            except JSONDecodeError as json_err:
                if hasattr(json_err, "msg"):
                    if json_err.msg in [
                        "No JSON object could be decoded",
                        "Expecting value",
                    ]:  # pylint: disable=no-member
                        matches = [create_match_yaml_parser_error(err, filename)]
                    else:
                        matches = [create_match_json_parser_error(json_err, filename)]
            except Exception as json_err:  # pylint: disable=W0703
                LOGGER.error("Template %s is malformed: %s", filename, err.problem)
                LOGGER.error(
                    "Tried to parse %s as JSON but got error: %s",
                    filename,
                    str(json_err),
                )
                return (
                    None,
                    [
                        create_match_file_error(
                            filename,
                            (
                                f"Tried to parse {filename} as JSON but got error:"
                                f" {str(json_err)}"
                            ),
                        )
                    ],
                )
        else:
            matches = [create_match_yaml_parser_error(err, filename)]
    except YAMLError as err:
        matches = [create_match_file_error(filename, str(err))]

    if not isinstance(template, dict) and not matches:
        # pylint: disable=import-outside-toplevel
        from cfnlint.rules.errors import ParseError

        # Template isn't a dict which means nearly nothing will work
        matches = [
            Match.create(
                filename=filename or "",
                rule=ParseError(),
                message="Template needs to be an object.",
            )
        ]
    return (template, matches)


def create_match_yaml_parser_error(parser_error, filename):
    """Create a Match for a parser error"""
    # pylint: disable=import-outside-toplevel
    from cfnlint.rules.errors import ParseError

    lineno = parser_error.problem_mark.line + 1
    colno = parser_error.problem_mark.column + 1
    msg = parser_error.problem
    return Match.create(
        message=msg,
        rule=ParseError(),
        filename=filename,
        linenumber=lineno,
        columnnumber=colno,
    )


def create_match_file_error(filename, msg):
    """Create a Match for a parser error"""
    # pylint: disable=import-outside-toplevel
    from cfnlint.rules.errors import ParseError

    return Match.create(
        filename=filename,
        rule=ParseError(),
        message=msg,
    )


def create_match_json_parser_error(parser_error, filename):
    """Create a Match for a parser error"""
    # pylint: disable=import-outside-toplevel
    from cfnlint.rules.errors import ParseError

    lineno = parser_error.lineno
    colno = parser_error.colno
    msg = parser_error.msg
    return Match.create(
        filename=filename,
        rule=ParseError(),
        message=msg,
        linenumber=lineno,
        columnnumber=colno,
    )
