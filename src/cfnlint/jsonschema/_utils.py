"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema

import itertools
from collections.abc import Mapping, Sequence
from typing import Any

import regex as re


def id_of(schema: Any) -> str:
    """
    Return the ID of a schema for recent JSON Schema drafts.
    """
    if schema is True or schema is False:
        return ""
    return schema.get("$id", "")  # type: ignore


class Unset:
    """
    An as-of-yet unset attribute or unprovided default parameter.
    """

    def __repr__(self):
        return "<unset>"


def find_additional_properties(instance, schema):
    """
    Return the set of additional properties for the given ``instance``.

    Weeds out properties that should have been validated by ``properties`` and
    / or ``patternProperties``.

    Assumes ``instance`` is dict-like already.
    """

    properties = schema.get("properties", {})
    patterns = "|".join(schema.get("patternProperties", {}))
    for property in instance:
        if property not in properties:
            if patterns and re.search(patterns, property):
                continue
            yield property


def extras_msg(extras):
    """
    Create an error message for extra items or properties.
    """

    verb = "was" if len(extras) == 1 else "were"
    return ", ".join(repr(extra) for extra in sorted(extras)), verb


def ensure_list(thing):
    """
    Wrap ``thing`` in a list if it's a single str.

    Otherwise, return it unchanged.
    """

    if isinstance(thing, str):
        return [thing]
    return thing


def _mapping_equal(one, two):
    """
    Check if two mappings are equal using the semantics of `equal`.
    """
    if len(one) != len(two):
        return False
    return all(key in two and equal(value, two[key]) for key, value in one.items())


def _sequence_equal(one, two):
    """
    Check if two sequences are equal using the semantics of `equal`.
    """
    if len(one) != len(two):
        return False
    return all(equal(i, j) for i, j in zip(one, two))


def equal(one, two):
    """
    Check if two things are equal evading some Python type hierarchy semantics.

    Specifically in JSON Schema, evade `bool` inheriting from `int`,
    recursing into sequences to do the same.
    """
    if isinstance(one, str) or isinstance(two, str):
        try:
            return str(one) == str(two)
        except ValueError:
            return False
    if isinstance(one, Sequence) and isinstance(two, Sequence):
        return _sequence_equal(one, two)
    if isinstance(one, Mapping) and isinstance(two, Mapping):
        return _mapping_equal(one, two)
    return unbool(one) == unbool(two)


def unbool(element, true=object(), false=object()):
    """
    A hack to make True and 1 and False and 0 unique for ``uniq``.
    """

    if element is True:
        return true
    elif element is False:
        return false
    return element


def uniq(container):
    """
    Check if all of a container's elements are unique.

    Tries to rely on the container being recursively sortable, or otherwise
    falls back on (slow) brute force.
    """
    c = []
    for i in container:
        i = unbool(i)
        if isinstance(i, (int, float, bool)):
            i = str(i)
        c.append(i)
    try:
        sort = sorted(unbool(i) for i in c)
        sliced = itertools.islice(sort, 1, None)

        for i, j in zip(sort, sliced):
            if equal(i, j):
                return False

    except (NotImplementedError, TypeError):
        seen = []
        for e in c:
            e = unbool(e)

            for i in seen:
                if equal(i, e):
                    return False

            seen.append(e)
    return True
