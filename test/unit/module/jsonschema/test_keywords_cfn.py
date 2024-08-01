"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest
from collections import namedtuple
from typing import List

from cfnlint.context import Context
from cfnlint.jsonschema._keywords_cfn import FnItems, cfn_type
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
        context = Context(regions=["us-east-1"], strict_types=False)
        cls = kwargs.pop("cls", cfn_validator(schema=schema, context=context))
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

    def test_null_values(self):
        self.message_errors(
            "Null value with string type",
            None,
            ["None is not of type 'string'"],
            {"type": "string"},
        )
        self.message_errors(
            "String value with null type",
            "foo",
            ["'foo' is not of type 'null'"],
            {"type": "null"},
        )
        self.message_errors(
            "Object value with null type",
            {},
            ["{} is not of type 'null'"],
            {"type": "null"},
        )
        self.message_errors(
            "None value with multiple types",
            None,
            [],
            {"type": ["string", "null"]},
        )


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


class TestFnItems(Base):

    def test_change_type(self):
        schema = [
            {
                "schema": {"type": "string"},
            },
        ]
        validator = CfnTemplateValidator({})

        items = list(FnItems().validate(validator, schema, [1], {}))

        self.assertListEqual(items, [])
