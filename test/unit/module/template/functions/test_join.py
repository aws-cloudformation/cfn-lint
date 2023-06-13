import json
import unittest
from typing import Any, Iterable

from cfnlint.context import Value, ValueType
from cfnlint.template.functions import Fn, FnJoin
from cfnlint.template.functions.exceptions import Unpredictable


class TestFnjoin(unittest.TestCase):
    def test_join_list(self):
        join = FnJoin([",", ["foo", "bar"]])
        self.assertListEqual(
            list(join.get_value(None, "us-east-1")),
            [Value(value="foo,bar", value_type=ValueType.FUNCTION)],
        )

    def test_join_nested_fn(self):
        source = {"Ref": "Foo"}
        fn = FnJoin([",", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield ["foo", "bar"]

        fns = {hash(json.dumps(source)): Foo(source)}

        self.assertListEqual(
            list(fn.get_value(fns, "us-east-1")),
            [Value(value="foo,bar", value_type=ValueType.FUNCTION)],
        )

    def test_join_nested_fn_no_value(self):
        source = {"Ref": "Foo"}
        fn = FnJoin([",", [source]])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                return
                yield

        fns = {hash(json.dumps(source)): Foo(source)}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_join_nested_fn_and_strings(self):
        source = {"Ref": "Foo"}
        fn = FnJoin([",", ["a", source, "c"]])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield "b1"
                yield "b2"

        fns = {hash(json.dumps(source)): Foo(source)}
        self.assertListEqual(
            list(fn.get_value(fns, "us-east-1")),
            [
                Value(value="a,b1,c", value_type=ValueType.FUNCTION),
                Value(value="a,b2,c", value_type=ValueType.FUNCTION),
            ],
        )

    def test_join_nested_fn_non_list(self):
        source = {"Ref": "Foo"}
        fn = FnJoin([",", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

            def get_value(self, fns, region: str) -> Iterable[Any]:
                yield ""

        fns = {hash(json.dumps(source)): Foo(source)}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_join_nested_fn_raise(self):
        source = {"Ref": "Foo"}
        fn = FnJoin(["-", source])

        class Foo(Fn):
            def __init__(self, instance: Any) -> None:
                super().__init__(instance)

        fns = {hash(json.dumps(source)): Foo(source)}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_join_nested_fn_not_found(self):
        source = {"Ref": "Foo"}
        fn = FnJoin([",", source])

        fns = {}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_join_nested_fn_not_found_list(self):
        source = [{"Ref": "Foo"}]
        fn = FnJoin([",", source])

        fns = {}

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(fn.get_value(fns, "us-east-1"))

    def test_join_invalid(self):
        # bad function
        join = FnJoin([",", {"Foo": "Bar"}])
        self.assertFalse(join.is_valid)

        # dict
        join = FnJoin([",", {"Foo": "Foo", "Bar": "Bar"}])
        self.assertFalse(join.is_valid)

        # wrong sized list
        join = FnJoin([","])
        self.assertFalse(join.is_valid)

        # bad delimiter
        join = FnJoin([[], "Foo"])
        self.assertFalse(join.is_valid)

        # join object
        join = FnJoin({"Foo": "Bar"})
        self.assertFalse(join.is_valid)

        # join nested object
        join = FnJoin([",", [{"Foo": "Foo", "Bar": "Bar"}]])
        self.assertFalse(join.is_valid)

        # join with list
        join = FnJoin([",", [[], ""]])
        self.assertFalse(join.is_valid)

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(join.get_value(None, "us-east-1"))
