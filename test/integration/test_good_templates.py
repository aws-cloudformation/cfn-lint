"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import warnings
from test.integration import BaseCliTestCase
import cfnlint.core


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing """

    scenarios = [
        {
            'filename': 'test/fixtures/templates/good/generic.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/minimal.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "ExampleLayer29b0582575"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect Resources/ExampleLayer29b0582575 from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                },
                {
                    "Filename": "test/fixtures/templates/good/transform.yaml",
                    "Level": "Informational",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 18
                        },
                        "Path": [
                            "Resources",
                            "AppName"
                        ],
                        "Start": {
                            "ColumnNumber": 3,
                            "LineNumber": 18
                        }
                    },
                    "Message": "The default action when replacing/removing a resource is to delete it. Set explicit values for UpdateReplacePolicy / DeletionPolicy on potentially stateful resource: Resources/AppName",
                    "Rule": {
                        "Description": "The default action when replacing/removing a resource is to delete it. This check requires you to explicitly set policies",
                        "Id": "I3011",
                        "ShortDescription": "Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 12,
        },
        {
            'filename': 'test/fixtures/templates/bad/transform_serverless_template.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        },
                        "Path": None,
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        }
                    },
                    "Message": "Error transforming template: Resource with id [AppName] is invalid. Resource is missing the required [Location] property.",
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint"
                    }
                },
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        },
                        "Path": None,
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        }
                    },
                    "Message": "Error transforming template: Resource with id [ExampleLayer] is invalid. Missing required property 'ContentUri'.",
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint"
                    }
                },
                {
                    "Filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        },
                        "Path": None,
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 1
                        }
                    },
                    "Message": "Error transforming template: Resource with id [myFunctionMyTimer] is invalid. Missing required property 'Schedule'.",
                    "Rule": {
                        "Description": "Errors found when performing transformation on the template",
                        "Id": "E0001",
                        "ShortDescription": "Error found when transforming the template",
                        "Source": "https://github.com/aws-cloudformation/cfn-python-lint"
                    }
                }
            ],
            'exit_code': 2,
        },
        {
            'filename': 'test/fixtures/templates/good/conditions.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/resources_codepipeline.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_api.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_api.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect Resources/myFunctionVersionee13cf2679 from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_function.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_function.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 4
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 4
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect Resources/myFunctionVersionee13cf2679 from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform_serverless_globals.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_globals.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 9
                        },
                        "Path": [
                            "Resources",
                            "myFunctionVersionee13cf2679"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 9
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect Resources/myFunctionVersionee13cf2679 from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                },
                {
                    "Filename": "test/fixtures/templates/good/transform_serverless_globals.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {
                            "ColumnNumber": 13,
                            "LineNumber": 10
                        },
                        "Path": [
                            "Resources",
                            "myFunction",
                            "Properties",
                            "Runtime"
                        ],
                        "Start": {
                            "ColumnNumber": 3,
                            "LineNumber": 10
                        }
                    },
                    "Message": "Deprecated runtime (nodejs6.10) specified. Updating disabled since 2019-08-12, please consider to update to nodejs10.x",
                    "Rule": {
                        "Description": "Check if an EOL Lambda Runtime is specified and give an error if used. ",
                        "Id": "E2531",
                        "ShortDescription": "Check if EOL Lambda Function Runtimes are used",
                        "Source": "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html"
                    }
                }
            ],
            'exit_code': 6,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform.yaml',
            'results': [
                {
                    "Filename": "test/fixtures/templates/good/transform/list_transform.yaml",
                    "Level": "Warning",
                    "Location": {
                        "End": {
                            "ColumnNumber": 10,
                            "LineNumber": 14
                        },
                        "Path": [
                            "Resources",
                            "SkillFunctionVersionb3d38083f6"
                        ],
                        "Start": {
                            "ColumnNumber": 1,
                            "LineNumber": 14
                        }
                    },
                    "Message": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect Resources/SkillFunctionVersionb3d38083f6 from deletion",
                    "Rule": {
                        "Description": "Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources from deletion",
                        "Id": "W3011",
                        "ShortDescription": "Check resources with UpdateReplacePolicy/DeletionPolicy have both",
                        "Source": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
                    }
                }
            ],
            'exit_code': 4,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_many.yaml',
            'results': [],
            'exit_code': 0,
        },
        {
            'filename': 'test/fixtures/templates/good/transform/list_transform_not_sam.yaml',
            'results': [],
            'exit_code': 0,
        }
    ]

    def test_templates(self):
        """Test Successful JSON Parsing"""
        self.run_scenarios(['-c', 'I'])

    def test_module_integration(self):
        """ Test same templates using integration approach"""

        config = cfnlint.config.ConfigMixIn()
        config.include_checks = ['I']
        self.run_module_integration_scenarios(config)

    def test_module_integration_legacy(self):
        """ Test same templates using integration approach"""

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            rules = cfnlint.core.get_rules(
                [], [], ['E', 'I', 'W'], {}, False)
            self.run_module_legacy_integration_scenarios(rules)
