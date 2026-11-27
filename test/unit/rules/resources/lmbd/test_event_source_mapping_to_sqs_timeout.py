"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import jsonpatch
import pytest

from cfnlint.context import create_context_for_template
from cfnlint.decode.cfn_yaml import load
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.EventSourceMappingToSqsTimeout import (
    EventSourceMappingToSqsTimeout,
)
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = EventSourceMappingToSqsTimeout()
    yield rule


_template = {
    "Resources": {
        "Queue": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "VisibilityTimeout": 300,
            },
        },
        "Lambda": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Timeout": 100,
                "Role": {"Fn::GetAtt": "Role.Arn"},
            },
        },
        "Mapping": {
            "Type": "AWS::Lambda::EventSourceMapping",
            "Properties": {
                "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                "FunctionName": {"Ref": "Lambda"},
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        (
            _template,
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Lambda/Properties/Timeout",
                        "value": 600,
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (300) is less "
                    "than Function timeout (600) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Lambda/Properties/Timeout",
                        "value": "600",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Queue/Properties/VisibilityTimeout",
                        "value": {"Ref": "AWS::Region"},
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Mapping/Properties/EventSourceArn",
                        "value": {"Fn::GetAtt": "Lambda.Arn"},
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Lambda/Properties/Timeout",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Queue/Properties/VisibilityTimeout",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (30) is less "
                    "than Function timeout (100) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        [
                            "Resources",
                            "Queue",
                            "Properties",
                            "VisibilityTimeout",
                        ]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        # Hardcoded EventSourceArn — no error
        (
            {
                "Resources": {
                    "Function": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Runtime": "python3.12",
                            "Handler": "index.handler",
                            "Code": {"ZipFile": "def handler(e, c): pass"},
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Timeout": 900,
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": (
                                "arn:aws:sqs:us-east-1:123456789012:my-queue"
                            ),
                            "FunctionName": {"Ref": "Function"},
                            "BatchSize": 10,
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Fn::If on VisibilityTimeout: violation only in the second branch (#4850)
        (
            {
                "Conditions": {
                    "UseLong": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": {"Fn::If": ["UseLong", 1800, 30]},
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": 300,
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (30) is less "
                    "than Function timeout (300) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        # Fn::If on VisibilityTimeout: both branches violate (#4850)
        (
            {
                "Conditions": {
                    "UseLong": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": {"Fn::If": ["UseLong", 200, 30]},
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": 300,
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (200) is less "
                    "than Function timeout (300) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
                ValidationError(
                    "Queue visibility timeout (30) is less "
                    "than Function timeout (300) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        # Fn::If on the referenced Function Timeout: violation only in one branch
        (
            {
                "Conditions": {
                    "UseLong": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": 300,
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": {"Fn::If": ["UseLong", 600, 3]},
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (300) is less "
                    "than Function timeout (600) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        # Same condition gates both sides: only (300, 1800) and (10, 30)
        # can occur, both fine, so no finding even though cross pairs
        # like (300, 30) would violate
        (
            {
                "Conditions": {
                    "UseLong": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": {"Fn::If": ["UseLong", 1800, 30]},
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": {"Fn::If": ["UseLong", 300, 10]},
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Unresolvable value: VisibilityTimeout is a Ref to a parameter,
        # so no comparison can be made and the rule stays silent (#4850)
        (
            {
                "Parameters": {
                    "VisibilityTimeout": {"Type": "Number"},
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": {"Ref": "VisibilityTimeout"},
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": 300,
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Duplicate branch values under different condition statuses:
        # both VisibilityTimeout branches are 30, and the reachable
        # UseLong=false pair is Timeout 300 / VisibilityTimeout 30.
        # Deduping gathered values by value alone kept only the
        # UseLong=true candidate and skipped that pair (#4869)
        (
            {
                "Conditions": {
                    "UseLong": {
                        "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"],
                    },
                },
                "Resources": {
                    "Queue": {
                        "Type": "AWS::SQS::Queue",
                        "Properties": {
                            "VisibilityTimeout": {"Fn::If": ["UseLong", 30, 30]},
                        },
                    },
                    "Lambda": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Timeout": {"Fn::If": ["UseLong", 10, 300]},
                            "Role": {"Fn::GetAtt": "Role.Arn"},
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                            "FunctionName": {"Ref": "Lambda"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (30) is less "
                    "than Function timeout (300) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"


def test_fnif_second_branch_low_fixture(rule):
    """Fixture template from #4850: Fn::If on a gathered property"""
    template = load(
        "test/fixtures/templates/bad/resources/lambda/fnif-second-branch-low.yaml"
    )
    cfn = Template("", template, regions=["us-east-1"])
    context = create_context_for_template(cfn)
    validator = CfnTemplateValidator(context=context, cfn=cfn)

    errs = []
    for instance, instance_validator in get_value_from_path(
        validator, template, deque(["Resources", "Mapping", "Properties"])
    ):
        errs.extend(rule.validate(instance_validator, "", instance, {}))

    assert [e.message for e in errs] == [
        "Queue visibility timeout (30) is less than Function timeout (300) seconds"
    ]
