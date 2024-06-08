"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import datetime

import pytest

from cfnlint.rules.resources.properties.StringLength import StringLength


@pytest.fixture(scope="module")
def rule():
    yield StringLength()


@pytest.mark.parametrize(
    "instance,mL,schema,expected",
    [
        ("foo", 2, {}, 0),
        ("foo", 4, {}, 1),
        ({"Fn::Sub": "foo"}, 2, {}, 0),
        ({"Fn::Sub": "foo"}, 4, {}, 1),
        ({"Fn::Sub": ["foo", {}]}, 2, {}, 0),
        ({"Fn::Sub": ["foo", {}]}, 4, {}, 1),
        ({"Fn::Sub": ["foo", {}, {}]}, 2, {}, 0),
        ({"foo": "bar"}, 10, {"type": "object"}, 0),
        ({"foo": "bar"}, 20, {"type": "object"}, 1),
        ({"foo": datetime.datetime.now()}, 10, {"type": "object"}, 0),
        ({"foo": datetime.datetime.now()}, 40, {"type": "object"}, 1),
        ({"foo": ["bar"]}, 10, {"type": "object"}, 0),
        ({"foo": ["bar"]}, 20, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Ref": "Parameter"}}, 10, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Ref": "Parameter"}}, 20, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Fn::Sub": "2"}}, 10, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Fn::Sub": "2"}}, 20, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Fn::Sub": ["2", {}]}}, 10, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Fn::Sub": ["2", {}]}}, 20, {"type": "object"}, 1),
    ],
)
def test_min_length(instance, mL, expected, rule, schema, validator):
    assert len(list(rule.minLength(validator, mL, instance, schema))) == expected


@pytest.mark.parametrize(
    "instance,mL,schema,expected",
    [
        ("foo", 4, {}, 0),
        ("foo", 2, {}, 1),
        ({"Fn::Sub": "foo"}, 4, {}, 0),
        ({"Fn::Sub": "foo"}, 2, {}, 1),
        ({"Fn::Sub": ["foo", {}]}, 4, {}, 0),
        ({"Fn::Sub": ["foo", {}]}, 2, {}, 1),
        ({"Fn::Sub": ["foo", {}, {}]}, 2, {}, 0),
        ({"foo": "bar"}, 20, {"type": "object"}, 0),
        ({"foo": "bar"}, 2, {"type": "object"}, 1),
        ({"foo": datetime.datetime.now()}, 40, {"type": "object"}, 0),
        ({"foo": datetime.datetime.now()}, 2, {"type": "object"}, 1),
        ({"foo": ["bar"]}, 20, {"type": "object"}, 0),
        ({"foo": ["bar"]}, 2, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Ref": "Parameter"}}, 20, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Ref": "Parameter"}}, 4, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Fn::Sub": "2"}}, 20, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Fn::Sub": "2"}}, 4, {"type": "object"}, 1),
        ({"foo": 1, "bar": {"Fn::Sub": ["2", {}]}}, 20, {"type": "object"}, 0),
        ({"foo": 1, "bar": {"Fn::Sub": ["2", {}]}}, 4, {"type": "object"}, 1),
    ],
)
def test_max_length(instance, mL, expected, rule, schema, validator):
    assert len(list(rule.maxLength(validator, mL, instance, schema))) == expected
