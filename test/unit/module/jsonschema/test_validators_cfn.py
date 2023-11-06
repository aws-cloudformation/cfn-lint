"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest
from collections import namedtuple
from typing import List, Tuple

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Resource, Transforms
from cfnlint.helpers import FUNCTIONS, REGIONS
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.jsonschema.exceptions import UnknownType
from cfnlint.jsonschema.validators import CfnTemplateValidator


class _Fns:
    def __init__(self, resp) -> None:
        self.resp = resp

    def get_value(self, instance, region):
        for item in self.resp:
            if isinstance(item, Exception):
                raise item
            yield item


class _Cfn:
    def __init__(self, resp) -> None:
        self.functions = _Fns(resp)


_T = namedtuple("_T", ["name", "instance", "schema", "errors", "cfn_response"])


class Base(unittest.TestCase):
    def message_errors(self, name, instance, errors, schema, **kwargs):
        cfn_validator = CfnTemplateValidator({}).extend(validators={"type": cfn_type})
        cls = kwargs.pop("cls", cfn_validator(schema=schema))
        validator = cls.evolve(**kwargs)
        i_errors = list(validator.iter_errors(instance))
        self.assertEqual(
            len(errors),
            len(i_errors),
            msg=(
                f"{name}: Expected exactly {len(errors)} error, "
                f"found {i_errors!r}, need {errors!r}"
            ),
        )
        err_messages = [err.message for err in i_errors]
        for err in errors:
            self.assertIn(
                err, err_messages, msg=f"{name}: expected {err} to be in {i_errors!r}"
            )

    def iterate_tests(self, tests: List[_T]):
        for test in tests:
            self.message_errors(
                name=test.name,
                instance=test.instance,
                schema=test.schema,
                errors=test.errors,
                cfn=_Cfn(test.cfn_response),
            )


class TestCfnTypes(Base):
    def build_execute_tests(self, instance, supported_types) -> None:
        _all_types = ["string", "number", "integer", "boolean", "array", "object"]
        tests: List[_T] = []
        for t in _all_types:
            reprs = ", ".join(repr(type) for type in [t])
            if t in supported_types:
                tests.append(
                    _T(
                        f"{instance} can return {t}",
                        instance,
                        {"type": t},
                        [],
                        [],
                    )
                )
            else:
                tests.append(
                    _T(
                        f"{instance} cannot return {t}",
                        instance,
                        {"type": t},
                        [f"{instance!r} is not of type {reprs}"],
                        [],
                    )
                )
        self.iterate_tests(tests)

    def test_standard_values(self):
        self.build_execute_tests({"Foo": True, "Bar": True}, ["object"])
        self.build_execute_tests({"Foo": True}, ["object"])
        self.build_execute_tests("a", ["string"])
        self.build_execute_tests("1.5", ["string", "number"])
        self.build_execute_tests("1", ["string", "number", "integer"])
        self.build_execute_tests(True, ["string", "boolean"])
        self.build_execute_tests("true", ["string", "boolean"])


class TestMultiCfnTypes(Base):
    def build_execute_tests(self, instance, supported_types, unsupported_type) -> None:
        tests: List[_T] = []
        check_types = supported_types + [unsupported_type]
        tests.append(
            _T(
                f"{instance} can return one of {check_types!r}",
                instance,
                {"type": check_types},
                [],
                [],
            )
        )

        self.iterate_tests(tests)

    def test_standard_values(self):
        # all these checks should return true as there is one good value
        self.build_execute_tests({"Foo": True, "Bar": True}, ["object"], "string")
        self.build_execute_tests({"Foo": True}, ["object"], "string")
        self.build_execute_tests("a", ["string"], "number")
        self.build_execute_tests("1.5", ["string", "number"], "integer")
        self.build_execute_tests("1", ["string", "number", "integer"], "boolean")
        self.build_execute_tests(True, ["string", "boolean"], "number")
        self.build_execute_tests("true", ["string", "boolean"], "object")


class TestCfnTypeFailure(Base):
    def test_cfn_type_failure(self):
        with self.assertRaises(UnknownType) as err:
            CfnTemplateValidator({}).is_type("foo", "bar")
        self.assertIn(
            "Unknown type 'bar' for validator with schema", str(err.exception)
        )


def _message_errors(cls, name, instance, schema, errors, **kwargs):
    validator = cls.evolve(**kwargs)
    i_errors = list(validator.iter_errors(instance))
    assert len(errors) == len(i_errors), (
        f"{name}: Expected exactly {len(errors)} error, "
        f"found {i_errors!r}, need {errors!r}"
    )

    err_messages = [err.message for err in i_errors]
    for err in errors:
        assert err in err_messages, f"{name}: expected {err} to be in {i_errors!r}"


def message_errors(name, instance, schema, errors, **kwargs):
    cls = kwargs.pop(
        "cls",
        CfnTemplateValidator(
            schema=schema,
            context=Context(
                functions=FUNCTIONS,
                resources={
                    "MyResource": Resource(
                        {
                            "Type": "AWS::S3::Bucket",
                        },
                    ),
                },
            ),
        ),
    )
    _message_errors(cls, name, instance, schema, errors, **kwargs)


def message_transform_errors(name, instance, schema, errors, **kwargs):
    cls = kwargs.pop(
        "cls",
        CfnTemplateValidator(
            schema=schema,
            context=Context(
                functions=FUNCTIONS,
                resources={
                    "MyResource": Resource(
                        {
                            "Type": "AWS::S3::Bucket",
                        },
                    ),
                },
                parameters={
                    "MyParameter": Parameter(
                        {
                            "Type": "string",
                            "Default": "bar",
                        }
                    ),
                    "MyResourceParameter": Parameter(
                        {
                            "Type": "string",
                            "Default": "MyResource",
                        }
                    ),
                },
                transforms=Transforms(["AWS::LanguageExtensions"]),
            ),
        ),
    )
    _message_errors(cls, name, instance, schema, errors, **kwargs)


# Ref
_ref_tests: List[Tuple] = [
    (
        "Invalid Ref with bad type",
        {"Ref": ["foo"]},
        {"type": "string"},
        [
            "['foo'] is not of type 'string'",
            (
                "['foo'] is not one of ['MyResource', 'AWS::NoValue', "
                "'AWS::AccountId', 'AWS::Partition', 'AWS::Region', "
                "'AWS::StackId', 'AWS::StackName', 'AWS::URLSuffix', "
                "'AWS::NotificationARNs']"
            ),
        ],
        [],
    ),
]

# Fn::GetAtt
_getatt_tests: List[Tuple] = [
    (
        "Valid GetAtt with a good attribute",
        {"Fn::GetAtt": ["MyResource", "Arn"]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid GetAtt with bad attribute",
        {"Fn::GetAtt": ["MyResource", "foo"]},
        {"type": "string"},
        [
            (
                "'foo' is not one of ['Arn', 'DomainName', "
                "'DualStackDomainName', 'RegionalDomainName', 'WebsiteURL']"
            )
        ],
        [],
    ),
    (
        "Invalid GetAtt with bad resource name",
        {"Fn::GetAtt": ["Foo", "bar"]},
        {"type": "string"},
        ["'Foo' is not one of ['MyResource']"],
        [],
    ),
    (
        "Invalid GetAtt with a bad type",
        {"Fn::GetAtt": {"foo": "bar"}},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'string', 'array'"],
        [],
    ),
]

# Fn::Base64
_base64_tests: List[Tuple] = [
    (
        "Valid Fn::Base64 string",
        {"Fn::Base64": "foo"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Base64 for wrong output type",
        {"Fn::Base64": "foo"},
        {"type": "array"},
        ["{'Fn::Base64': 'foo'} is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Base64 is NOT a string",
        {"Fn::Base64": ["foo", "bar"]},
        {"type": "string"},
        ["['foo', 'bar'] is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Base64 using an invalid function",
        {"Fn::Base64": {"foo": "bar"}},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'string'"],
        [],
    ),
    (
        "Valid Fn::Base64 with a valid function",
        {"Fn::Base64": {"Fn::Sub": "foo"}},
        {"type": "string"},
        [],
        [],
    ),
]

_split_tests: List[Tuple] = [
    (
        "Valid Fn::Split with array",
        {"Fn::Split": ["foo", "bar"]},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Invalid Fn::Split with wrong output type",
        {"Fn::Split": ["foo", "bar"]},
        {"type": "string"},
        ["{'Fn::Split': ['foo', 'bar']} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Split is NOT a array",
        {"Fn::Split": "foo"},
        {"type": "array"},
        ["'foo' is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Split using a function for delimiter",
        {"Fn::Split": [{"foo": "bar"}, "bar"]},
        {"type": "array"},
        ["{'foo': 'bar'} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Split using an invalid function",
        {"Fn::Split": ["-", {"foo": "bar"}]},
        {"type": "array"},
        ["{'foo': 'bar'} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Split using an invalid CFN function",
        {"Fn::Split": ["-", {"Fn::Split": ["-", "bar"]}]},
        {"type": "array"},
        ["{'Fn::Split': ['-', 'bar']} is not of type 'string'"],
        [],
    ),
    (
        "Valid Fn::Split with a valid function",
        {"Fn::Split": ["foo", {"Fn::Sub": "bar"}]},
        {"type": "array"},
        [],
        [],
    ),
]

# join tests
_join_tests: List[Tuple] = [
    (
        "Valid Fn::Join with array",
        {"Fn::Join": ["foo", ["bar"]]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Join with wrong output type",
        {"Fn::Join": ["foo", ["bar"]]},
        {"type": "array"},
        ["{'Fn::Join': ['foo', ['bar']]} is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Join is NOT a array",
        {"Fn::Join": "foo"},
        {"type": "string"},
        ["'foo' is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Join using a function for delimiter",
        {"Fn::Join": [{"Ref": "MyResource"}, ["bar"]]},
        {"type": "string"},
        ["{'Ref': 'MyResource'} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Join using an invalid function",
        {"Fn::Join": ["-", {"foo": "bar"}]},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Join using an invalid CFN function",
        {"Fn::Join": ["-", {"Fn::Join": ["-", "bar"]}]},
        {"type": "string"},
        ["{'Fn::Join': ['-', 'bar']} is not of type 'array'"],
        [],
    ),
    (
        "Valid Fn::Join with a valid function",
        {"Fn::Join": ["-", {"Fn::Split": ["-", "bar"]}]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Valid Fn::Join with a valid item function",
        {"Fn::Join": ["-", [{"Fn::Sub": "bar"}]]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Join with an invalid function",
        {"Fn::Join": ["-", [{"Fn::Split": ["-", {"Ref": "MyResource"}]}]]},
        {"type": "string"},
        ["{'Fn::Split': ['-', {'Ref': 'MyResource'}]} is not of type 'string'"],
        [],
    ),
]

_select_tests: List[Tuple] = [
    (
        "Valid Fn::Select with array",
        {"Fn::Select": [1, ["bar"]]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Select is NOT a array",
        {"Fn::Select": "foo"},
        {"type": "string"},
        ["'foo' is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Select using an invalid function for index",
        {"Fn::Select": [{"Fn::GetAtt": "MyResource"}, ["bar"]]},
        {"type": "string"},
        ["{'Fn::GetAtt': 'MyResource'} is not of type 'integer'"],
        [],
    ),
    (
        "Invalid Fn::Select using an invalid function for array",
        {"Fn::Select": [1, {"foo": "bar"}]},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::Select using an invalid CFN function",
        {"Fn::Select": [1, {"Fn::Join": ["-", "bar"]}]},
        {"type": "string"},
        ["{'Fn::Join': ['-', 'bar']} is not of type 'array'"],
        [],
    ),
    (
        "Valid Fn::Select with a valid function",
        {"Fn::Select": [1, {"Fn::Split": ["-", "bar"]}]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Valid Fn::Select with a valid function",
        {"Fn::Select": [1, ["foo", {"Fn::FindInMap": ["a", "b", "c"]}]]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Select with an invalid function",
        {"Fn::Select": [1, ["foo", {"foo": "bar"}]]},
        {"type": "string"},
        [
            (
                "{'Fn::Select': [1, ['foo', {'foo': 'bar'}]]} is not of type "
                "'string' when 'Fn::Select' is resolved"
            )
        ],
        [],
    ),
]

# CIDR
_cidr_tests: List[Tuple] = [
    (
        "Valid Fn::Cidr with 2 element array",
        {"Fn::Cidr": ["192.168.0.0/24", 6]},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Valid Fn::Cidr with 3 element array",
        {"Fn::Cidr": ["192.168.0.0/24", 6, 5]},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Invalid Fn::Cidr with wrong output type",
        {"Fn::Cidr": ["192.168.0.0/24", 2]},
        {"type": "string"},
        ["{'Fn::Cidr': ['192.168.0.0/24', 2]} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::Cidr is NOT a array",
        {"Fn::Cidr": "foo"},
        {"type": "array"},
        ["'foo' is not of type 'array'"],
        [],
    ),
    (
        "Valid Fn::Cidr with a valid function",
        {"Fn::Cidr": ["192.168.0.0/24", {"Fn::FindInMap": ["a", "b", "c"]}]},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Invalid Fn::Cidr with an invalid function",
        {"Fn::Cidr": ["foo", {"Fn::Join": ["-", "bar"]}]},
        {"type": "array"},
        ["{'Fn::Join': ['-', 'bar']} is not of type 'integer'"],
        [],
    ),
]

_getazs_tests: List[Tuple] = [
    (
        "Valid Fn::GetAZs with empty string",
        {"Fn::GetAZs": ""},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Valid Fn::GetAZs with Ref",
        {"Fn::GetAZs": {"Ref": "AWS::Region"}},
        {"type": "array"},
        [],
        [],
    ),
    (
        "Invalid Fn::GetAZs with an invalid output type",
        {"Fn::GetAZs": {"Ref": "AWS::Region"}},
        {"type": "string"},
        ["{'Fn::GetAZs': {'Ref': 'AWS::Region'}} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::GetAZs with Ref to a bad pseudo-parameter",
        {"Fn::GetAZs": {"Ref": "AWS::Partition"}},
        {"type": "array"},
        [
            (
                "{'Ref': 'AWS::Partition'} is not one of "
                f"{[''] + REGIONS!r} when 'Ref' is resolved"
            )
        ],
        [],
    ),
    (
        "Invalid Fn::GetAZs with a bad value type",
        {"Fn::GetAZs": ["foo"]},
        {"type": "array"},
        [
            "['foo'] is not of type 'string'",
            f"['foo'] is not one of {[''] + REGIONS!r}",
        ],
        [],
    ),
]

_importvalue_tests: List[Tuple] = [
    (
        "Valid Fn::ImportValue with a string",
        {"Fn::ImportValue": "foo"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::ImportValue with an invalid type",
        {"Fn::ImportValue": ["foo"]},
        {"type": "string"},
        ["['foo'] is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::ImportValue with an invalid output type",
        {"Fn::ImportValue": "foo"},
        {"type": "array"},
        ["{'Fn::ImportValue': 'foo'} is not of type 'array'"],
        [],
    ),
    (
        "Valid Fn::ImportValue with a function",
        {"Fn::ImportValue": {"Fn::Sub": "foo"}},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::ImportValue with an invalid function",
        {"Fn::ImportValue": {"Fn::Split": "foo"}},
        {"type": "string"},
        ["{'Fn::Split': 'foo'} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::ImportValue with a Ref to a resource",
        {"Fn::ImportValue": {"Ref": "MyResource"}},
        {"type": "string"},
        [
            (
                "'MyResource' is not one of ['AWS::NoValue', "
                "'AWS::AccountId', 'AWS::Partition', "
                "'AWS::Region', 'AWS::StackId', 'AWS::StackName', "
                "'AWS::URLSuffix', 'AWS::NotificationARNs']"
            )
        ],
        [],
    ),
]

_if_tests: List[Tuple] = [
    (
        "Valid Fn::If",
        {"Fn::If": ["condition", "foo", "bar"]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::If with to many arguments",
        {"Fn::If": ["condition", "foo", "bar", "key"]},
        {"type": "string"},
        ["['condition', 'foo', 'bar', 'key'] is too long"],
        [],
    ),
    (
        "Invalid Fn::If with bad first element",
        {"Fn::If": ["condition", {"foo": "bar"}, "bar"]},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'string'"],
        [],
    ),
    (
        "Invalid Fn::If with bad first element",
        {"Fn::If": ["condition", "foo", {"foo": "bar"}]},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'string'"],
        [],
    ),
]

_sub_tests: List[Tuple] = [
    (
        "Valid Fn::Sub",
        {"Fn::Sub": "foo"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Sub with an incorrect type",
        {"Fn::Sub": {"foo": "bar"}},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'array', 'string'"],
        [],
    ),
    (
        "Invalid Fn::Sub with an invalid output type",
        {"Fn::Sub": "foo"},
        {"type": "array"},
        ["{'Fn::Sub': 'foo'} is not of type 'array'"],
        [],
    ),
    (
        "Valid Fn::Sub with a valid Ref",
        {"Fn::Sub": "${AWS::Region}"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Sub with a invalid Ref",
        {"Fn::Sub": "${foo}"},
        {"type": "string"},
        [
            (
                "'foo' is not one of ['MyResource', 'AWS::NoValue', 'AWS::AccountId', "
                "'AWS::Partition', 'AWS::Region', 'AWS::StackId', "
                "'AWS::StackName', 'AWS::URLSuffix', "
                "'AWS::NotificationARNs']"
            ),
        ],
        [],
    ),
    (
        "Valid Fn::Sub with a Ref to parameter",
        {"Fn::Sub": ["${foo}", {"foo": "bar"}]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Valid Fn::Sub with an escape character",
        {"Fn::Sub": "${!foo}"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Sub with a bad object",
        {"Fn::Sub": ["${foo}", []]},
        {"type": "string"},
        ["[] is not of type 'object'"],
        [],
    ),
    (
        "Invalid Fn::Sub with a bad object type",
        {
            "Fn::Sub": [
                "${foo}",
                {
                    "foo": [],
                },
            ]
        },
        {"type": "string"},
        ["[] is not of type 'string'"],
        [],
    ),
    (
        "Valid Fn::Sub with a GetAtt",
        {"Fn::Sub": "${MyResource.Arn}"},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::Sub with a GetAtt and a bad attribute",
        {"Fn::Sub": "${MyResource.Foo}"},
        {"type": "string"},
        [
            (
                "'MyResource.Foo' is not one of ['MyResource.Arn', "
                "'MyResource.DomainName', "
                "'MyResource.DualStackDomainName', "
                "'MyResource.RegionalDomainName', "
                "'MyResource.WebsiteURL']"
            )
        ],
        [],
    ),
    (
        "Invalid Fn::Sub with a GetAtt and a bad resource name",
        {"Fn::Sub": "${Foo.Bar}"},
        {"type": "string"},
        ["'Foo.Bar' is not one of ['MyResource']"],
        [],
    ),
]

# Fn::FindInMap
_findinmap_tests: List[Tuple] = [
    (
        "Valid Fn::FindInMap",
        {"Fn::FindInMap": ["foo", "bar", "key"]},
        {"type": "string"},
        [],
        [],
    ),
    (
        "Invalid Fn::FindInMap too long",
        {"Fn::FindInMap": ["foo", "bar", "key", "key2"]},
        {"type": "string"},
        ["['foo', 'bar', 'key', 'key2'] is too long"],
        [],
    ),
    (
        "Invalid Fn::FindInMap with wrong type",
        {"Fn::FindInMap": {"foo": "bar"}},
        {"type": "string"},
        ["{'foo': 'bar'} is not of type 'array'"],
        [],
    ),
    (
        "Invalid Fn::FindInMap with wrong function",
        {"Fn::FindInMap": [{"Fn::GetAtt": "MyResource.Arn"}, "foo", "bar"]},
        {"type": "string"},
        ["{'Fn::GetAtt': 'MyResource.Arn'} is not of type 'string'"],
        [],
    ),
]

# Fn::Length
_length_tests: List[Tuple] = [
    (
        "Fn::Length is not supported",
        {"Fn::Length": []},
        {"type": "integer"},
        ["Fn::Length is not supported without 'AWS::LanguageExtensions' transform"],
        [],
    ),
]

# Fn::ToJsonString
_tojsonstring_tests: List[Tuple] = [
    (
        "Fn::ToJsonString is not supported",
        {"Fn::ToJsonString": []},
        {"type": "string"},
        [
            (
                "Fn::ToJsonString is not supported without "
                "'AWS::LanguageExtensions' transform"
            )
        ],
        [],
    ),
]

# Fn::ForEach
_foreach_tests: List[Tuple] = [
    (
        "Fn::ForEach is not supported",
        {"Fn::ForEach::Foo": []},
        {"type": "object"},
        [
            (
                "Fn::ForEach::Foo is not supported without "
                "'AWS::LanguageExtensions' transform"
            )
        ],
        [],
    ),
]


@pytest.mark.parametrize(
    "name,instance,schema,errors,cfn_response",
    _ref_tests
    + _base64_tests
    + _cidr_tests
    + _findinmap_tests
    + _if_tests
    + _foreach_tests
    + _getatt_tests
    + _getazs_tests
    + _importvalue_tests
    + _join_tests
    + _length_tests
    + _select_tests
    + _split_tests
    + _sub_tests
    + _tojsonstring_tests,
)
def test_functions(name, instance, schema, errors, cfn_response):
    message_errors(name, instance, schema, errors)


@pytest.mark.parametrize(
    "name,instance,schema,errors,cfn_response",
    [
        (
            "Valid Ref with a Ref",
            {"Ref": {"Ref": "MyResource"}},
            {"type": "string"},
            [],
            [],
        ),
        (
            "Valid GetAtt with a Ref",
            {"Fn::GetAtt": [{"Ref": "MyResourceParameter"}, {"Ref": "MyResource"}]},
            {"type": "string"},
            [],
            [],
        ),
        (
            "Invalid Fn::FindInMap with default value",
            {"Fn::FindInMap": ["foo", "bar", "key", {"DefaultValue": "default"}]},
            {"type": "string"},
            [],
            [],
        ),
        (
            "Invalid Fn::FindInMap with default value",
            {"Fn::FindInMap": ["foo", "bar", "key", {"Default": "default"}]},
            {"type": "string"},
            [
                "Additional properties are not allowed ('Default' was unexpected)",
                "'DefaultValue' is a required property",
            ],
            [],
        ),
        (
            "Fn::Length valid structure",
            {"Fn::Length": []},
            {"type": "integer"},
            [],
            [],
        ),
        (
            "Fn::Length invalid type",
            {"Fn::Length": "foo"},
            {"type": "integer"},
            ["'foo' is not of type 'array'"],
            [],
        ),
        (
            "Fn::Length invalid output type",
            {"Fn::Length": ["foo"]},
            {"type": "array"},
            ["{'Fn::Length': ['foo']} is not of type 'array'"],
            [],
        ),
        (
            "Fn::Length using valid function",
            {"Fn::Length": {"Fn::GetAZs": ""}},
            {"type": "integer"},
            [],
            [],
        ),
        (
            "Fn::Length using valid functions in array",
            {"Fn::Length": [{"Ref": "MyResource"}]},
            {"type": "integer"},
            [],
            [],
        ),
        (
            "Fn::ToJsonString is valid",
            {"Fn::ToJsonString": {"foo": "bar"}},
            {"type": "string"},
            [],
            [],
        ),
        (
            "Fn::ToJsonString is invalid with wrong type",
            {"Fn::ToJsonString": "foo"},
            {"type": "string"},
            ["'foo' is not of type 'array', 'object'"],
            [],
        ),
        (
            "Fn::ToJsonString is invalid with wrong output type",
            {"Fn::ToJsonString": {"foo": "bar"}},
            {"type": "object"},
            ["{'Fn::ToJsonString': {'foo': 'bar'}} is not of type 'object'"],
            [],
        ),
        (
            "Fn::ToJsonString is valid array with functions",
            {"Fn::ToJsonString": [{"Ref": "MyResource"}]},
            {"type": "string"},
            [],
            [],
        ),
        (
            "Fn::ToJsonString is valid object with functions",
            {"Fn::ToJsonString": {"Key": {"Ref": "MyResource"}}},
            {"type": "string"},
            [],
            [],
        ),
        # Fn::ForEach
        (
            "Valid Fn::ForEach",
            {"Fn::ForEach::Test": ["foo", ["foo", "bar"], {"foo${foo}": "bar"}]},
            {"type": "object"},
            [],
            [],
        ),
        (
            "Invalid Fn::ForEach with invalid length",
            {"Fn::ForEach::Test": ["foo", ["foo", "bar"]]},
            {"type": "object"},
            ["['foo', ['foo', 'bar']] is too short"],
            [],
        ),
        (
            "Invalid Fn::ForEach with invalid output type",
            {"Fn::ForEach::Test": ["foo", ["foo", "bar"], {"foo${foo}": "bar"}]},
            {"type": "string"},
            [
                (
                    "{'Fn::ForEach::Test': ['foo', ['foo', 'bar'], "
                    "{'foo${foo}': 'bar'}]} is not of type 'string'"
                )
            ],
            [],
        ),
        (
            "Invalid Fn::ForEach with invalid identifier type",
            {"Fn::ForEach::Test": [[], ["foo", "bar"], {"foo${foo}": "bar"}]},
            {"type": "object"},
            ["[] is not of type 'string'"],
            [],
        ),
        (
            "Invalid Fn::ForEach with invalid collection type",
            {"Fn::ForEach::Test": ["foo", {"foo": "bar"}, {"foo${foo}": "bar"}]},
            {"type": "object"},
            ["{'foo': 'bar'} is not of type 'array'"],
            [],
        ),
        (
            "Invalid Fn::ForEach with invalid output type",
            {"Fn::ForEach::Test": ["foo", ["bar"], []]},
            {"type": "array"},
            [
                "{'Fn::ForEach::Test': ['foo', ['bar'], []]} is not of type 'array'",
                "[] is not of type 'object'",
            ],
            [],
        ),
        (
            "Valid Fn::ForEach with valid output from schema",
            {"Fn::ForEach::Test": ["id", ["bar"], {"foo-${id}": "bar"}]},
            {
                "type": "object",
                "properties": {"foo-bar": {"type": "string", "enum": ["bar"]}},
                "additionalProperties": False,
            },
            [],
            [],
        ),
        (
            "Valid Fn::ForEach with a valid Ref value",
            {
                "Fn::ForEach::Test": [
                    "id",
                    [{"Ref": "MyParameter"}],
                    {"foo-${id}": "bar"},
                ]
            },
            {
                "type": "object",
                "properties": {"foo-bar": {"type": "string", "enum": ["bar"]}},
                "additionalProperties": False,
            },
            [],
            [],
        ),
    ],
)
def test_language_extension_functions(name, instance, schema, errors, cfn_response):
    message_transform_errors(name, instance, schema, errors)
