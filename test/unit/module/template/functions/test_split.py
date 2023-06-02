import json
import unittest
from collections import UserDict
from typing import Any, Iterable

from cfnlint.template.functions import Fn, FnSplit
from cfnlint.template.functions.exceptions import Unpredictable


class TestFnSplit(unittest.TestCase):
    def test_split_string(self):
        split = FnSplit([",", "foo,bar"])

        self.assertListEqual(list(split.get_value(None, "us-east-1")), [["foo", "bar"]])

    def test_split_nested_fn(self):
        source = {"Ref": "Foo"}
        split = FnSplit(["-", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield "foo-bar"

        fns = {hash(json.dumps(source)): Foo(source)}

        self.assertListEqual(list(split.get_value(fns, "us-east-1")), [["foo", "bar"]])

    def test_split_nested_fn_no_value(self):
        source = {"Ref": "Foo"}
        split = FnSplit(["-", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                return
                yield

        fns = {hash(json.dumps(source)): Foo(source)}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(fns, "us-east-1"))

    def test_split_nested_fn_non_string(self):
        source = {"Ref": "Foo"}
        split = FnSplit(["-", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield []

        class Fns(UserDict):
            def __init__(self) -> None:
                super().__init__()
                self.data[hash(json.dumps(source))] = Foo(source)

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(Fns(), "us-east-1"))

    def test_split_nested_fn_raise(self):
        source = {"Ref": "Foo"}
        split = FnSplit(["-", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

        fns = {hash(json.dumps(source)): Foo(source)}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(fns, "us-east-1"))

    def test_split_nested_fn_not_found(self):
        source = {"Ref": "Foo"}
        split = FnSplit(["-", source])

        class Fns(UserDict):
            def __init__(self) -> None:
                super().__init__()

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(Fns(), "us-east-1"))

    def test_split_invalid(self):
        # bad function
        split = FnSplit(["-", {"Foo": "Bar"}])
        self.assertFalse(split.is_valid)

        # dict
        split = FnSplit(["-", {"Foo": "Foo", "Bar": "Bar"}])
        self.assertFalse(split.is_valid)

        # wrong sized list
        split = FnSplit(["-"])
        self.assertFalse(split.is_valid)

        # bad delimiter
        split = FnSplit([[], "Foo"])
        self.assertFalse(split.is_valid)

        # split object
        split = FnSplit({"Foo": "Bar"})
        self.assertFalse(split.is_valid)

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(split.get_value(None, "us-east-1"))
