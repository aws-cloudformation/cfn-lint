"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_json  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint import ConfigMixIn
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules
from cfnlint.runner import TemplateRunner


class TestRunner(BaseTestCase):
    """Test Duplicates Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.rules = Rules.create_from_directory(_DEFAULT_RULESDIR)
        (self.template, _) = cfnlint.decode.decode_str(
            """
            AWSTemplateFormatVersion: "2010-09-09"
            Description: >
                Template with all error levels: Warning, Error and Informational
            # Adding in an issue outside of the Resources for validating
            Conditions:
                IsUsEast1: !Equals ["a", "b", "c"]
            Resources:
                myTable:
                    Metadata:
                        cfn-lint:
                            config:
                                ignore_checks:
                                - I3011
                                - W1020
                                - E8003 # condition error #
                    Type: "AWS::DynamoDB::Table"
                    Properties:
                        TableName: !Sub "TableName"
                        AttributeDefinitions:
                            - AttributeName: "Id"
                              AttributeType: "S" # Valid AllowedValue
                        KeySchema:
                            - AttributeName: "Id"
                              KeyType: "HASH"
                        ProvisionedThroughput:
                            ReadCapacityUnits: 5
                            WriteCapacityUnits: "5"
                myTable2:
                    # With no ignore_checks so we
                    # should still get issues from this
                    Type: "AWS::DynamoDB::Table"
                    Properties:
                        TableName: !Sub "TableName1"
                        AttributeDefinitions:
                            - AttributeName: "Id"
                              AttributeType: "S" # Valid AllowedValue
                        KeySchema:
                            - AttributeName: "Id"
                              KeyType: "HASH"
                        ProvisionedThroughput:
                            ReadCapacityUnits: !If [IsUsEast1, 5, 5]
                            WriteCapacityUnits: "5"
        """
        )

    def test_runner(self):
        """Success test"""
        runner = TemplateRunner(
            filename=None,
            template=self.template,
            config=ConfigMixIn(
                regions=["us-east-1"],
                include_checks=["I"],
                include_experimental=True,
            ),
            rules=self.rules,
        )
        failures = list(runner.run())
        self.assertEqual(len(failures), 4, "Got failures {}".format(failures))

    def test_runner_mandatory_rules(self):
        """Success test"""
        runner = TemplateRunner(
            filename=None,
            template=self.template,
            config=ConfigMixIn(
                mandatory_checks=["W1020"],
                regions=["us-east-1"],
                include_checks=["I"],
                include_experimental=True,
            ),
            rules=self.rules,
        )
        failures = list(runner.run())
        self.assertEqual(len(failures), 5, "Got failures {}".format(failures))

        runner = TemplateRunner(
            filename=None,
            template=self.template,
            config=ConfigMixIn(
                mandatory_checks=["W9000"],
                regions=["us-east-1"],
                include_checks=["I"],
                include_experimental=True,
            ),
            rules=self.rules,
        )
        failures = list(runner.run())
        self.assertEqual(len(failures), 4, "Got failures {}".format(failures))
