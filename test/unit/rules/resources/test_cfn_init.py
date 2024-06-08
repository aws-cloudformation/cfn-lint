"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.CfnInit import CfnInit


@pytest.fixture(scope="module")
def rule():
    rule = CfnInit()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {
            "MyString": {
                "Type": "String",
            }
        }
    }


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Metadata",
            {
                "config": {
                    "packages": {"yum": {"httpd": []}},
                    "files": {
                        "/var/www/html/index.html": {
                            "content": (
                                "<body>\n  <h1>Congratulations, you have "
                                "successfully launched the AWS "
                                "CloudFormation sample.</h1>\n</body>\n"
                            ),
                            "mode": "000644",
                            "owner": "root",
                            "group": "root",
                        },
                        "/etc/cfn/cfn-hup.conf": {
                            "content": {
                                "Fn::Sub": (
                                    "[main]\nstack="
                                    "${AWS::StackId}\n"
                                    "region=${AWS::Region}\n"
                                )
                            },
                            "mode": "000400",
                            "owner": "root",
                            "group": "root",
                        },
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf": {
                            "content": {
                                "Fn::Sub": (
                                    "[cfn-auto-reloader-hook]\ntriggers="
                                    "post.update\npath=Resources."
                                    "LaunchConfig.Metadata.AWS::CloudFormation::Init"
                                    "\naction=/opt/aws/bin/cfn-init "
                                    "-v --stack ${AWS::StackName}"
                                    " --resource Instance --region "
                                    "${AWS::Region}\nrunas=root"
                                )
                            }
                        },
                    },
                    "services": {
                        "sysvinit": {
                            "httpd": {"enabled": True, "ensureRunning": True},
                            "cfn-hup": {
                                "enabled": True,
                                "ensureRunning": True,
                                "files": [
                                    "/etc/cfn/cfn-hup.conf",
                                    "/etc/cfn/hooks.d/cfn-auto-reloader.conf",
                                ],
                            },
                        }
                    },
                },
            },
            [],
        ),
        (
            "Bad type",
            [],
            [
                ValidationError(
                    ("[] is not of type 'object'"),
                    path=deque([]),
                    schema_path=deque(["type"]),
                    validator="type",
                    rule=CfnInit(),
                    path_override=deque([]),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
