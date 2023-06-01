import json
import unittest
from typing import Any, Iterable
from unittest import mock

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.template.functions import FnGetAZs
from cfnlint.template.functions.exceptions import Unpredictable


def create_fns(instance, yield_value, raise_error=False):
    class Fns:
        def get_value_by_hash(self, hash_, region) -> Iterable[Any]:
            if hash(json.dumps(instance)) != hash_:
                yield yield_value
            if raise_error:
                raise Unpredictable("Error")

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

        fns = create_fns(instance=instance, yield_value="us-east-1")()

        with mock.patch.dict(
            AVAILABILITY_ZONES, {"us-east-1": ["foo", "bar"]}, clear=True
        ):
            print("start")
            self.assertListEqual(list(fn.get_value(fns, "us-east-1")), [["foo", "bar"]])
            print("end")

    def test_fn_nested_fn_no_value(self):
        instance = {"Ref": "Foo"}
        fn = FnGetAZs(instance)

        fns = create_fns(instance=instance, yield_value="us-east-1", raise_error=True)()

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_fn_nested_fn_non_string(self):
        instance = {"Ref": "Foo"}
        fn = FnGetAZs(instance)

        fns = create_fns(instance=instance, yield_value=[], raise_error=True)()

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_invalid_structure(self):
        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(FnGetAZs(["us-east-1"]).get_value(None, "us-east-1"))

        with self.assertRaises(Unpredictable):
            list(FnGetAZs({"Ref": "Foo", "Foo": "Bar"}).get_value(None, "us-east-1"))
