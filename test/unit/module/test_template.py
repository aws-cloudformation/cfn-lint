"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import os
from test.testlib.testcase import BaseTestCase

from cfnlint.decode import cfn_yaml, convert_dict
from cfnlint.template import Template  # pylint: disable=E0401


class TestTemplate(BaseTestCase):
    """Test Template Class in cfnlint"""

    def setUp(self):
        """SetUp template object"""
        filename = "test/fixtures/templates/good/generic.yaml"
        template = self.load_template(filename)
        self.template = Template(filename, template)
        self.resource_names = [
            "IamPipeline",
            "RootInstanceProfile",
            "RolePolicies",
            "MyEC2Instance",
            "RootRole",
            "mySnsTopic",
            "MyEC2Instance1",
            "ElasticLoadBalancer",
            "MyModule",
        ]
        self.parameter_names = ["WebServerPort", "Package", "Package1", "pIops"]

    def test_build_graph(self):
        self.template.build_graph()

        dot = "test/fixtures/templates/good/generic.yaml.dot"

        expected_content = """digraph "template" {
MyModule [color=black, label="MyModule\\n<My::Organization::Custom::MODULE>", shape=ellipse, type=Resource];
RootRole [color=black, label="RootRole\\n<AWS::IAM::Role>", shape=ellipse, type=Resource];
RolePolicies [color=black, label="RolePolicies\\n<AWS::IAM::Policy>", shape=ellipse, type=Resource];
RootInstanceProfile [color=black, label="RootInstanceProfile\\n<AWS::IAM::InstanceProfile>", shape=ellipse, type=Resource];
MyEC2Instance [color=black, label="MyEC2Instance\\n<AWS::EC2::Instance>", shape=ellipse, type=Resource];
mySnsTopic [color=black, label="mySnsTopic\\n<AWS::SNS::Topic>", shape=ellipse, type=Resource];
MyEC2Instance1 [color=black, label="MyEC2Instance1\\n<AWS::EC2::Instance>", shape=ellipse, type=Resource];
ElasticIP [color=black, label="ElasticIP\\n<AWS::EC2::EIP>", shape=ellipse, type=Resource];
ElasticLoadBalancer [color=black, label="ElasticLoadBalancer\\n<AWS::ElasticLoadBalancing::LoadBalancer>", shape=ellipse, type=Resource];
IamPipeline [color=black, label="IamPipeline\\n<AWS::CloudFormation::Stack>", shape=ellipse, type=Resource];
CustomResource [color=black, label="CustomResource\\n<Custom::Function>", shape=ellipse, type=Resource];
WaitCondition [color=black, label="WaitCondition\\n<AWS::CloudFormation::WaitCondition>", shape=ellipse, type=Resource];
LambdaFunction [color=black, label="LambdaFunction\\n<AWS::Lambda::Function>", shape=ellipse, type=Resource];
RolePolicies -> RootRole  [color=black, key=0, label=Ref, source_paths="['Properties', 'Roles', 0]"];
RootInstanceProfile -> RootRole  [color=black, key=0, label=Ref, source_paths="['Properties', 'Roles', 0]"];
MyEC2Instance -> RootInstanceProfile  [color=black, key=0, label=Ref, source_paths="['Properties', 'IamInstanceProfile']"];
ElasticLoadBalancer -> MyEC2Instance  [color=black, key=0, label=Ref, source_paths="['Properties', 'Instances', 0]"];
}
""".split(
            "\n"
        )

        assert os.path.exists(dot)
        with open(dot, "r") as file:
            file_contents = file.read().split("\n")
            # doing set equality instead of string equality because python 2.7 and 3.8 produce the same graph but with different edge order
            assert len(file_contents) == len(
                expected_content
            ), f"Length {len(file_contents)} != {len(expected_content)}"
            assert sorted(file_contents) == sorted(expected_content)

        os.remove(dot)

    def test_get_resources_success(self):
        """Test Success on Get Resources"""
        valid_resource_count = 13
        resources = self.template.get_resources()
        assert (
            len(resources) == valid_resource_count
        ), "Expected {} resources, got {}".format(valid_resource_count, len(resources))

    def test_get_modules_success(self):
        """Test Success on Get Modules"""
        expected_modules_count = 1
        actual_modules = self.template.get_modules()
        assert (
            len(actual_modules) == expected_modules_count
        ), "Expected {} modules, got {}".format(
            expected_modules_count, len(actual_modules)
        )

    def test_get_resources_bad(self):
        """Don't get resources that aren't properly configured"""
        template = {
            "Resources": {
                "Properties": {"BucketName": "bucket_test"},
                "Type": "AWS::S3::Bucket",
            }
        }
        self.template = Template("test.yaml", template)
        resources = self.template.get_resources()
        assert resources == {}

    def test_get_resource_names(self):
        """Test Resource Names"""
        resource_names = self.template.get_resource_names()
        assert bool(set(resource_names).intersection(self.resource_names))

    def test_get_parameters(self):
        """Test Get Parameters"""
        valid_parameter_count = 7
        parameters = self.template.get_parameters()
        assert (
            len(parameters) == valid_parameter_count
        ), "Expected {} parameters, got {}".format(
            valid_parameter_count, len(parameters)
        )

    def test_get_parameter_names(self):
        """Test Get Parameter Names"""
        parameters = self.template.get_parameter_names()
        assert bool(set(parameters).intersection(self.parameter_names))

    def test_get_valid_refs(self):
        """Get Valid REFs"""
        valid_ref_count = 28
        refs = self.template.get_valid_refs()
        assert len(refs) == valid_ref_count, "Expected {} refs, got {}".format(
            valid_ref_count, len(refs)
        )

    def test_conditions_return_object_success(self):
        """Test condition object response and nested IFs"""
        template = [
            "isProd",
            {"Key": "Environment1", "Value": "Prod"},
            {
                "Fn::If": [
                    "isDev",
                    {"Key": "Environment2", "Value": "Dev"},
                    {"Ref": "AWS::NoValue"},
                ]
            },
        ]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(
            results,
            [
                {"Path": [1], "Value": {"Value": "Prod", "Key": "Environment1"}},
                {
                    "Path": [2, "Fn::If", 1],
                    "Value": {"Value": "Dev", "Key": "Environment2"},
                },
            ],
        )

    def test_conditions_return_list_success(self):
        """Test condition list response"""
        template = ["PrimaryRegion", ["EN"], ["BE", "LU", "NL"]]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(
            results,
            [
                {"Value": ["EN"], "Path": [1]},
                {"Value": ["BE", "LU", "NL"], "Path": [2]},
            ],
        )

    def test_conditions_return_string_success(self):
        """Test condition object response and nested IFs"""
        template = ["isProd", {"Ref": "Sample"}, "String"]

        results = self.template.get_condition_values(template, [])
        self.assertEqual(
            results,
            [
                {"Path": [1], "Value": {"Ref": "Sample"}},
                {"Path": [2], "Value": "String"},
            ],
        )

    def test_is_resource_available(self):
        """Test is resource available"""
        temp_obj = convert_dict(
            {
                "Mappings": {"location": {"us-east-1": {"primary": "True"}}},
                "Conditions": {
                    "isPrimary": {
                        "Fn::Equals": [
                            "True",
                            {
                                "Fn::FindInMap": [
                                    "location",
                                    {"Ref": "AWS::Region"},
                                    "primary",
                                ]
                            },
                        ]
                    },
                    "isNotPrimary": {"Fn::Not": [{"Condition": "isPrimary"}]},
                },
                "Resources": {
                    "LambdaExecutionRole": {
                        "Condition": "isPrimary",
                        "Type": "AWS::IAM::Role",
                        "Properties": {},
                    },
                    "AMIIDLookup": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Handler": "index.handler",
                            "Role": {
                                "Fn::If": [
                                    "isPrimary",
                                    {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                    {"Ref": "AWS::NoValue"},
                                ]
                            },
                        },
                    },
                    "AMIIDLookupBackup": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Handler": "index.handler",
                            "Role": {
                                "Fn::If": [
                                    "isPrimary",
                                    {
                                        "Fn::If": [
                                            "isPrimary",
                                            {"Ref": "AWS::NoValue"},
                                            {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                        ]
                                    },
                                    {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                ]
                            },
                        },
                    },
                },
                "Outputs": {
                    "lambdaArn": {
                        "Condition": "isPrimary",
                        "Value": {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                    },
                    "AMIIDLookupBackup": {
                        "Value": {
                            "Fn::If": [
                                "isNotPrimary",
                                {
                                    "Fn::If": [
                                        "isNotPrimary",
                                        {"Ref": "AWS::NoValue"},
                                        {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                    ]
                                },
                                {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                            ]
                        }
                    },
                },
            }
        )
        template = Template("test.yaml", temp_obj)
        # Doesn't fail with a Fn::If based condition
        self.assertEqual(
            template.is_resource_available(
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "Role",
                    "Fn::If",
                    1,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [],
        )
        # Failure when the opposite of the resource condition is used
        self.assertEqual(
            template.is_resource_available(
                [
                    "Resources",
                    "AMIIDLookupBackup",
                    "Properties",
                    "Role",
                    "Fn::If",
                    2,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [{"isPrimary": {False}}],
        )
        # No error when the condition has both true/false use cases
        self.assertEqual(
            template.is_resource_available(
                [
                    "Outputs",
                    "AMIIDLookupBackup",
                    "Value",
                    "Fn::If",
                    1,
                    "Fn::If",
                    2,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [],
        )
        # Doesn't fail when the Output has a Condition defined
        self.assertEqual(
            template.is_resource_available(
                [
                    "Outputs",
                    "lambdaArn",
                    "Value",
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [],
        )
        # Doesn't fail when the Resource doesn't exist
        self.assertEqual(
            template.is_resource_available(
                [
                    "Outputs",
                    "lambdaArn",
                    "Value",
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "UnknownResource",
            ),
            [],
        )

    def test_is_resource_not_available(self):
        """Test is resource available"""
        temp_obj = convert_dict(
            {
                "Mappings": {"location": {"us-east-1": {"primary": "True"}}},
                "Conditions": {
                    "isPrimary": {
                        "Fn::Equals": [
                            "True",
                            {
                                "Fn::FindInMap": [
                                    "location",
                                    {"Ref": "AWS::Region"},
                                    "primary",
                                ]
                            },
                        ]
                    },
                },
                "Resources": {
                    "LambdaExecutionRole": {
                        "Condition": "isPrimary",
                        "Type": "AWS::IAM::Role",
                        "Properties": {},
                    },
                    "AMIIDLookup": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Handler": "index.handler",
                            "Role": {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                        },
                    },
                },
                "Outputs": {
                    "lambdaArn": {"Value": {"Fn::GetAtt": "LambdaExecutionRole.Arn"}}
                },
            }
        )
        template = Template("test.yaml", temp_obj)
        self.assertEqual(
            template.is_resource_available(
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "Role",
                    "Fn::If",
                    1,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [{"isPrimary": False}],
        )
        self.assertEqual(
            template.is_resource_available(
                [
                    "Outputs",
                    "lambdaArn",
                    "Value",
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [{"isPrimary": False}],
        )
        # Doesn't fail when the Path doesn't exist.  Still shows an error based on the fact there
        # are no conditions in the path that is workable
        self.assertEqual(
            template.is_resource_available(
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "BadProperty",
                    "Fn::If",
                    1,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
                "LambdaExecutionRole",
            ),
            [{"isPrimary": False}],
        )
        # Gives appropriate response when there is no condition in path
        self.assertEqual(
            template.is_resource_available(
                ["Resources", "AMIIDLookup", "Properties", "Handler"],
                "LambdaExecutionRole",
            ),
            [{"isPrimary": False}],
        )

    def test_get_conditions_from_path(self):
        """Test is resource available"""
        temp_obj = convert_dict(
            {
                "Resources": {
                    "AMIIDLookup": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Role": {
                                "Fn::If": [
                                    "isPrimary",
                                    {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                    {"Ref": "AWS::NoValue"},
                                ]
                            }
                        },
                    },
                    "InstanceProfile": {
                        "Condition": "isPrimaryAndProduction",
                        "Type": "AWS::IAM::InstanceProfile",
                        "Properties": {
                            "Path": "/",
                            "Roles": [{"Ref": "LambdaExecutionRole"}],
                        },
                    },
                },
                "Outputs": {
                    "lambdaArn": {
                        "Condition": "isPrimary",
                        "Value": {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                    }
                },
            }
        )
        template = Template("test.yaml", temp_obj)
        # Gets the condition when in the middle of the Path
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "Role",
                    "Fn::If",
                    1,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
            ),
            {"isPrimary": {True}},
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                ["Resources", "AMIIDLookup", "Properties", "Role", "Fn::If"],
            ),
            {"isPrimary": {True, False}},
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Outputs",
                    "lambdaArn",
                    "Value",
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
            ),
            {"isPrimary": {True}},
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Resources",
                    "InstanceProfile",
                    "Properties",
                    "Roles",
                    0,
                    "Ref",
                    "LambdaExecutionRole",
                ],
            ),
            {"isPrimaryAndProduction": {True}},
        )
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "Handler",
                    "Ref",
                    "LambdaHandler",
                ],
            ),
            {},
        )

    def test_failure_get_conditions_from_path(self):
        """Test get conditions from path when things arne't formatted correctly"""
        temp_obj = convert_dict(
            {
                "Resources": {
                    "AMIIDLookup": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Role": {
                                "Fn::If": [
                                    "isPrimary",
                                    {"Fn::GetAtt": "LambdaExecutionRole.Arn"},
                                ]
                            }
                        },
                    },
                    "myInstance4": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "InstanceType": {
                                "Fn::If": {
                                    "Fn::If": ["isPrimary", "t3.2xlarge", "t3.xlarge"]
                                }
                            }
                        },
                    },
                }
            }
        )
        template = Template("test.yaml", temp_obj)
        # Gets no condition names when it isn't a valid list
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Resources",
                    "AMIIDLookup",
                    "Properties",
                    "Role",
                    "Fn::If",
                    1,
                    "Fn::GetAtt",
                    ["LambdaExecutionRole", "Arn"],
                ],
            ),
            {},
        )
        # Gets no condition names when it isn't really a list
        self.assertEqual(
            template.get_conditions_from_path(
                template.template,
                [
                    "Resources",
                    "myInstance4",
                    "Properties",
                    "InstanceType",
                    "Fn::If",
                    "Fn::If",
                    0,
                ],
            ),
            {},
        )

    def test_get_conditions_scenarios_from_object(self):
        """Test Getting condition names in an object/list"""
        template = {
            "Conditions": {
                "isProduction": {"Fn::Equals": [{"Ref": "myEnvironment"}, "Prod"]},
                "isPrimary": {
                    "Fn::Equals": [
                        "True",
                        {
                            "Fn::FindInMap": [
                                "location",
                                {"Ref": "AWS::Region"},
                                "primary",
                            ]
                        },
                    ]
                },
                "isPrimaryAndProduction": {
                    "Fn::And": [
                        {"Condition": "isProduction"},
                        {"Condition": "isPrimary"},
                    ]
                },
                "isDevelopment": {"Fn::Equals": [{"Ref": "myEnvironment"}, "Dev"]},
            },
            "Resources": {
                "myInstance1": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "Fn::If": [
                            "isPrimaryAndProduction",
                            {"ImageId": "ami-1234567", "InstanceType": "t2.medium"},
                            {
                                "Fn::If": [
                                    "isDevelopment",
                                    {
                                        "ImageId": "ami-abcdefg",
                                        "InstanceType": "t2.xlarge",
                                    },
                                    {
                                        "ImageId": "ami-123abcd",
                                        "InstanceType": "m3.medium",
                                    },
                                ]
                            },
                        ]
                    },
                },
                "myInstance2": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": {
                            "Fn::If": ["isProduction", "ami-123456", "ami-abcdef"]
                        },
                        "InstanceType": {
                            "Fn::If": [
                                "isPrimaryAndProduction",
                                {"Fn::If": ["isPrimary", "t3.2xlarge", "t3.xlarge"]},
                                "t3.medium",
                            ]
                        },
                    },
                },
            },
        }
        template = Template("test.yaml", template)
        # includes nested IFs
        self.assertEqualListOfDicts(
            template.get_conditions_scenarios_from_object(
                template.template.get("Resources", {})
                .get("myInstance2", {})
                .get("Properties", {})
            ),
            [
                {
                    "isPrimary": True,
                    "isProduction": True,
                    "isPrimaryAndProduction": True,
                },
                {
                    "isPrimary": True,
                    "isProduction": False,
                    "isPrimaryAndProduction": False,
                },
                {
                    "isPrimary": False,
                    "isProduction": True,
                    "isPrimaryAndProduction": False,
                },
                {
                    "isPrimary": False,
                    "isProduction": False,
                    "isPrimaryAndProduction": False,
                },
            ],
        )
        self.assertEqualListOfDicts(
            template.get_conditions_scenarios_from_object(
                template.template.get("Resources", {})
                .get("myInstance1", {})
                .get("Properties", {})
            ),
            [
                {"isPrimaryAndProduction": True, "isDevelopment": False},
                {"isPrimaryAndProduction": False, "isDevelopment": True},
                {"isPrimaryAndProduction": False, "isDevelopment": False},
            ],
        )

    def test_get_object_without_conditions(self):
        """Test Getting condition names in an object/list"""
        template = convert_dict(
            {
                "Conditions": {
                    "useAmiId": {"Fn::Not": [{"Fn::Equals": [{"Ref": "myAmiId"}, ""]}]}
                },
                "Resources": {
                    "myInstance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "ImageId": {
                                "Fn::If": [
                                    "useAmiId",
                                    {"Ref": "myAmiId"},
                                    {"Ref": "AWS::NoValue"},
                                ]
                            },
                            "LaunchConfiguration": {
                                "Fn::If": [
                                    "useAmiId",
                                    {"Ref": "AWS::NoValue"},
                                    {"Ref": "LaunchConfiguration"},
                                ]
                            },
                        },
                    }
                },
            }
        )
        template = Template("test.yaml", template)

        results = template.get_object_without_conditions(
            template.template.get("Resources", {})
            .get("myInstance", {})
            .get("Properties", {})
        )

        for result in results:
            if result["Scenario"] == {"useAmiId": True}:
                self.assertDictEqual(result["Object"], {"ImageId": {"Ref": "myAmiId"}})
            elif result["Scenario"] == {"useAmiId": False}:
                self.assertDictEqual(
                    result["Object"],
                    {"LaunchConfiguration": {"Ref": "LaunchConfiguration"}},
                )

    def test_get_object_without_conditions_no_value(self):
        """Test Getting condition names in an object/list"""
        template = {
            "Conditions": {
                "CreateAppVolume": {"Fn::Equals": [{"Ref": "myAppVolume"}, "true"]}
            },
            "Resources": {
                "myInstance": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": "ami-123456",
                        "BlockDeviceMappings": [
                            {
                                "DeviceName": "/dev/hda1",
                                "Ebs": {
                                    "DeleteOnTermination": True,
                                    "VolumeType": "gp2",
                                },
                            },
                            {
                                "Fn::If": [
                                    "CreateAppVolume",
                                    {
                                        "DeviceName": "/dev/xvdf",
                                        "Ebs": {
                                            "DeleteOnTermination": True,
                                            "VolumeType": "gp2",
                                        },
                                    },
                                    {"Ref": "AWS::NoValue"},
                                ]
                            },
                        ],
                    },
                }
            },
        }
        template = Template("test.yaml", template)

        results = template.get_object_without_conditions(
            template.template.get("Resources")
            .get("myInstance")
            .get("Properties")
            .get("BlockDeviceMappings")[1]
            .get("Fn::If")[2]
        )

        self.assertEqual(results, [])

        results = template.get_object_without_conditions(
            template.template.get("Resources")
            .get("myInstance")
            .get("Properties")
            .get("BlockDeviceMappings")
        )
        # when item is a list return empty list
        self.assertEqual(results, [])

        # when item is a string return empty list
        self.assertEqual(template.get_object_without_conditions("String"), [])

    def test_get_object_without_conditions_for_list(self):
        """Test Getting condition names in an object/list"""
        template = convert_dict(
            {
                "Conditions": {
                    "CreateAppVolume": {"Fn::Equals": [{"Ref": "CreateVolums"}, "true"]}
                },
                "Resources": {
                    "myInstance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "ImageId": "ami-123456",
                            "BlockDeviceMappings": {
                                "Fn::If": [
                                    "CreateAppVolume",
                                    [
                                        {
                                            "DeviceName": "/dev/hda1",
                                            "Ebs": {
                                                "DeleteOnTermination": True,
                                                "VolumeType": "gp2",
                                            },
                                        },
                                        {
                                            "DeviceName": "/dev/xvdf",
                                            "Ebs": {
                                                "DeleteOnTermination": True,
                                                "VolumeType": "gp2",
                                            },
                                        },
                                    ],
                                    {"Ref": "AWS::NoValue"},
                                ]
                            },
                        },
                    }
                },
            }
        )

        template = Template("test.yaml", template)

        results = template.get_object_without_conditions(
            template.template.get("Resources")
            .get("myInstance")
            .get("Properties")
            .get("BlockDeviceMappings")
        )
        # handles IFs for a list
        self.assertEqual(
            results,
            [
                {
                    "Scenario": {"CreateAppVolume": True},
                    "Object": [
                        {
                            "DeviceName": "/dev/hda1",
                            "Ebs": {"DeleteOnTermination": True, "VolumeType": "gp2"},
                        },
                        {
                            "DeviceName": "/dev/xvdf",
                            "Ebs": {"DeleteOnTermination": True, "VolumeType": "gp2"},
                        },
                    ],
                }
            ],
        )

    def test_get_object_without_conditions_for_bad_formats(self):
        """Test Getting condition names in an object/list"""
        template = {
            "Conditions": {
                "CreateAppVolume": {"Fn::Equals": [{"Ref": "CreateVolums"}, "true"]}
            },
            "Resources": {
                "myInstance": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": "ami-123456",
                        "BlockDeviceMappings": {
                            "Fn::If": ["CreateAppVolume", {"Ref": "AWS::NoValue"}]
                        },
                    },
                },
                "myInstance1": {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "ImageId": "ami-123456",
                        "BlockDeviceMappings": {"Fn::If": ["CreateAppVolume"]},
                    },
                },
            },
        }

        template = Template("test.yaml", template)

        results = template.get_object_without_conditions(
            template.template.get("Resources")
            .get("myInstance")
            .get("Properties")
            .get("BlockDeviceMappings")
        )
        # There is no False here but it still passes the 1st item back
        self.assertEqual(
            results,
            [
                {
                    "Object": {"Fn::If": ["CreateAppVolume", {"Ref": "AWS::NoValue"}]},
                    "Scenario": None,
                }
            ],
        )

        results = template.get_object_without_conditions(
            template.template.get("Resources")
            .get("myInstance1")
            .get("Properties")
            .get("BlockDeviceMappings")
        )
        # There is no False here but it still passes the 1st item back
        self.assertEqual(
            results, [{"Object": {"Fn::If": ["CreateAppVolume"]}, "Scenario": None}]
        )

    def test_get_object_without_nested_conditions(self):
        """Test Getting condition names in an object/list"""
        template = convert_dict(
            {
                "Conditions": {
                    "isProduction": {"Fn::Equals": [{"Ref": "myEnvironment"}, "prod"]},
                    "isDevelopment": {"Fn::Equals": [{"Ref": "myEnvironment"}, "dev"]},
                },
                "Resources": {
                    "myInstance": {
                        "Type": "AWS::EC2::Instance",
                        "Properties": {
                            "ImageId": {
                                "Fn::If": [
                                    "isProduction",
                                    "ami-prod1234",
                                    {
                                        "Fn::If": [
                                            "isDevelopment",
                                            "ami-dev1234",
                                            "ami-lab1234",
                                        ]
                                    },
                                ]
                            }
                        },
                    }
                },
            }
        )
        template = Template("test.yaml", template)

        results = template.get_object_without_conditions(
            template.template.get("Resources", {})
            .get("myInstance", {})
            .get("Properties", {})
        )

        self.assertEqual(len(results), 3)
        for result in results:
            if (
                result["Scenario"]["isProduction"]
                and not result["Scenario"]["isDevelopment"]
            ):
                self.assertDictEqual(result["Object"], {"ImageId": "ami-prod1234"})
            elif result["Scenario"] == {"isProduction": False, "isDevelopment": True}:
                self.assertDictEqual(result["Object"], {"ImageId": "ami-dev1234"})
            elif result["Scenario"] == {"isProduction": False, "isDevelopment": False}:
                self.assertDictEqual(result["Object"], {"ImageId": "ami-lab1234"})
            else:
                # Blanket assertion error
                self.assertDictEqual(result["Scenario"], {})

    def test_get_object_without_nested_conditions_iam(self):
        """Test Getting condition names in an object/list"""
        template = {
            "Conditions": {
                "isProduction": {"Fn::Equals": [{"Ref": "myEnvironment"}, "prod"]},
                "isDevelopment": {"Fn::Equals": [{"Ref": "myEnvironment"}, "dev"]},
            },
            "Resources": {
                "Role": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "",
                                    "Action": "sts:AssumeRole",
                                    "Effect": "Allow",
                                    "Principal": {
                                        "AWS": {
                                            "Fn::If": [
                                                "isProduction",
                                                "123456789012",
                                                "210987654321",
                                            ]
                                        }
                                    },
                                }
                            ],
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/AdministratorAccess"
                        ],
                        "Path": "/",
                    },
                }
            },
        }

        template = Template("test.yaml", template)

        results = template.get_object_without_nested_conditions(
            template.template.get("Resources", {})
            .get("Role", {})
            .get("Properties", {})
            .get("AssumeRolePolicyDocument", {}),
            ["Resources", "Role", "Properties", "AssumeRolePolicyDocument"],
        )

        self.assertEqual(len(results), 2)
        for result in results:
            if not result["Scenario"]["isProduction"]:
                self.assertDictEqual(
                    result["Object"],
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "",
                                "Action": "sts:AssumeRole",
                                "Effect": "Allow",
                                "Principal": {"AWS": "210987654321"},
                            }
                        ],
                    },
                )
            if result["Scenario"]["isProduction"]:
                self.assertDictEqual(
                    result["Object"],
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "",
                                "Action": "sts:AssumeRole",
                                "Effect": "Allow",
                                "Principal": {"AWS": "123456789012"},
                            }
                        ],
                    },
                )

    def test_get_object_without_nested_conditions_basic(self):
        """Test Getting condition names in an object/list"""
        template = {"Resources": {"Test": "Test"}}

        template = Template("test.yaml", template)

        results = template.get_object_without_nested_conditions(
            template.template.get("Resources", {}).get("Test", {}),
            ["Resources", "Test"],
        )
        self.assertEqual(results, [])

    def test_get_object_without_nested_conditions_ref(self):
        """Test Getting condition names in an object/list"""
        template = {"Resources": {"Test": {"Ref": "AWS::NoValue"}}}

        template = Template("test.yaml", template)

        results = template.get_object_without_nested_conditions(
            template.template.get("Resources", {}).get("Test", {}),
            ["Resources", "Test"],
        )
        self.assertEqual(results, [])
        results = template.get_object_without_nested_conditions(
            template.template.get("Resources", {}), ["Resources"]
        )
        self.assertEqual(
            results, [{"Object": {"Test": {"Ref": "AWS::NoValue"}}, "Scenario": None}]
        )

    def test_get_condition_scenarios_below_path(self):
        """Test Getting condition names in an object/list"""
        template = {
            "Parameters": {"Environment": {"Type": "String"}},
            "Conditions": {
                "isPrimaryRegion": {
                    "Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]
                },
                "isProduction": {"Fn::Equals": [{"Ref": "Environment"}, "prod"]},
            },
            "Resources": {
                "Role": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "",
                                    "Action": "sts:AssumeRole",
                                    "Effect": "Allow",
                                    "Principal": {
                                        "AWS": {
                                            "Fn::If": [
                                                "isProduction",
                                                {
                                                    "Fn::Sub": [
                                                        "{account}",
                                                        {
                                                            "account": {
                                                                "Fn::If": [
                                                                    "isPrimaryRegion",
                                                                    "123456789012",
                                                                    "ABCDEFGHIJKL",
                                                                ]
                                                            }
                                                        },
                                                    ]
                                                },
                                                "210987654321",
                                            ]
                                        }
                                    },
                                }
                            ],
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/AdministratorAccess"
                        ],
                        "Path": "/",
                    },
                }
            },
        }

        template = Template("test.yaml", template)
        results = template.get_condition_scenarios_below_path(
            ["Resources", "Role", "Properties", "AssumeRolePolicyDocument"]
        )
        self.assertEqualListOfDicts(
            results, [{"isProduction": True}, {"isProduction": False}]
        )
        results = template.get_condition_scenarios_below_path(
            ["Resources", "Role", "Properties", "AssumeRolePolicyDocument"], True
        )
        self.assertEqualListOfDicts(
            results,
            [
                {"isPrimaryRegion": False, "isProduction": False},
                {"isPrimaryRegion": False, "isProduction": True},
                {"isPrimaryRegion": True, "isProduction": False},
                {"isPrimaryRegion": True, "isProduction": True},
            ],
        )

    def test_get_directives(self):
        """Test getting directives from a template"""
        template_yaml = {
            "Resources": {
                "Type": "AWS::S3::Bucket",
                "myBucket": {
                    "Properties": {"BucketName": "bucket_test"},
                    "Type": "AWS::S3::Bucket",
                },
                "myBucket1": {
                    "Metadata": {
                        "cfn-lint": {"config": {"ignore_checks": ["E3012", "I1001"]}}
                    },
                    "Properties": {},
                    "Type": "AWS::S3::Bucket",
                },
                "myBucket2": {
                    "Metadata": {
                        "cfn-lint": {
                            "config": {
                                "ignore_checks": [
                                    "E3012",
                                ]
                            }
                        }
                    },
                    "Properties": {},
                    "Type": "AWS::S3::Bucket",
                },
            }
        }

        template = Template(
            "test.yaml",
            cfn_yaml.loads(
                json.dumps(
                    template_yaml, sort_keys=True, indent=4, separators=(",", ": ")
                )
            ),
        )
        directives = template.get_directives()
        expected_result = {
            "E3012": [
                {"end": (23, 10), "start": (10, 9)},
                {"end": (36, 10), "start": (24, 9)},
            ],
            "I1001": [{"end": (23, 10), "start": (10, 9)}],
        }
        self.assertEqual(len(expected_result), len(directives))
        for key, items in directives.items():
            self.assertIn(key, expected_result)
            if key in expected_result:
                self.assertEqualListOfDicts(items, expected_result.get(key))
