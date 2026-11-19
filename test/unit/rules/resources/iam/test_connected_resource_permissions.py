"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.decode.decode import decode_str
from cfnlint.rules.resources.iam.ConnectedResourcePermissions import (
    _UNKNOWN,
    ConnectedResourcePermissions,
)
from cfnlint.template import Template

# ruff: noqa: E501


class TestConnectedResourcePermissions(BaseRuleTestCase):
    """Test resource policies for connected resources"""

    def setUp(self):
        """Setup"""
        super().setUp()
        self.collection.register(ConnectedResourcePermissions())
        self.success_templates = [
            "test/fixtures/templates/good/resources/iam/connected_resource_permissions/template.yaml",
            "test/fixtures/templates/good/resources/iam/connected_resource_permissions/sam.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/connected_resource_permissions/template.yaml",
            6,
        )

    def test_file_negative_sam(self):
        """Test failure with SAM"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/connected_resource_permissions/sam.yaml",
            2,
        )


@pytest.mark.parametrize(
    "name,value,expected",
    [
        ("String", "arn:aws:lambda:us-east-1:123456789012:function:f", []),
        ("Ref", {"Ref": "Function"}, ["Function"]),
        ("Ref pseudo parameter", {"Ref": "AWS::Region"}, [_UNKNOWN]),
        ("GetAtt list", {"Fn::GetAtt": ["Function", "Arn"]}, ["Function"]),
        ("GetAtt string", {"Fn::GetAtt": "Function.Arn"}, ["Function"]),
        ("GetAtt bad", {"Fn::GetAtt": {}}, [_UNKNOWN]),
        (
            "Sub",
            {"Fn::Sub": "arn:${AWS::Partition}:x:${Function.Arn}/${!Literal}"},
            ["Function"],
        ),
        (
            "Sub with variables",
            {"Fn::Sub": ["${Arn}/invocations", {"Arn": {"Fn::GetAtt": "Alias.Arn"}}]},
            ["Alias"],
        ),
        ("Sub bad", {"Fn::Sub": {}}, [_UNKNOWN]),
        (
            "Join",
            {"Fn::Join": ["", ["arn:", {"Ref": "Function"}, "/invocations"]]},
            ["Function"],
        ),
        ("Join bad", {"Fn::Join": "bad"}, [_UNKNOWN]),
        (
            "If",
            {"Fn::If": ["Cond", {"Ref": "A"}, {"Ref": "B"}]},
            ["A", "B"],
        ),
        ("If bad", {"Fn::If": []}, [_UNKNOWN]),
        ("ImportValue", {"Fn::ImportValue": "Export"}, [_UNKNOWN]),
        ("Not a function", {"A": "B", "C": "D"}, [_UNKNOWN]),
        ("List", [], [_UNKNOWN]),
    ],
)
def test_targets(name, value, expected):
    assert list(ConnectedResourcePermissions()._targets(value)) == expected, (
        f"Test {name!r} got unexpected targets"
    )


@pytest.mark.parametrize(
    "name,document,expected",
    [
        ("Not an object", [], {_UNKNOWN}),
        ("No statements", {}, {_UNKNOWN}),
        ("Statement is a function", {"Statement": {"Fn::If": []}}, {_UNKNOWN}),
        (
            "Statement object",
            {
                "Statement": {
                    "Effect": "Allow",
                    "Principal": {"Service": "s3.amazonaws.com"},
                }
            },
            {"s3.amazonaws.com"},
        ),
        (
            "Deny is ignored",
            {
                "Statement": [
                    {"Effect": "Deny", "Principal": {"Service": "s3.amazonaws.com"}}
                ]
            },
            set(),
        ),
        (
            "Everyone",
            {
                "Statement": [
                    {"Effect": "Allow", "Principal": "*"},
                    {"Effect": "Allow", "Principal": {"AWS": "*"}},
                ]
            },
            {"*"},
        ),
        (
            "Account principals don't grant a service",
            {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
                    }
                ]
            },
            set(),
        ),
        (
            "Unresolved",
            {
                "Statement": [
                    "bad",
                    {"Effect": "Allow", "Principal": {"Ref": "Principal"}},
                    {"Effect": "Allow", "Principal": {"Service": [{"Ref": "S"}]}},
                ]
            },
            {_UNKNOWN},
        ),
    ],
)
def test_service_principals(name, document, expected):
    assert ConnectedResourcePermissions()._service_principals(document) == expected, (
        f"Test {name!r} got unexpected principals"
    )


def _match(template: str):
    tpl, _ = decode_str(template)
    return ConnectedResourcePermissions().match(Template("", tpl, ["us-east-1"]))


def test_unresolved_permission_allows_everything():
    """A permission without readable properties could grant anything"""
    assert (
        _match(
            """
Resources:
  Function:
    Type: AWS::Lambda::Function
  Permission:
    Type: AWS::Lambda::Permission
    Properties: !If [Cond, {}, {}]
  Rule:
    Type: AWS::Events::Rule
    Properties:
      Targets:
        - Id: function
          Arn: !GetAtt Function.Arn
"""
        )
        == []
    )


def test_unresolved_queue_policy_allows_everything():
    assert (
        _match(
            """
Resources:
  Queue:
    Type: AWS::SQS::Queue
  QueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues: !Ref Queues
      PolicyDocument: {}
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      NotificationConfiguration:
        QueueConfigurations:
          - Event: s3:ObjectCreated:*
            Queue: !GetAtt Queue.Arn
"""
        )
        == []
    )


def test_sam_event_without_type_allows_everything():
    assert (
        _match(
            """
Resources:
  Function:
    Type: AWS::Serverless::Function
    Properties:
      Events:
        Event:
          Type: !Ref EventType
  Rule:
    Type: AWS::Events::Rule
    Properties:
      Targets:
        - Id: function
          Arn: !GetAtt Function.Arn
"""
        )
        == []
    )


def test_bad_shapes_are_ignored():
    """Malformed properties are reported by other rules"""
    assert (
        _match(
            """
Resources:
  Function:
    Type: AWS::Lambda::Function
  Method:
    Type: AWS::ApiGateway::Method
    Properties:
      Integration: []
  Integration:
    Type: AWS::ApiGatewayV2::Integration
    Properties: []
  HttpApi:
    Type: AWS::ApiGatewayV2::Api
    Properties: []
  RestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Body:
        paths:
          - x-amazon-apigateway-integration: []
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      NotificationConfiguration:
        LambdaConfigurations:
          - bad
        QueueConfigurations: {}
  OtherBucket:
    Type: AWS::S3::Bucket
    Properties:
      NotificationConfiguration: []
  Rule:
    Type: AWS::Events::Rule
    Properties:
      Targets:
        - bad
  OtherRule:
    Type: AWS::Events::Rule
    Properties:
      Targets: {}
"""
        )
        == []
    )


def test_openapi_integrations():
    matches = _match(
        """
Resources:
  Function:
    Type: AWS::Lambda::Function
  RestApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Body:
        paths:
          /http:
            get:
              x-amazon-apigateway-integration:
                type: http_proxy
                uri: !Sub https://${Function}.example.com
          /role:
            get:
              x-amazon-apigateway-integration:
                type: aws_proxy
                credentials: arn:aws:iam::123456789012:role/api
                uri: !Sub arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${Function.Arn}/invocations
          /missing:
            post:
              x-amazon-apigateway-integration:
                type: AWS
                uri: !Sub arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/${Function.Arn}/invocations
"""
    )
    assert [match.path for match in matches] == [
        [
            "Resources",
            "RestApi",
            "Properties",
            "Body",
            "paths",
            "/missing",
            "post",
            "x-amazon-apigateway-integration",
            "uri",
        ]
    ]


def test_qualified_permission_on_function_covers_alias():
    """FunctionName: !Sub ${Function}:live grants the alias"""
    assert (
        _match(
            """
Resources:
  Function:
    Type: AWS::Lambda::Function
  Alias:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref Function
      Name: live
  Permission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Sub ${Function}:live
      Principal: events.amazonaws.com
  Rule:
    Type: AWS::Events::Rule
    Properties:
      Targets:
        - Id: alias
          Arn: !Ref Alias
"""
        )
        == []
    )
