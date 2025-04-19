"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context._mappings import Mappings
from cfnlint.context.context import (
    Context,
    Parameter,
    Path,
    Resource,
    create_context_for_template,
)
from cfnlint.jsonschema import ValidationError
from cfnlint.jsonschema.validators import CfnTemplateValidator
from cfnlint.template import Template


def _resolve(name, instance, expected_results, **kwargs):
    validator = CfnTemplateValidator().evolve(**kwargs)

    resolutions = list(validator.resolve_value(instance))

    assert len(resolutions) == len(
        expected_results
    ), f"{name!r} got {len(resolutions)!r}"

    for i, (instance, v, errors) in enumerate(resolutions):
        assert instance == expected_results[i][0], f"{name!r} got {instance!r}"
        assert errors == expected_results[i][2], f"{name!r} got {errors!r}"
        if not errors:
            expected_context = expected_results[i][1]
            _, expected_context = list(expected_context.ref_value("AWS::Region"))[0]
            assert (
                v.context.path == expected_context.path
            ), f"{name!r} got {v.context.path!r}"
            assert (
                v.context.ref_values == expected_context.ref_values
            ), f"{name!r} got {v.context.ref_values!r}"


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Valid Ref with a single instance",
            {"Ref": {"Ref": "MyResource"}},
            [],
        ),
    ],
)
def test_resolvers_ref(name, instance, response):
    _resolve(name, instance, response)


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Invalid Ref with an array",
            {"Ref": []},
            [],
        ),
        (
            "Invalid Ref with an invalid object",
            {"Ref": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid Join with an invalid type",
            {"Fn::Join": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid Join with an invalid array length",
            {"Fn::Join": ["a", "b", "c"]},
            [],
        ),
        (
            "Invalid Join with an invalid type for first element",
            {"Fn::Join": [["a"], "b"]},
            [],
        ),
        (
            "Invalid Join with an invalid type for second element",
            {"Fn::Join": ["a", "b"]},
            [],
        ),
        (
            "Invalid Join with an invalid type for second element item",
            {"Fn::Join": ["/", [["a"], "b"]]},
            [],
        ),
        (
            "Invalid Select with an invalid type",
            {"Fn::Select": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid Select with an invalid array length",
            {"Fn::Select": ["a", "b", "c"]},
            [],
        ),
        (
            "Invalid Select with an invalid type for second element",
            {"Fn::Select": ["a", "b"]},
            [],
        ),
        (
            "Invalid Select with an invalid type for second element",
            {"Fn::Select": [0, "b"]},
            [],
        ),
        (
            "Invalid Split with an invalid type",
            {"Fn::Split": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid Split with an invalid array length",
            {"Fn::Split": ["a", "b", "c"]},
            [],
        ),
        (
            "Invalid Split with an invalid type for first element",
            {"Fn::Split": [0, "b"]},
            [],
        ),
        (
            "Invalid Split with an invalid type for second element",
            {"Fn::Split": ["a", ["b"]]},
            [],
        ),
        (
            "Invalid GetAZs with an invalid type ",
            {"Fn::GetAZs": {"a": "b"}},
            [],
        ),
        (
            "Invalid GetAZs with an invalid type ",
            {"Fn::GetAZs": ["a", "b"]},
            [],
        ),
        (
            "Invalid GetAZs with an invalid region",
            {"Fn::GetAZs": "foo"},
            [],
        ),
        (
            "Invalid FindInMap with an invalid type",
            {"Fn::FindInMap": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid FindInMap with an invalid length",
            {"Fn::FindInMap": ["foo", "bar"]},
            [],
        ),
        (
            "Invalid FindInMap with an invalid type for first element",
            {"Fn::FindInMap": [["foo"], "bar", "value"]},
            [],
        ),
        (
            "Invalid FindInMap with an invalid type for second element",
            {"Fn::FindInMap": ["foo", ["bar"], "value"]},
            [],
        ),
        (
            "Invalid FindInMap with an invalid type for third element",
            {"Fn::FindInMap": ["foo", "first", ["value"]]},
            [],
        ),
        (
            "Invalid FnSub with an invalid type",
            {"Fn::Sub": {"foo": "bar"}},
            [],
        ),
        (
            "Invalid FnSub with an array of wrong length",
            {"Fn::Sub": ["foo", "bar", "value"]},
            [],
        ),
        (
            "Invalid FnSub with the wrong type for element one",
            {"Fn::Sub": [["foo"], {"foo": "bar"}]},
            [],
        ),
        (
            "Invalid FnSub with the wrong type for element two",
            {"Fn::Sub": ["foo", ["bar"]]},
            [],
        ),
    ],
)
def test_invalid_functions(name, instance, response):
    context = Context(
        mappings=Mappings.create_from_dict({"foo": {"first": {"second": "bar"}}})
    )

    _resolve(name, instance, response, context=context)


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Valid Join with an empty type",
            {"Fn::Join": [".", []]},
            [],
        ),
        (
            "Valid Join with a list of strings",
            {"Fn::Join": [".", ["a", "b", "c"]]},
            [("a.b.c", Context(), None)],
        ),
        (
            "Valid GetAZs with empty string",
            {"Fn::GetAZs": ""},
            [
                (
                    [
                        "us-east-1a",
                        "us-east-1b",
                        "us-east-1c",
                        "us-east-1d",
                        "us-east-1e",
                        "us-east-1f",
                    ],
                    Context(),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with bad keys and a default value",
            {"Fn::FindInMap": ["foo", "bar", "value", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with valid keys and a default value",
            {"Fn::FindInMap": ["foo", "first", "second", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                ),
                (
                    "bar",
                    Context(
                        path=Path(
                            value_path=deque(["Mappings", "foo", "first", "second"])
                        )
                    ),
                    None,
                ),
            ],
        ),
        (
            "Valid FindInMap with a bad mapping",
            {"Fn::FindInMap": ["bar", "first", "second"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        (
                            "'bar' is not one of ['foo', "
                            "'transformFirstKey', 'transformSecondKey', "
                            "'integers', 'accounts', 'environments']"
                        ),
                        path=deque(["Fn::FindInMap", 0]),
                    ),
                )
            ],
        ),
        (
            "Valid FindInMap with a bad mapping and default",
            {"Fn::FindInMap": ["bar", "first", "second", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with a bad mapping and aws no value",
            {
                "Fn::FindInMap": [
                    "bar",
                    "first",
                    "second",
                    {"DefaultValue": {"Ref": "AWS::NoValue"}},
                ]
            },
            [],
        ),
        (
            "Valid FindInMap with a bad top key",
            {"Fn::FindInMap": ["foo", "second", "first"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        ("'second' is not one of ['first'] for " "mapping 'foo'"),
                        path=deque(["Fn::FindInMap", 1]),
                    ),
                )
            ],
        ),
        (
            "Valid FindInMap with a bad top key and default",
            {"Fn::FindInMap": ["foo", "second", "first", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with a map name that is a Ref to pseudo param",
            {"Fn::FindInMap": [{"Ref": "AWS::StackName"}, "first", "second"]},
            [],
        ),
        (
            "Valid FindInMap with an top level key that is a Ref to an account",
            {"Fn::FindInMap": ["accounts", {"Ref": "AWS::AccountId"}, "dev"]},
            [
                (
                    "bar",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "accounts", "123456789012", "dev"]
                            )
                        ),
                    ),
                    None,
                )
            ],
        ),
        (
            (
                "Valid FindInMap with an top level key "
                "that is a Ref to non account non region"
            ),
            {"Fn::FindInMap": ["accounts", {"Ref": "AWS::StackName"}, "dev"]},
            [
                (
                    "bar",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "accounts", "123456789012", "dev"]
                            )
                        ),
                    ),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with an top level key that is a Ref to a region",
            {"Fn::FindInMap": ["accounts", {"Ref": "AWS::Region"}, "bar"]},
            [
                (
                    "foo",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "accounts", "us-east-1", "bar"]
                            )
                        ),
                    ),
                    None,
                )
            ],
        ),
        (
            "Invalid FindInMap with an top level key that is a Ref to an account",
            {"Fn::FindInMap": ["accounts", {"Ref": "AWS::AccountId"}, "bar"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        (
                            "'bar' is not a second level key "
                            "when {'Ref': 'AWS::AccountId'} is "
                            "resolved for mapping 'accounts'"
                        ),
                        path=deque(["Fn::FindInMap", 2]),
                    ),
                )
            ],
        ),
        (
            "Invalid FindInMap with an top level key that is a Ref to pseudo param",
            {"Fn::FindInMap": ["foo", {"Ref": "AWS::AccountId"}, "second"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        (
                            "{'Ref': 'AWS::AccountId'} is not a "
                            "first level key for mapping 'foo'"
                        ),
                        path=deque(["Fn::FindInMap", 1]),
                    ),
                )
            ],
        ),
        (
            "Valid FindInMap with a second level key that is a Ref to pseudo param",
            {"Fn::FindInMap": ["foo", "first", {"Ref": "AWS::AccountId"}]},
            [],
        ),
        (
            "Valid FindInMap with a bad third key",
            {"Fn::FindInMap": ["foo", "first", "third"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        (
                            "'third' is not one of ['second'] for "
                            "mapping 'foo' and key 'first'"
                        ),
                        path=deque(["Fn::FindInMap", 2]),
                    ),
                )
            ],
        ),
        (
            "Valid FindInMap with integer types",
            {"Fn::FindInMap": ["integers", 1, 2]},
            [
                (
                    "Value",
                    Context(
                        path=Path(value_path=deque(["Mappings", "integers", "1", "2"]))
                    ),
                    None,
                )
            ],
        ),
        (
            (
                "Valid FindInMap with a Ref to a parameter "
                "with allowed values for top level key"
            ),
            {"Fn::FindInMap": ["environments", {"Ref": "Environment"}, "foo"]},
            [
                (
                    "one",
                    Context(
                        path=Path(
                            value_path=deque(["Mappings", "environments", "dev", "foo"])
                        ),
                        ref_values={"Environment": "dev"},
                    ),
                    None,
                ),
                (
                    "two",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "test", "foo"]
                            ),
                        ),
                        ref_values={"Environment": "test"},
                    ),
                    None,
                ),
            ],
        ),
        (
            "Valid FindInMap with a Ref to a parameter for top level key",
            {"Fn::FindInMap": ["environments", {"Ref": "RandomString"}, "foo"]},
            [],
        ),
        (
            (
                "Valid FindInMap with a Ref to accounts for top level "
                "key Ref to a ramom string for second level key"
            ),
            {
                "Fn::FindInMap": [
                    "accounts",
                    {"Ref": "AWS::AccountId"},
                    {"Ref": "RandomString"},
                ]
            },
            [],
        ),
        (
            (
                "Valid FindInMap with a Ref to accounts for top level "
                "key Ref to an allowed value parameter for second level key"
            ),
            {
                "Fn::FindInMap": [
                    "accounts",
                    {"Ref": "AWS::AccountId"},
                    {"Ref": "Environment"},
                ]
            },
            [],
        ),
        (
            (
                "Valid FindInMap with a Ref to a parameter "
                "with allowed values for second level key"
            ),
            {"Fn::FindInMap": ["environments", "lion", {"Ref": "Environment"}]},
            [
                (
                    "one",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "dev"]
                            )
                        ),
                        ref_values={"Environment": "dev"},
                    ),
                    None,
                ),
                (
                    "two",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "test"]
                            )
                        ),
                        ref_values={"Environment": "test"},
                    ),
                    None,
                ),
                (
                    "three",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "prod"]
                            )
                        ),
                        ref_values={"Environment": "prod"},
                    ),
                    None,
                ),
            ],
        ),
        (
            "Valid FindInMap with a Ref to a parameter for top level key",
            {"Fn::FindInMap": ["environments", {"Ref": "RandomString"}, "foo"]},
            [],
        ),
        (
            "Valid FindInMap with a Ref to a parameter and a Ref to pseudo parameter",
            {
                "Fn::FindInMap": [
                    "accounts",
                    {"Ref": "AWS::AccountId"},
                    {"Ref": "RandomString"},
                ]
            },
            [],
        ),
        (
            "Valid FindInMap with a bad second key and default",
            {"Fn::FindInMap": ["foo", "first", "third", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                )
            ],
        ),
        (
            "Valid FindInMap with a transform on first key",
            {"Fn::FindInMap": ["transformFirstKey", "first", "third"]},
            [],
        ),
        (
            "Valid FindInMap with a transform on second key",
            {"Fn::FindInMap": ["transformSecondKey", "first", "third"]},
            [],
        ),
        (
            "Valid FindInMap using a Sub",
            {
                "Fn::FindInMap": [
                    "environments",
                    "lion",
                    {"Fn::Sub": "${AWS::AccountId}Extra"},
                ]
            },
            [],
        ),
        (
            ("Valid FindInMap with a Sub with no parameters"),
            {"Fn::FindInMap": ["environments", "lion", {"Fn::Sub": "dev"}]},
            [
                (
                    "one",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "dev"]
                            )
                        )
                    ),
                    None,
                ),
            ],
        ),
        (
            ("Valid FindInMap with sub to a paremter"),
            {"Fn::FindInMap": ["environments", "lion", {"Fn::Sub": "${Environment}"}]},
            [
                (
                    "one",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "dev"]
                            )
                        ),
                        ref_values={"Environment": "dev"},
                    ),
                    None,
                ),
                (
                    "two",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "test"]
                            )
                        ),
                        ref_values={"Environment": "test"},
                    ),
                    None,
                ),
                (
                    "three",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "prod"]
                            )
                        ),
                        ref_values={"Environment": "prod"},
                    ),
                    None,
                ),
            ],
        ),
        (
            ("Valid FindInMap with sub list value to a paramter"),
            {
                "Fn::FindInMap": [
                    "environments",
                    "lion",
                    {"Fn::Sub": ["${Environment}", {}]},
                ]
            },
            [
                (
                    "one",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "dev"]
                            )
                        ),
                        ref_values={"Environment": "dev"},
                    ),
                    None,
                ),
                (
                    "two",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "test"]
                            )
                        ),
                        ref_values={"Environment": "test"},
                    ),
                    None,
                ),
                (
                    "three",
                    Context(
                        path=Path(
                            value_path=deque(
                                ["Mappings", "environments", "lion", "prod"]
                            )
                        ),
                        ref_values={"Environment": "prod"},
                    ),
                    None,
                ),
            ],
        ),
        (
            ("Valid FindInMap with an invalid sub"),
            {
                "Fn::FindInMap": [
                    "environments",
                    "lion",
                    {"Fn::Sub": {"A": "B", "C": "D"}},
                ]
            },
            [],
        ),
        (
            "Valid Sub with a resolvable values",
            {"Fn::Sub": ["${a}-${b}", {"a": "foo", "b": "bar"}]},
            [("foo-bar", Context(), None)],
        ),
        (
            "Valid Sub with empty parameters",
            {"Fn::Sub": ["foo", {}]},
            [("foo", Context(), None)],
        ),
        (
            "Valid Sub with a getatt and list",
            {"Fn::Sub": ["${MyResource.Arn}", {}]},
            [],
        ),
        (
            "Valid Sub with a getatt string",
            {"Fn::Sub": "${MyResource.Arn}"},
            [],
        ),
        (
            "Fn::Join uses previous values when doing resolution",
            {"Fn::Join": ["-", [{"Ref": "Environment"}, {"Ref": "Environment"}]]},
            [
                ("dev-dev", Context(ref_values={"Environment": "dev"}), None),
                ("test-test", Context(ref_values={"Environment": "test"}), None),
                ("prod-prod", Context(ref_values={"Environment": "prod"}), None),
            ],
        ),
        (
            "Fn::Join using a few values with a bad Ref",
            {"Fn::Join": ["-", [{"Ref": "Environment"}, {"Ref": "DNE"}]]},
            [],
        ),
    ],
)
def test_valid_functions(name, instance, response):
    context = Context(
        parameters={
            "RandomString": Parameter(
                {
                    "Type": "String",
                }
            ),
            "Environment": Parameter(
                {
                    "Type": "String",
                    "AllowedValues": ["dev", "test", "prod"],
                }
            ),
        },
        mappings=Mappings.create_from_dict(
            {
                "foo": {"first": {"second": "bar"}},
                "transformFirstKey": {"Fn::Transform": {"second": "bar"}},
                "transformSecondKey": {"first": {"Fn::Transform": "bar"}},
                "integers": {"1": {"2": "Value"}},
                "accounts": {
                    "123456789012": {"dev": "bar"},
                    "us-east-1": {"bar": "foo"},
                },
                "environments": {
                    "dev": {"foo": "one"},
                    "test": {"foo": "two"},
                    "prod": {"bar": "three"},
                    "lion": {
                        "dev": "one",
                        "test": "two",
                        "prod": "three",
                    },
                },
            }
        ),
        resources={
            "MyResource": Resource(
                {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": "XXX",
                    },
                }
            ),
        },
    )
    _resolve(name, instance, response, context=context)


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Invalid FindInMap with no mappings",
            {"Fn::FindInMap": [{"Ref": "MyParameter"}, "B", "C"]},
            [
                (
                    None,
                    Context(),
                    ValidationError(
                        ("{'Ref': 'MyParameter'} is not one of []"),
                        path=deque(["Fn::FindInMap", 0]),
                    ),
                )
            ],
        ),
        (
            "Invalid FindInMap with no mappings and default value",
            {"Fn::FindInMap": ["A", "B", "C", {"DefaultValue": "default"}]},
            [
                (
                    "default",
                    Context(path=Path(value_path=deque([4, "DefaultValue"]))),
                    None,
                )
            ],
        ),
    ],
)
def test_no_mapping(name, instance, response):
    _resolve(name, instance, response)


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Valid FindInMap using transform key (maybe) with fn",
            {"Fn::FindInMap": [{"Ref": "AWS::Region"}, "B", "C"]},
            [],
        ),
        (
            "Valid FindInMap using transform key (maybe)",
            {"Fn::FindInMap": ["A", "B", "C"]},
            [],
        ),
    ],
)
def test_find_in_map_with_transform(name, instance, response):
    context = Context(
        mappings=Mappings.create_from_dict(
            {
                "foo": {"first": {"second": "bar"}},
                "Fn::Transform": "foobar",
            }
        ),
        resources={},
    )
    _resolve(name, instance, response, context=context)


def test_if():
    cfn = Template(
        None,
        {
            "Conditions": {
                "Condition": {"Fn::Equals": [{"Ref": "AWS::StackName"}, "test"]}
            },
            "Resources": {},
        },
    )
    context = create_context_for_template(cfn)
    validator = CfnTemplateValidator().evolve(
        context=context,
        cfn=cfn,
    )

    instance = {"Fn::If": ["Condition", "Foo", "Bar"]}

    results = list(validator.resolve_value(instance))

    assert len(results) == 2
    assert results[0][0] == "Foo"
    assert results[1][0] == "Bar"

    assert results[0][1].context.conditions.status == {"Condition": True}
    assert results[1][1].context.conditions.status == {"Condition": False}

    validator = validator.evolve(
        context=validator.context.evolve(
            conditions=validator.context.conditions.evolve({"Condition": False})
        )
    )

    results = list(validator.resolve_value(instance))
    assert len(results) == 1
    assert results[0][0] == "Bar"
