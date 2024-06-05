"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.template.getatts import GetAtts


class TestGetAtts(BaseTestCase):
    """Test GetAtts Class in template"""

    def test_getatt(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Module", "Organization::Resource::Type::MODULE")
        results = getatts.match("us-east-1", "ModuleResource.Module")
        self.assertEqual(results, "/properties/CfnLintAllTypes")

    def test_many_modules(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Module", "Organization::Resource::Type::MODULE")
        getatts.add("Module1", "Organization::Resource::Type::MODULE")
        results = getatts.match("us-east-1", "ModuleResource.Module")
        self.assertEqual(results, "/properties/CfnLintAllTypes")

        results = getatts.match("us-east-1", "Module1Resource.Module")
        self.assertEqual(results, "/properties/CfnLintAllTypes")

    def test_getatt_resource_and_modules(self):
        getatts = GetAtts(["us-east-1", "us-west-2"])
        getatts.add("Resource", "Organization::Resource::Type::MODULE")
        getatts.add("Resource1", "Organization::Resource::Type")
        results = getatts.match("us-east-1", "ResourceOne.Module")
        self.assertEqual(results, "/properties/CfnLintAllTypes")

        with self.assertRaises(ValueError):
            getatts.match("us-east-1", "NoMatch.Attribute")

    def test_getatt_type_errors(self):
        getatts = GetAtts(["us-east-1"])

        with self.assertRaises(TypeError):
            getatts.match("us-east-1", {})

        with self.assertRaises(TypeError):
            getatts.match("us-east-1", ["Foo", "Bar", "FooBar"])

    def test_getatt_resource_with_list(self):
        getatts = GetAtts(["us-east-1"])
        getatts.add("Resource", "AWS::NetworkFirewall::Firewall")
        results = getatts.match("us-east-1", "Resource.EndpointIds")
        self.assertEqual(results, "/properties/EndpointIds")
        self.assertDictEqual(
            getatts.json_schema("us-east-1"),
            {
                "oneOf": [
                    {
                        "type": "array",
                        "items": [
                            {"type": "string", "enum": ["Resource"]},
                            {"type": ["string", "object"]},
                        ],
                        "allOf": [
                            {
                                "if": {
                                    "items": [
                                        {"type": "string", "const": "Resource"},
                                        {"type": ["string", "object"]},
                                    ]
                                },
                                "then": {
                                    "if": {
                                        "items": [
                                            {"type": "string", "const": "Resource"},
                                            {"type": "string"},
                                        ]
                                    },
                                    "then": {
                                        "items": [
                                            {"type": "string", "const": "Resource"},
                                            {
                                                "type": "string",
                                                "enum": [
                                                    "FirewallArn",
                                                    "FirewallId",
                                                    "EndpointIds",
                                                ],
                                            },
                                        ]
                                    },
                                    "else": {
                                        "items": [
                                            {"type": "string", "const": "Resource"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "Ref": {"type": "string"}
                                                },
                                                "required": ["Ref"],
                                                "additionalProperties": False,
                                            },
                                        ]
                                    },
                                },
                                "else": {},
                            }
                        ],
                    },
                    {
                        "type": "string",
                        "enum": [
                            "Resource.FirewallArn",
                            "Resource.FirewallId",
                            "Resource.EndpointIds",
                        ],
                    },
                ]
            },
        )
