import json
import unittest
from collections import UserDict
from typing import Any, Iterable
from unittest import mock

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.template.functions import FnGetAZs
from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn


def create_fns(instance, fn):
    class Fns(UserDict):
        def __init__(self) -> None:
            super().__init__()
            self.data[hash(json.dumps(instance))] = fn(instance)

    return Fns


class TestFnGetAZs(unittest.TestCase):
    def test_fn_string(self):
        split = FnGetAZs("us-east-1")

        with mock.patch.dict(
            AVAILABILITY_ZONES, {"us-east-1": ["foo", "bar"]}, clear=True
        ):
            self.assertListEqual(
                list(split.get_value(None, "us-east-1")), [["foo", "bar"]]
            )

    def test_fn_nested_fn(self):
        instance = {"Ref": "AWS::Region"}
        fn = FnGetAZs(instance)

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield "us-east-1"

        fns = create_fns(instance=instance, fn=Foo)()

        with mock.patch.dict(
            AVAILABILITY_ZONES, {"us-east-1": ["foo", "bar"]}, clear=True
        ):
            self.assertListEqual(list(fn.get_value(fns, "us-east-1")), [["foo", "bar"]])

    def test_fn_nested_fn_no_value(self):
        instance = {"Ref": "Foo"}
        fn = FnGetAZs(instance)

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                raise Unpredictable("Error")

        fns = create_fns(instance=instance, fn=Foo)()

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_fn_nested_fn_non_string(self):
        instance = {"Ref": "Foo"}
        fn = FnGetAZs(instance)

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield []

        fns = create_fns(instance=instance, fn=Foo)()

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_invalid_structure(self):
        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(FnGetAZs(["us-east-1"]).get_value(None, "us-east-1"))

        with self.assertRaises(Unpredictable):
            list(FnGetAZs({"Ref": "Foo", "Foo": "Bar"}).get_value(None, "us-east-1"))
