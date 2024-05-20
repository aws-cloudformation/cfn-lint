"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context, Path
from cfnlint.context.context import Parameter, Resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.DeletionPolicy import DeletionPolicy


@pytest.mark.parametrize(
    "name, instance, path, expected",
    [
        ("Correct type", "Snapshot", deque(["Resources", "MyVolume"]), []),
        (
            "Incorrect type",
            {"Foo": "Bar"},
            deque(["Resources", "MyVolume"]),
            [
                ValidationError(
                    "{'Foo': 'Bar'} is not of type 'string'",
                    schema_path=deque(["type"]),
                    validator="type",
                    rule=DeletionPolicy(),
                ),
                ValidationError(
                    (
                        "{'Foo': 'Bar'} is not one of ['Delete', 'Retain', "
                        "'RetainExceptOnCreate', 'Snapshot']"
                    ),
                    schema_path=deque(["enum"]),
                    validator="enum",
                    rule=DeletionPolicy(),
                ),
            ],
        ),
        (
            "Snapshot not supported",
            "Snapshot",
            deque(["Resources", "MyInstance"]),
            [
                ValidationError(
                    (
                        "'Snapshot' is not one of ['Delete', 'Retain', "
                        "'RetainExceptOnCreate']"
                    ),
                    schema_path=deque(["enum"]),
                    validator="enum",
                    rule=DeletionPolicy(),
                ),
            ],
        ),
        (
            "Success on a valid function",
            {"Ref": "MyParameter"},
            deque(["Resources", "MyInstance"]),
            [],
        ),
    ],
)
def test_deletion_policy(name, instance, path, expected):
    context = Context(
        regions=["us-east-1"],
        path=Path(path=path),
        resources={
            "MyVolume": Resource({"Type": "AWS::EC2::Volume"}),
            "MyInstance": Resource({"Type": "AWS::EC2::Instance"}),
        },
        parameters={"MyParameter": Parameter({"Type": "String"})},
    )
    validator = CfnTemplateValidator(context=context)

    rule = DeletionPolicy()
    errors = list(
        rule.validate(
            validator=validator,
            dP="deletionpolicy",
            instance=instance,
            schema={},
        )
    )

    assert errors == expected
