"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import cfnlint.decode.cfn_json  # pylint: disable=E0401
import cfnlint.decode.cfn_yaml  # pylint: disable=E0401
from cfnlint.core import DEFAULT_RULESDIR  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.runner import Runner


class TestRunner(BaseTestCase):
    """Test Duplicates Parsing"""

    def setUp(self):
        """SetUp template object"""
        self.collection = RulesCollection(
            include_rules=["I"], include_experimental=True
        )
        rulesdirs = [DEFAULT_RULESDIR]
        for rulesdir in rulesdirs:
            self.collection.create_from_directory(rulesdir)
        (self.template, _) = cfnlint.decode.decode_str(
            """
            AWSTemplateFormatVersion: "2010-09-09"
            Description: >
                Template with all error levels: Warning, Error and Informational
            Resources:
                myTable:
                    Metadata:
                        cfn-lint:
                            config:
                                ignore_checks:
                                - I3011
                                - W1020
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
        """
        )

    def test_runner(self):
        """Success test"""
        runner = Runner(self.collection, "", self.template, ["us-east-1"], [])
        runner.transform()
        failures = runner.run()
        assert [] == failures, "Got failures {}".format(failures)

    def test_runner_mandatory_rules(self):
        """Success test"""
        runner = Runner(
            self.collection, "", self.template, ["us-east-1"], mandatory_rules=["W1020"]
        )
        runner.transform()
        failures = runner.run()
        self.assertEqual(len(failures), 1)

        runner = Runner(
            self.collection, "", self.template, ["us-east-1"], mandatory_rules=["W9000"]
        )
        runner.transform()
        failures = runner.run()
        self.assertEqual(len(failures), 0)
