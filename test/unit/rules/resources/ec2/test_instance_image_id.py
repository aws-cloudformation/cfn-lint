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
                    "Instance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
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
                    },
                }
            },
            {
                "ImageId": "ami-12345678",
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
                    "Instance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "LaunchTemplate": {
                                "LaunchTemplateId": {
                                    "Fn::GetAtt": [
                                        "LaunchTemplate",
                                        "LaunchTemplateId",
                                    ],
                                }
                            },
                        },
                    },
                }
            },
            {},
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Invalid with no relationship",
            {
                "Resources": {
                    "Instance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {},
                    },
                }
            },
            {},
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [ValidationError("'ImageId' is a required property")],
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
                    "Instance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "LaunchTemplate": {
                                "LaunchTemplateId": {
                                    "Fn::GetAtt": [
                                        "LaunchTemplate",
                                        "LaunchTemplateId",
                                    ],
                                }
                            },
                        },
                    },
                }
            },
            {},
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'ImageId' is a required property",
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
                    "Instance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
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
                    },
                },
            },
            {
                "ImageId": {
                    "Fn::If": ["IsUsEast1", "ami-12345678", {"Ref": "AWS::NoValue"}]
                }
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'ImageId' is a required property",
                    path_override=deque(
                        [
                            "Resources",
                            "Instance",
                            "Properties",
                            "ImageId",
                            "Fn::If",
                            2,
                            "Ref",
                        ]
                    ),
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
