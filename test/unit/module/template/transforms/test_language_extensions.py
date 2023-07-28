"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from copy import deepcopy
from unittest import TestCase

from cfnlint.decode import convert_dict
from cfnlint.template import Template
from cfnlint.template.transforms._language_extensions import (
    _ForEach,
    _ForEachValue,
    _ForEachValueFnFindInMap,
    _ForEachValueRef,
    _ResolveError,
    _Transform,
    _TypeError,
    _ValueError,
    language_extension,
)


class TestForEach(TestCase):
    def test_valid(self):
        _ForEach("key", [{"Ref": "Parameter"}, ["Foo", {"Ref": "Parameter"}], {}], {})
        _ForEach(
            "key", [{"Ref": "Parameter"}, {"Ref": "AWS::NotificationArns"}, {}], {}
        )

    def test_wrong_type(self):
        with self.assertRaises(_TypeError):
            _ForEach("key", 1, {})

        with self.assertRaises(_TypeError):
            _ForEach("key", ["foo", []], {})

    def test_collection_type(self):
        with self.assertRaises(_TypeError):
            _ForEach("key", ["foo", "bar", {}], {})

        with self.assertRaises(_ValueError):
            _ForEach("key", ["foo", {"foo": "foo", "bar": "bar"}, {}], {})

    def test_identifier_type(self):
        with self.assertRaises(_TypeError):
            _ForEach("key", [[], "bar", {}], {})

        with self.assertRaises(_ValueError):
            _ForEach("key", [{"foo": "foo", "bar": "bar"}, "bar", {}], {})

    def test_output_type(self):
        with self.assertRaises(_TypeError):
            _ForEach("key", ["foo", ["bar"], []], {})


class TestRef(TestCase):
    def setUp(self) -> None:
        self.template_obj = convert_dict(
            {
                "Parameters": {
                    "Random": {
                        "Type": "String",
                    },
                    "Environment": {
                        "Type": "String",
                        "Default": "Production",
                    },
                    "AllowedValue": {"Type": "String", "AllowedValues": ["Names"]},
                    "Subnets": {
                        "Type": "List<AWS::EC2::Subnet::Id>",
                        "Default": "subnet-12345678, subnet-87654321",
                    },
                    "SecurityGroups": {
                        "Type": "List<AWS::EC2::Subnet::Id>",
                        "AllowedValues": ["sg-12345678, sg-87654321"],
                    },
                },
            }
        )
        self.cfn = Template(
            filename="", template=self.template_obj, regions=["us-west-2"]
        )

    def test_ref(self):
        fe = _ForEachValue.create({"Ref": "AWS::Region"})
        self.assertEqual(fe.value(self.cfn), "us-west-2")

        fe = _ForEachValue.create({"Ref": "AWS::AccountId"})
        self.assertEqual(fe.value(self.cfn), "123456789012")

        fe = _ForEachValue.create({"Ref": "AWS::NotificationARNs"})
        self.assertListEqual(
            fe.value(self.cfn), ["arn:aws:sns:us-west-2:123456789012:notification"]
        )

        fe = _ForEachValue.create({"Ref": "AWS::Partition"})
        self.assertEqual(fe.value(self.cfn), "aws")

        fe = _ForEachValue.create({"Ref": "AWS::StackId"})
        self.assertEqual(
            fe.value(self.cfn),
            "arn:aws:cloudformation:us-west-2:123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123",
        )

        fe = _ForEachValue.create({"Ref": "AWS::StackName"})
        self.assertEqual(fe.value(self.cfn), "teststack")

        fe = _ForEachValue.create({"Ref": "AWS::URLSuffix"})
        self.assertEqual(fe.value(self.cfn), "amazonaws.com")

        fe = _ForEachValue.create({"Ref": "Subnets"})
        self.assertEqual(fe.value(self.cfn), ["subnet-12345678", "subnet-87654321"])

        fe = _ForEachValue.create({"Ref": "SecurityGroups"})
        self.assertEqual(fe.value(self.cfn), ["sg-12345678", "sg-87654321"])


class TestFindInMap(TestCase):
    def setUp(self) -> None:
        self.template_obj = convert_dict(
            {
                "Transforms": ["AWS::LanguageExtensions"],
                "Parameters": {
                    "MapName": {
                        "Type": "String",
                    },
                    "Environment": {
                        "Type": "String",
                        "Default": "Production",
                    },
                    "Key": {"Type": "String", "AllowedValues": ["Names"]},
                },
                "Mappings": {
                    "Bucket": {"Production": {"Names": ["foo", "bar"]}},
                },
            }
        )
        self.cfn = Template(
            filename="", template=self.template_obj, regions=["us-east-1"]
        )

    def test_mappings(self):
        fe = _ForEachValue.create({"Fn::FindInMap": ["Bucket", "Production", "Names"]})
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": ["Bucket", {"Ref": "Environment"}, "Names"]}
        )
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": ["Bucket", "Production", {"Ref": "Key"}]}
        )
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": ["Bucket", {"Ref": "Environment"}, {"Ref": "Key"}]}
        )
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": ["Bucket", {"Ref": "Environment"}, {"Ref": "Key"}]}
        )
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

        fe = _ForEachValue.create(
            {
                "Fn::FindInMap": [
                    {"Ref": "MapName"},
                    {"Ref": "Environment"},
                    {"Ref": "Key"},
                ]
            }
        )
        self.assertListEqual(fe.value(self.cfn), ["foo", "bar"])

    def test_bad_mappings(self):
        with self.assertRaises(_TypeError):
            _ForEachValueFnFindInMap("", {})

        with self.assertRaises(_ValueError):
            _ForEachValueFnFindInMap("", ["foo"])

    def test_two_mappings(self):
        template_obj = deepcopy(self.template_obj)
        template_obj["Mappings"]["Foo"] = {"Bar": {"Key": ["a", "b"]}}
        del template_obj["Parameters"]["Key"]["AllowedValues"]

        self.cfn = Template(filename="", template=template_obj, regions=["us-east-1"])

        fe = _ForEachValue.create({"Fn::FindInMap": [{"Ref": "MapName"}, "Bar", "Key"]})
        self.assertListEqual(fe.value(self.cfn), ["a", "b"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": [{"Ref": "MapName"}, {"Ref": "Key"}, "Key"]}
        )
        self.assertListEqual(fe.value(self.cfn), ["a", "b"])

        fe = _ForEachValue.create({"Fn::FindInMap": ["Foo", {"Ref": "Key"}, "Key"]})
        self.assertListEqual(fe.value(self.cfn), ["a", "b"])

        fe = _ForEachValue.create(
            {"Fn::FindInMap": [{"Ref": "MapName"}, {"Ref": "Key"}, {"Ref": "Key"}]}
        )
        with self.assertRaises(_ResolveError):
            fe.value(self.cfn)

        fe = _ForEachValue.create(
            {"Fn::FindInMap": ["Foo", {"Ref": "Key"}, {"Ref": "Key"}]}
        )
        with self.assertRaises(_ResolveError):
            fe.value(self.cfn)


class TestTransform(TestCase):
    def setUp(self) -> None:
        self.template_obj = convert_dict(
            {
                "Transforms": ["AWS::LanguageExtensions"],
                "Mappings": {
                    "Bucket": {
                        "Outputs": {
                            "Attributes": [
                                "Arn",
                                "DomainName",
                            ],
                        },
                    },
                },
                "Resources": {
                    "Fn::ForEach::Buckets": [
                        "Identifier",
                        ["A", "B"],
                        {
                            "S3Bucket${Identifier}": {
                                "Type": "AWS::S3::Bucket",
                                "Properties": {
                                    "BucketName": {
                                        "Fn::Sub": "bucket-name-${Identifier}"
                                    },
                                },
                            }
                        },
                    ]
                },
                "Outputs": {
                    "Fn::ForEach::BucketOutputs": [
                        "Identifier",
                        ["A", "B"],
                        {
                            "Fn::ForEach::Attribute": [
                                "Property",
                                {"Fn::FindInMap": ["Bucket", "Outputs", "Attributes"]},
                                {
                                    "S3Bucket${Identifier}${Property}": {
                                        "Value": {
                                            "Fn::GetAtt": [
                                                {
                                                    "Fn::Sub": [
                                                        "S3Bucket${Identifier}",
                                                        {},
                                                    ]
                                                },
                                                {"Ref": "Property"},
                                            ]
                                        },
                                    },
                                },
                            ],
                        },
                    ]
                },
            }
        )
        self.result = {
            "Mappings": {
                "Bucket": {
                    "Outputs": {
                        "Attributes": [
                            "Arn",
                            "DomainName",
                        ],
                    },
                },
            },
            "Outputs": {
                "S3BucketAArn": {
                    "Value": {
                        "Fn::GetAtt": ["S3BucketA", "Arn"],
                    }
                },
                "S3BucketADomainName": {
                    "Value": {
                        "Fn::GetAtt": ["S3BucketA", "DomainName"],
                    }
                },
                "S3BucketBArn": {
                    "Value": {
                        "Fn::GetAtt": ["S3BucketB", "Arn"],
                    }
                },
                "S3BucketBDomainName": {
                    "Value": {
                        "Fn::GetAtt": ["S3BucketB", "DomainName"],
                    }
                },
            },
            "Resources": {
                "S3BucketA": {
                    "Properties": {
                        "BucketName": "bucket-name-A",
                    },
                    "Type": "AWS::S3::Bucket",
                },
                "S3BucketB": {
                    "Properties": {
                        "BucketName": "bucket-name-B",
                    },
                    "Type": "AWS::S3::Bucket",
                },
            },
            "Transforms": ["AWS::LanguageExtensions"],
        }

        return super().setUp()

    def test_transform(self):
        cfn = Template(filename="", template=self.template_obj, regions=["us-east-1"])
        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])
        self.assertDictEqual(
            template,
            self.result,
        )

    def test_transform_findinmap_function(self):
        template_obj = deepcopy(self.template_obj)
        parameters = {"Key2": {"Type": "String", "Default": "Attributes"}}
        template_obj["Parameters"] = parameters

        nested_set(
            template_obj,
            [
                "Outputs",
                "Fn::ForEach::BucketOutputs",
                2,
                "Fn::ForEach::Attribute",
                1,
                "Fn::FindInMap",
                2,
            ],
            {"Ref": "Key2"},
        )
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])
        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])

        result = deepcopy(self.result)
        result["Parameters"] = parameters
        self.assertDictEqual(
            template,
            result,
        )

    def test_bad_collection_ref(self):
        template_obj = deepcopy(self.template_obj)
        nested_set(
            template_obj,
            ["Resources", "Fn::ForEach::Buckets", 1],
            ["A", {"Ref": "Foo"}],
        )
        template_obj["Outputs"] = {}
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])
        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])
        self.assertTrue(len(template["Resources"]) == 2)
        self.assertTrue("S3BucketA" in template["Resources"])

    def test_duplicate_key(self):
        template_obj = deepcopy(self.template_obj)
        template_obj["Resources"]["S3BucketA"] = {"Type": "AWS::S3::Bucket"}
        template_obj["Outputs"] = {}
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])
        cfn.transform_pre["Fn::ForEach"] = []
        transform = _Transform()
        with self.assertRaises(_ValueError):
            transform.transform(cfn)

    def test_transform_error(self):
        template_obj = deepcopy(self.template_obj)
        template_obj["Resources"]["Fn::ForEach::Buckets"].append("foo")
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])

        matches, template = language_extension(cfn)

        self.assertIsNone(template)
        self.assertEqual(len(matches), 1)

    def test_bad_mapping(self):
        template_obj = deepcopy(self.template_obj)
        nested_set(
            template_obj,
            [
                "Resources",
                "Fn::ForEach::Buckets",
                2,
                "S3Bucket${Identifier}",
                "Properties",
                "Tags",
            ],
            [{"Key": "Foo", "Value": {"Fn::FindInMap": ["Bucket", "Tags", "Key"]}}],
        )
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])

        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])
        self.assertListEqual(
            template["Resources"]["S3BucketA"]["Properties"]["Tags"],
            [{"Key": "Foo", "Value": {"Fn::FindInMap": ["Bucket", "Tags", "Key"]}}],
        )


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        if isinstance(key, str):
            dic = dic.setdefault(key, {})
        if isinstance(key, int):
            dic = dic[key]
    dic[keys[-1]] = value
