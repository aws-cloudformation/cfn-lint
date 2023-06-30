"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest
from collections import namedtuple
from typing import List

from cfnlint.context.value import Value, ValueType
from cfnlint.jsonschema.exceptions import UnknownType
from cfnlint.jsonschema.validators import CfnTemplateValidator
from cfnlint.template.functions import Unpredictable


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

    def get_object_without_conditions(self, obj, property_names=None):
        return [{"Scenario": None, "Object": obj}]


_T = namedtuple("_T", ["name", "instance", "schema", "errors", "cfn_response"])


class Base(unittest.TestCase):
    def message_errors(self, name, instance, errors, schema, **kwargs):
        cls = kwargs.pop("cls", CfnTemplateValidator(schema=schema))
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


class TestCfnTypesUnpredicted(Base):
    def build_execute_tests(self, fn_name, supported_types):
        _all_types = ["string", "number", "integer", "boolean", "array", "object"]
        tests: List[_T] = []
        for t in _all_types:
            instance = {fn_name: "a"}
            if t in supported_types:
                tests.append(
                    _T(
                        f"{fn_name} can return {t}",
                        instance,
                        {"type": t},
                        [],
                        [Unpredictable(None)],
                    )
                )
            else:
                tests.append(
                    _T(
                        f"{fn_name} cannot return {t}",
                        instance,
                        {"type": t},
                        [f"{instance!r} is not of type {t!r}"],
                        [Unpredictable(None)],
                    )
                )
        self.iterate_tests(tests)

    def test_ref(self):
        tests: List[_T] = [
            _T(
                "Unpredictable: Ref returns singular value",
                {"Ref": "foo"},
                {"type": "number"},
                [],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref can return array",
                {"Ref": "foo"},
                {"type": "array"},
                [],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref cannot return an object",
                {"Ref": "foo"},
                {"type": "object"},
                ["{'Ref': 'foo'} is not of type 'object'"],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref can return string with string pseudo parameter",
                {"Ref": "AWS::Region"},
                {"type": "string"},
                [],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref cannot return array with string pseudo parameter",
                {"Ref": "AWS::Region"},
                {"type": "array"},
                ["{'Ref': 'AWS::Region'} is not of type 'array'"],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref can return array with array pseudo parameter",
                {"Ref": "AWS::NotificationARNs"},
                {"type": "array"},
                [],
                [Unpredictable(None)],
            ),
            _T(
                "Unpredictable: Ref cannot return array with string pseudo parameter",
                {"Ref": "AWS::NotificationARNs"},
                {"type": "string"},
                ["{'Ref': 'AWS::NotificationARNs'} is not of type 'string'"],
                [Unpredictable(None)],
            ),
            _T(
                "Ref will not return an error on NoValue",
                {"Ref": "AWS::NoValue"},
                {"type": "object"},
                [],
                [],
            ),
        ]

        self.iterate_tests(tests)

    def test_fn_base64(self):
        self.build_execute_tests("Fn::Base64", ["string"])

    def test_fn_cidr(self):
        self.build_execute_tests("Fn::Cidr", ["array"])

    def test_fn_if(self):
        tests: List[_T] = [
            _T(
                "Fn::If follows provides two errors",
                {"Fn::If": ["Condition", "foo", "bar"]},
                {"type": "array"},
                ["'foo' is not of type 'array'", "'bar' is not of type 'array'"],
                [],
            ),
            _T(
                "Fn::If provides errors from left side",
                {"Fn::If": ["Condition", "foo", []]},
                {"type": "array"},
                ["'foo' is not of type 'array'"],
                [],
            ),
            _T(
                "Fn::If provides errors from right side",
                {"Fn::If": ["Condition", "foo", []]},
                {"type": "string"},
                ["[] is not of type 'string'"],
                [],
            ),
        ]

        self.iterate_tests(tests)

    def test_fn_find_in_map(self):
        self.build_execute_tests(
            "Fn::FindInMap", ["array", "string", "integer", "number", "boolean"]
        )

    def test_fn_getatt(self):
        self.build_execute_tests(
            "Fn::GetAtt", ["array", "string", "integer", "number", "boolean", "object"]
        )

    def test_fn_getazs(self):
        self.build_execute_tests("Fn::GetAZs", ["array"])

    def test_fn_importvalue(self):
        self.build_execute_tests(
            "Fn::ImportValue", ["string", "integer", "number", "boolean"]
        )

    def test_fn_join(self):
        self.build_execute_tests("Fn::Join", ["string", "number", "integer", "boolean"])

    def test_fn_length(self):
        self.build_execute_tests("Fn::Length", ["string", "integer", "number"])

    def test_fn_select(self):
        self.build_execute_tests(
            "Fn::Select", ["string", "integer", "number", "array", "boolean", "object"]
        )

    def test_fn_split(self):
        self.build_execute_tests("Fn::Split", ["array"])

    def test_fn_sub(self):
        self.build_execute_tests("Fn::Sub", ["string", "integer", "number", "boolean"])

    def test_fn_to_json_string(self):
        self.build_execute_tests("Fn::ToJsonString", ["string"])


class TestCfnTypes(Base):
    def build_execute_tests(self, instance, supported_types):
        _all_types = ["string", "number", "integer", "boolean", "array", "object"]
        tests: List[_T] = []
        for t in _all_types:
            if t in supported_types:
                tests.append(
                    _T(
                        f"{instance} can return {t}",
                        instance,
                        {"type": t},
                        [],
                        [Unpredictable(None)],
                    )
                )
            else:
                tests.append(
                    _T(
                        f"{instance} cannot return {t}",
                        instance,
                        {"type": t},
                        [f"{instance!r} is not of type {t!r}"],
                        [Unpredictable(None)],
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
    def build_execute_tests(self, instance, supported_types, unsupported_type):
        tests: List[_T] = []
        check_types = supported_types + [unsupported_type]
        tests.append(
            _T(
                f"{instance} can return one of {check_types!r}",
                instance,
                {"type": check_types},
                [],
                [Unpredictable(None)],
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


class TestCfnPredictedValues(Base):
    def build_execute_tests(self, instance, supported_types, predictions):
        tests: List[_T] = []
        tests.append(
            _T(
                f"{instance} will fail on unsupported cfn response {supported_types!r}",
                instance,
                {"type": supported_types},
                [f"{instance!r} is not of type {supported_types!r}"],
                predictions,
            )
        )

        self.iterate_tests(tests)

    def test_standard_values(self):
        # all these checks should return true as there is one good value
        self.build_execute_tests(
            {"Ref": "Foo"},
            "integer",
            [
                Value(value=[1, "2"], value_type=ValueType.FUNCTION),
            ],
        )


class TestCfnTypeFailure(Base):
    def test_cfn_type_failure(self):
        with self.assertRaises(UnknownType) as err:
            CfnTemplateValidator({}).is_type("foo", "bar")
        self.assertIn(
            "Unknown type 'bar' for validator with schema", str(err.exception)
        )
