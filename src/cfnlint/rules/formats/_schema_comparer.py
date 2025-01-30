"""
Helpers for loading resources, managing specs, constants, etc.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from cfnlint.jsonschema.exceptions import ValidationError

_keyword = "format"

LOGGER = logging.getLogger(__name__)


def _any_of(
    source: str,
    any_ofs: list[dict[str, Any]],
) -> tuple[bool, list[str]]:
    """Compare the source schema with the destination schema and
    return a ValidationError if they don't match.

    Args:
        source (str): The source schema to compare.
        destination (list[dict[str, Any]]): The anyOf schemas

    Returns:
        tuple[bool, list[str]]: A bool value if format matches and a
                                list of format values if they don't match.
    """
    formats = []
    for subschema in any_ofs:
        if _keyword in subschema:
            if source == subschema[_keyword]:
                return True, []

            formats.append(subschema[_keyword])

    return False, formats


_schema_composition: dict[str, Callable] = {
    "anyOf": _any_of,
}


def _backwards_compatibility(format: Any) -> Any:
    if format == "AWS::EC2::SecurityGroup.GroupId":
        LOGGER.warning(
            f"{format!r} is deprecated. Use 'AWS::EC2::SecurityGroup.Id' instead"
        )
        return "AWS::EC2::SecurityGroup.Id"
    return format


def _compare_schemas(
    source: str,
    destination: dict[str, Any],
) -> tuple[bool, list[str]]:
    """Compare two schemas and return a ValidationError if they don't match.

    Args:
        source (str): The source schema to compare.
        destination (dict[str, Any]): The destination schema to compare against.

    Returns:
        tuple[bool, list[str]]: True/False if the format keyword matches
    """

    dest_f = _backwards_compatibility(destination.get(_keyword))
    if dest_f == source:
        return True, [dest_f]  # Nothing else matters to be on the safe side

    all_formats = [dest_f] if dest_f else []
    for composition_key in _schema_composition:
        if composition_key in destination:
            match, formats = _schema_composition[composition_key](
                source, destination[composition_key]
            )
            if match:
                return True, []
            all_formats.extend(formats)

    return False, all_formats


def compare_schemas(
    source: dict[str, Any],
    destination: dict[str, Any],
) -> ValidationError | None:
    """Compare two schemas and return a ValidationError if they don't match.

    Args:
        source (dict[str, Any]): The source schema to compare.
        destination (dict[str, Any]): The destination schema to compare against.

    Returns:
        ValidationError: A ValidationError if the schemas don't match, otherwise None.
    """

    f = _backwards_compatibility(source.get(_keyword))

    if f is None:
        return None

    match, formats = _compare_schemas(f, destination)
    if match:
        return None

    if formats:
        return ValidationError(
            f"{f!r} format is incompatible with formats {formats!r}",
            schema={"format": f},
            instance=formats,
        )

    return ValidationError(
        f"{f!r} format is incompatible",
        schema={"format": f},
        instance=None,
    )
