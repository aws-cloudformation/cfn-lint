"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import namedtuple

import pytest

from cfnlint import Template
from cfnlint.context.context import create_context_for_template

_Counts = namedtuple("_Counts", ["resources", "parameters", "conditions", "mappings"])


@pytest.mark.parametrize(
    "name,instance,counts",
    [
        (
            "Valid template",
            {
                "Parameters": {
                    "Env": {
                        "Type": "String",
                    }
                },
                "Conditions": {
                    "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
                },
                "Mappings": {"Map": {"us-east-1": {"foo": "bar"}}},
                "Resources": {
                    "Bucket": {
                        "Type": "AWS::S3::Bucket",
                    },
                },
            },
            _Counts(resources=1, parameters=1, conditions=1, mappings=1),
        ),
        (
            "Bad types in template",
            {
                "Parameters": [],
                "Conditions": [],
                "Mappings": [],
                "Resources": [],
            },
            _Counts(resources=0, parameters=0, conditions=0, mappings=0),
        ),
        (
            "Invalid type configurations",
            {
                "Parameters": {
                    "BusinessUnit": [],
                    "Env": {
                        "Type": "String",
                    },
                },
                "Mappings": {"AnotherMap": [], "Map": {"us-east-1": {"foo": "bar"}}},
                "Resources": {
                    "Instance": [],
                    "Bucket": {
                        "Type": "AWS::S3::Bucket",
                    },
                },
            },
            _Counts(resources=1, parameters=1, conditions=0, mappings=2),
        ),
        (
            "Invalid mapping second key",
            {
                "Mappings": {
                    "BadKey": {
                        "Foo": [],
                    },
                    "Map": {"us-east-1": {"foo": "bar"}},
                },
            },
            _Counts(resources=0, parameters=0, conditions=0, mappings=2),
        ),
        (
            "Invalid mapping third key",
            {
                "Mappings": {
                    "BadKey": {
                        "Foo": {
                            "Bar": {},
                        },
                    },
                    "Map": {"us-east-1": {"foo": "bar"}},
                },
            },
            _Counts(resources=0, parameters=0, conditions=0, mappings=2),
        ),
    ],
)
def test_create_context(name, instance, counts):
    cfn = Template("", instance, ["us-east-1"])
    context = create_context_for_template(cfn)

    for i in counts._fields:
        if i == "conditions":
            assert len(context.conditions.conditions) == getattr(counts, i), (
                f"Test {name} has {i} {len(getattr(context, i))} "
                f"and expected {getattr(counts, i)}"
            )
        elif i == "mappings":
            assert len(context.mappings.maps) == getattr(counts, i), (
                f"Test {name} has {i} {len(context.mappings.maps)} "
                f"and expected {getattr(counts, i)}"
            )
        else:
            assert len(getattr(context, i)) == getattr(counts, i), (
                f"Test {name} has {i} {len(getattr(context, i))} "
                f"and expected {getattr(counts, i)}"
            )
