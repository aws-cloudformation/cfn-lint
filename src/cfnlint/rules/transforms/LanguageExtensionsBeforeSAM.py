"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class LanguageExtensionsBeforeSAM(CloudFormationLintRule):
    """Check if Serverless Resources exist without the Serverless Transform"""

    id = "W0510"
    shortdesc = "Put LanguageExtensions before SAM transform"
    description = (
        "If using language extensions with SAM, you should add AWS::LanguageExtensions "
        "before the serverless transform (that is, before AWS::Serverless-2016-10-31)"
    )
    source_url = "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy.html"
    tags = ["transforms"]

    def match(self, cfn):
        matches = []

        if isinstance(cfn.transform_pre["Transform"], list):
            flag = False
            for i, transform in enumerate(cfn.transform_pre["Transform"]):
                if transform == "AWS::Serverless-2016-10-31":
                    flag = True
                if transform == "AWS::LanguageExtensions" and flag:
                    matches.append(
                        RuleMatch(
                            ["Transform", i],
                            (
                                "Place 'AWS::LanguageExtensions' before "
                                "'AWS::Serverless-2016-10-31'"
                            ),
                        )
                    )
        return matches
