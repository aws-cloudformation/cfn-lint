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
    _ForEachCollection,
    _ForEachValue,
    _ForEachValueFnFindInMap,
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
        _ForEach("key", ["AccountId", {"Ref": "AccountIds"}, {}], {})

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


class TestForEachCollection(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cfn = Template(
            "",
            {
                "Parameters": {
                    "AccountIds": {
                        "Type": "CommaDelimitedList",
                    },
                },
            },
            regions=["us-west-2"],
        )

    def test_valid(self):
        fec = _ForEachCollection({"Ref": "AccountIds"})
        self.assertListEqual(
            list(fec.values(self.cfn, {})),
            [
                {"Fn::Select": [0, {"Ref": "AccountIds"}]},
                {"Fn::Select": [1, {"Ref": "AccountIds"}]},
            ],
        )


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
                    "AccountIds": {
                        "Type": "CommaDelimitedList",
                    },
                    "SSMParameter": {
                        "Type": "AWS::SSM::Parameter::Value<String>",
                        "Default": "/global/account/accounttype",
                        "AllowedValues": ["/global/account/accounttype"],
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

        fe = _ForEachValue.create({"Ref": "AccountIds"})
        self.assertEqual(
            fe.value(self.cfn),
            [
                {"Fn::Select": [0, {"Ref": "AccountIds"}]},
                {"Fn::Select": [1, {"Ref": "AccountIds"}]},
            ],
        )

        fe = _ForEachValue.create({"Ref": "SSMParameter"})
        with self.assertRaises(_ResolveError):
            fe.value(self.cfn)


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
                    "List": {"Type": "CommaDelimitedList", "Default": "foo,bar"},
                },
                "Mappings": {
                    "Bucket": {"Production": {"Names": ["foo", "bar"]}},
                    "AnotherBucket": {"Production": {"Names": ["a", "b"]}},
                    "Config": {
                        "DBInstances": {
                            "Development": "1",
                            "Stage": ["1", "2"],
                            "Production": ["1", "2", "3"],
                        },
                        "Instances": {
                            "Development": "A",
                            "Stage": ["A", "B"],
                            "Production": ["A", "B", "C"],
                        },
                    },
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
                    {"Ref": "MapName"},
                    {"Ref": "MapName"},
                    {"DefaultValue": ["one", "two"]},
                ]
            }
        )
        self.assertListEqual(fe.value(self.cfn), ["one", "two"])

        fe = _ForEachValue.create(
            {
                "Fn::FindInMap": [
                    {"Ref": "MapName"},
                    {"Ref": "MapName"},
                    {"Ref": "MapName"},
                    {"DefaultValue": {"Ref": "List"}},
                ]
            }
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

        with self.assertRaises(_TypeError):
            _ForEachValueFnFindInMap("", ["", "", "", []])

        with self.assertRaises(_ValueError):
            _ForEachValueFnFindInMap("", ["", "", "", {"Default": "Bad"}])

        with self.assertRaises(_ValueError):
            _ForEachValueFnFindInMap("", ["", "", "", {"Foo": "Bar", "Bar": "Foo"}])

    def test_find_in_map_values_with_default(self):
        map = _ForEachValueFnFindInMap(
            "a", ["Bucket", {"Ref": "Foo"}, "Key", {"DefaultValue": "bar"}]
        )

        self.assertEqual(map.value(self.cfn, None, False, True), "bar")
        with self.assertRaises(_ResolveError):
            map.value(self.cfn, None, False, False)

    def test_find_in_map_values_without_default(self):
        map = _ForEachValueFnFindInMap("a", ["Bucket", {"Ref": "Foo"}, "Key"])

        with self.assertRaises(_ResolveError):
            self.assertEqual(map.value(self.cfn, None, False, True), "bar")
        with self.assertRaises(_ResolveError):
            map.value(self.cfn, None, False, False)

    def test_second_key_resolution(self):
        map = _ForEachValueFnFindInMap("a", ["Config", {"Ref": "Value"}, "Production"])

        self.assertEqual(
            map.value(self.cfn, {"Value": "DBInstances"}, False, True), ["1", "2", "3"]
        )

        self.assertEqual(
            map.value(self.cfn, {"Value": "Instances"}, False, True), ["A", "B", "C"]
        )

    def test_find_in_map_values_without_default_resolve_error(self):
        map = _ForEachValueFnFindInMap(
            "a", ["Bucket", "Production", {"Ref": "SSMParameter"}]
        )

        self.assertEqual(map.value(self.cfn, None, False, True), ["foo", "bar"])

        map = _ForEachValueFnFindInMap(
            "a", ["Config", "DBInstances", {"Ref": "SSMParameter"}]
        )

        self.assertEqual(map.value(self.cfn, None, False, True), ["1", "2"])

    def test_mapping_not_found(self):
        map = _ForEachValueFnFindInMap(
            "a", ["Foo", {"Ref": "Foo"}, "Key", {"DefaultValue": "bar"}]
        )

        self.assertEqual(map.value(self.cfn, None, False, True), "bar")
        with self.assertRaises(_ResolveError):
            map.value(self.cfn, None, False, False)

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
                    ],
                    "Fn::ForEach::SpecialCharacters": [
                        "Identifier",
                        ["a-b", "c-d"],
                        {
                            "S3Bucket&{Identifier}": {
                                "Type": "AWS::S3::Bucket",
                                "Properties": {
                                    "BucketName": {
                                        "Fn::Sub": "bucket-name-&{Identifier}"
                                    },
                                },
                            }
                        },
                    ],
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
                "S3Bucketab": {
                    "Properties": {
                        "BucketName": "bucket-name-ab",
                    },
                    "Type": "AWS::S3::Bucket",
                },
                "S3Bucketcd": {
                    "Properties": {
                        "BucketName": "bucket-name-cd",
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
            template,
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

    def test_transform_list_parameter(self):
        template_obj = deepcopy(self.template_obj)
        parameters = {"AccountIds": {"Type": "CommaDelimitedList"}}
        template_obj["Parameters"] = parameters

        nested_set(
            template_obj,
            [
                "Resources",
                "Fn::ForEach::SpecialCharacters",
                1,
            ],
            {"Ref": "AccountIds"},
        )
        nested_set(
            template_obj,
            [
                "Resources",
                "Fn::ForEach::SpecialCharacters",
                2,
            ],
            {
                "S3Bucket&{Identifier}": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "BucketName": {"Ref": "Identifier"},
                        "Tags": [
                            {"Key": "Name", "Value": {"Fn::Sub": "Name-${Identifier}"}},
                        ],
                    },
                }
            },
        )
        cfn = Template(filename="", template=template_obj, regions=["us-east-1"])
        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])

        result = deepcopy(self.result)
        result["Parameters"] = parameters
        result["Resources"]["S3Bucket5096"] = {
            "Properties": {
                "BucketName": {"Fn::Select": [1, {"Ref": "AccountIds"}]},
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "Name-5096",
                    },
                ],
            },
            "Type": "AWS::S3::Bucket",
        }
        result["Resources"]["S3Bucketa72a"] = {
            "Properties": {
                "BucketName": {"Fn::Select": [0, {"Ref": "AccountIds"}]},
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "Name-a72a",
                    },
                ],
            },
            "Type": "AWS::S3::Bucket",
        }
        del result["Resources"]["S3Bucketab"]
        del result["Resources"]["S3Bucketcd"]
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
        self.assertTrue(len(template["Resources"]) == 4)
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


class TestTransformValues(TestCase):
    def setUp(self) -> None:
        self.template_obj = convert_dict(
            {
                "Transform": ["AWS::LanguageExtensions"],
                "Mappings": {
                    "111111111111": {
                        "A": {"AppName": "appa-dev"},
                        "B": {"AppName": "appb-dev"},
                    },
                    "222222222222": {
                        "A": {"AppName": "appa-qa"},
                        "B": {"AppName": "appb-qa"},
                    },
                },
                "Resources": {
                    "Fn::ForEach::Regions": [
                        "Region",
                        ["A"],
                        {
                            "${Region}Role": {
                                "Type": "AWS::IAM::Role",
                                "Properties": {
                                    "RoleName": {
                                        "Fn::Sub": [
                                            "${appname}",
                                            {
                                                "appname": {
                                                    "Fn::FindInMap": [
                                                        {"Ref": "AWS::AccountId"},
                                                        {"Ref": "Region"},
                                                        "AppName",
                                                    ]
                                                }
                                            },
                                        ]
                                    },
                                    "AssumeRolePolicyDocument": {
                                        "Version": "2012-10-17",
                                        "Statement": [
                                            {
                                                "Effect": "Allow",
                                                "Principal": {
                                                    "Service": ["ec2.amazonaws.com"]
                                                },
                                                "Action": ["sts:AssumeRole"],
                                            }
                                        ],
                                    },
                                    "Path": "/",
                                },
                            }
                        },
                    ],
                    "Fn::ForEach::NewRegions": [
                        "Region",
                        ["B"],
                        {
                            "${Region}Role": {
                                "Type": "AWS::IAM::Role",
                                "Properties": {
                                    "RoleName": {
                                        "Fn::Sub": [
                                            "${appname}",
                                            {
                                                "appname": {
                                                    "Fn::FindInMap": [
                                                        {"Ref": "AWS::AccountId"},
                                                        {"Ref": "Region"},
                                                        "AppName",
                                                    ]
                                                }
                                            },
                                        ]
                                    },
                                    "AssumeRolePolicyDocument": {
                                        "Version": "2012-10-17",
                                        "Statement": [
                                            {
                                                "Effect": "Allow",
                                                "Principal": {
                                                    "Service": ["ec2.amazonaws.com"]
                                                },
                                                "Action": ["sts:AssumeRole"],
                                            }
                                        ],
                                    },
                                    "Path": "/",
                                },
                            }
                        },
                    ],
                },
            }
        )

        self.result = {
            "Mappings": {
                "111111111111": {
                    "A": {"AppName": "appa-dev"},
                    "B": {"AppName": "appb-dev"},
                },
                "222222222222": {
                    "A": {"AppName": "appa-qa"},
                    "B": {"AppName": "appb-qa"},
                },
            },
            "Resources": {
                "ARole": {
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Statement": [
                                {
                                    "Action": ["sts:AssumeRole"],
                                    "Effect": "Allow",
                                    "Principal": {"Service": ["ec2.amazonaws.com"]},
                                }
                            ],
                            "Version": "2012-10-17",
                        },
                        "Path": "/",
                        "RoleName": {
                            "Fn::Sub": ["${appname}", {"appname": "appa-dev"}]
                        },
                    },
                    "Type": "AWS::IAM::Role",
                },
                "BRole": {
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Statement": [
                                {
                                    "Action": ["sts:AssumeRole"],
                                    "Effect": "Allow",
                                    "Principal": {"Service": ["ec2.amazonaws.com"]},
                                }
                            ],
                            "Version": "2012-10-17",
                        },
                        "Path": "/",
                        "RoleName": {
                            "Fn::Sub": ["${appname}", {"appname": "appb-dev"}]
                        },
                    },
                    "Type": "AWS::IAM::Role",
                },
            },
            "Transform": ["AWS::LanguageExtensions"],
        }

    def test_transform(self):
        self.maxDiff = None
        cfn = Template(filename="", template=self.template_obj, regions=["us-east-1"])
        matches, template = language_extension(cfn)
        self.assertListEqual(matches, [])
        self.assertDictEqual(
            template,
            self.result,
            template,
        )


def nested_set(dic, keys, value):
    for key in keys[:-1]:
        if isinstance(key, str):
            dic = dic.setdefault(key, {})
        if isinstance(key, int):
            dic = dic[key]
    dic[keys[-1]] = value
