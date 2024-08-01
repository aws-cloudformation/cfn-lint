"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.InstanceImageId import InstanceImageId


@pytest.fixture(scope="module")
def rule():
    rule = InstanceImageId()
    yield rule


@pytest.mark.parametrize(
    "name,template,instance,path,expected",
    [
        (
            "Valid with no ImageId in LaunchTemplate",
            {
                "Resources": {
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateName": "a-template",
                            "LaunchTemplateData": {
                                "Monitoring": {"Enabled": True},
                            },
                        },
                    },
                }
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateId": {
                        "Fn::GetAtt": [
                            "LaunchTemplate",
                            "LaunchTemplateId",
                        ],
                    }
                },
                "ImageId": "ami-12345678",
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with no ImageId and a string launch template",
            {
                "Resources": {},
            },
            {
                "LaunchTemplate": {"LaunchTemplateId": "foo"},
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with no ImageId and a parameter",
            {
                "Parameters": {
                    "LaunchTemplateId": {
                        "Type": "String",
                    }
                },
                "Resources": {},
            },
            {
                "LaunchTemplate": {"LaunchTemplateId": {"Ref": "LaunchTemplateId"}},
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with no ImageId a random ref",
            {
                "Resources": {},
            },
            {
                "LaunchTemplate": {"LaunchTemplateName": {"Ref": "AWS::StackName"}},
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with no ImageId and another function",
            {
                "Parameters": {
                    "LaunchTemplateId": {
                        "Type": "String",
                    }
                },
                "Resources": {},
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateId": {"Fn::FindInMap": ["One", "Two", "Three"]}
                },
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with ImageId in LaunchTemplate",
            {
                "Resources": {
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateName": "a-template",
                            "LaunchTemplateData": {
                                "Monitoring": {"Enabled": True},
                                "ImageId": "ami-12345678",
                            },
                        },
                    },
                }
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateId": {
                        "Fn::GetAtt": [
                            "LaunchTemplate",
                            "LaunchTemplateId",
                        ],
                    }
                },
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with ImageId in LaunchTemplate using Name",
            {
                "Resources": {
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateName": "a-template",
                            "LaunchTemplateData": {
                                "Monitoring": {"Enabled": True},
                                "ImageId": "ami-12345678",
                            },
                        },
                    },
                }
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateName": {
                        "Ref": "LaunchTemplate",
                    }
                },
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Invalid with no relationship",
            {},
            {},
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'ImageId' is a required property",
                    validator="required",
                    rule=InstanceImageId(),
                    path=deque([]),
                )
            ],
        ),
        (
            "Invalid with no ImageId in LaunchTemplate",
            {
                "Resources": {
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateName": "a-template",
                            "LaunchTemplateData": {
                                "Monitoring": {"Enabled": True},
                            },
                        },
                    },
                }
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateId": {
                        "Fn::GetAtt": [
                            "LaunchTemplate",
                            "LaunchTemplateId",
                        ],
                    }
                },
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'ImageId' is a required property",
                    validator="required",
                    rule=InstanceImageId(),
                    path=deque([]),
                )
            ],
        ),
        (
            "Invalid with no ImageId in LaunchTemplate with condition",
            {
                "Conditions": {
                    "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
                },
                "Resources": {
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateName": "a-template",
                            "LaunchTemplateData": {
                                "Monitoring": {"Enabled": True},
                            },
                        },
                    },
                },
            },
            {
                "LaunchTemplate": {
                    "LaunchTemplateId": {
                        "Fn::GetAtt": [
                            "LaunchTemplate",
                            "LaunchTemplateId",
                        ],
                    }
                },
                "ImageId": {
                    "Fn::If": [
                        "IsUsEast1",
                        "ami-12345678",
                        {"Ref": "AWS::NoValue"},
                    ]
                },
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'ImageId' is a required property",
                    validator="required",
                    rule=InstanceImageId(),
                    path=deque(["ImageId", "Fn::If", 2, "Ref"]),
                )
            ],
        ),
    ],
    indirect=["template", "path"],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert (
        errs == expected
    ), f"Expected test {name!r} to have {expected!r} but got {errs!r}"
