"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule


class ValueRefGetAtt(CloudFormationLintRule):
    """Check if Resource Properties are correct"""

    id = "E3008"
    shortdesc = "Check values of properties for valid Refs and GetAtts"
    description = "Checks resource properties for Ref and GetAtt values"
    tags = ["resources", "ref", "getatt"]

    def __init__(self):
        super().__init__()
        self.cfn = None

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    # pylint: disable=unused-argument
    def awsType(self, validator, uI, instance, schema):
        pass
