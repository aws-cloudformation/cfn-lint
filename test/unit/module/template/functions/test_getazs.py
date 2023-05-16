import json
import unittest
from typing import Any, Iterable
from unittest import mock

from cfnlint.helpers import AVAILABILITY_ZONES
from cfnlint.template.functions import FnGetAZs
from cfnlint.template.functions.exceptions import Unpredictable


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
        source = {"Ref": "AWS::Region"}
        split = FnGetAZs(source)

        class Fns:
            def get_value_by_hash(self, hash_, region) -> Iterable[Any]:
                if hash(json.dumps(source)) == hash_:
                    yield "us-east-1"
                return

        with mock.patch.dict(
            AVAILABILITY_ZONES, {"us-east-1": ["foo", "bar"]}, clear=True
        ):
            self.assertListEqual(
                list(split.get_value(Fns(), "us-east-1")), [["foo", "bar"]]
            )

    def test_fn_nested_fn_no_value(self):
        source = {"Ref": "Foo"}
        split = FnGetAZs(source)

        class Fns:
            def get_value_by_hash(self, hash_, region) -> Iterable[Any]:
                if hash(json.dumps(source)) != hash_:
                    yield "us-east-1"
                raise Unpredictable("Error")

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(Fns(), "us-east-1"))

    def test_fn_nested_fn_non_string(self):
        source = {"Ref": "Foo"}
        split = FnGetAZs(source)

        class Fns:
            def get_value_by_hash(self, hash_, region) -> Iterable[Any]:
                if hash(json.dumps(source)) == hash_:
                    yield []
                raise Unpredictable("Error")

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(Fns(), "us-east-1"))
