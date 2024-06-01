"""
Copyright (c) 2013 Julian Berman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

SPDX-License-Identifier: MIT
"""

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema

import itertools
from collections.abc import Mapping, Sequence

import regex as re


class Unset:
    """
    An as-of-yet unset attribute or unprovided default parameter.
    """

    def __repr__(self):
        return "<unset>"


def find_additional_properties(validator, instance, schema):
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
            if validator.is_type(property, "string"):
                if patterns and re.search(patterns, property):
                    continue
            yield property


def custom_msg(validator, schema):
    """
    Create an error message for custom validation.
    """
    if not isinstance(schema, dict):
        return None
    messages = schema.get("message")
    if isinstance(messages, dict):
        return messages.get(validator)

    return None


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


def uniq_keys(container, keys):
    """
    Check if all of a container's elements are unique based on a key.

    Tries to rely on the container being recursively sortable, or otherwise
    falls back on (slow) brute force.
    """
    c = []
    for i in container:
        try:
            o = {}
            for k in keys:
                o[k] = i[k]
            c.append(o)
        except (KeyError, TypeError):
            pass

    seen = []
    for e in c:
        e = unbool(e)
        for i in seen:
            if equal(i, e):
                return False

        seen.append(e)
    return True
