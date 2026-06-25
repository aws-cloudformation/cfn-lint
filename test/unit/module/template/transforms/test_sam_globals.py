"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.template.transforms._sam_globals import merge_globals


class TestMerge:
    def test_dict_merge(self):
        template = {
            "Globals": {"Function": {"Environment": {"Variables": {"A": "1"}}}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Environment": {"Variables": {"B": "2"}},
                    },
                }
            },
        }
        merge_globals(template)
        env = template["Resources"]["Fn"]["Properties"]["Environment"]["Variables"]
        assert env == {"A": "1", "B": "2"}

    def test_list_concat(self):
        template = {
            "Globals": {"Function": {"Layers": ["arn:layer1"]}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Layers": ["arn:layer2"]},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Layers"] == [
            "arn:layer1",
            "arn:layer2",
        ]

    def test_local_overrides_primitive(self):
        template = {
            "Globals": {"Function": {"Runtime": "python3.9"}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Runtime": "python3.12"},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Runtime"] == "python3.12"

    def test_intrinsic_local_wins(self):
        template = {
            "Globals": {"Function": {"Timeout": 30}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Timeout": {"Ref": "Param"}},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Timeout"] == {"Ref": "Param"}

    def test_intrinsic_global_replaced_by_local(self):
        template = {
            "Globals": {
                "Function": {"Environment": {"Fn::If": ["Cond", {"A": "1"}, {}]}}
            },
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Environment": {"Variables": {"B": "2"}}},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Environment"] == {
            "Variables": {"B": "2"}
        }

    def test_type_mismatch_local_wins(self):
        template = {
            "Globals": {"Function": {"Tags": {"Key": "Val"}}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Tags": "override"},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Tags"] == "override"

    def test_ignore_globals_star(self):
        template = {
            "Globals": {"Function": {"Runtime": "python3.9", "Timeout": 30}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "IgnoreGlobals": "*",
                    "Properties": {},
                }
            },
        }
        merge_globals(template)
        assert "Runtime" not in template["Resources"]["Fn"]["Properties"]

    def test_ignore_globals_list(self):
        template = {
            "Globals": {"Function": {"Runtime": "python3.9", "Timeout": 30}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "IgnoreGlobals": ["Runtime"],
                    "Properties": {},
                }
            },
        }
        merge_globals(template)
        props = template["Resources"]["Fn"]["Properties"]
        assert "Runtime" not in props
        assert props["Timeout"] == 30

    def test_no_globals_section(self):
        template = {
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Runtime": "python3.12"},
                }
            }
        }
        result = merge_globals(template)
        assert result is template

    def test_globals_not_dict(self):
        template = {"Globals": "invalid", "Resources": {}}
        result = merge_globals(template)
        assert result is template

    def test_resources_not_dict(self):
        template = {"Globals": {"Function": {"Runtime": "python3.9"}}}
        result = merge_globals(template)
        assert result is template

    def test_non_dict_resource_skipped(self):
        template = {
            "Globals": {"Function": {"Runtime": "python3.9"}},
            "Resources": {"Bad": "not-a-dict"},
        }
        merge_globals(template)
        assert template["Resources"]["Bad"] == "not-a-dict"

    def test_no_local_properties(self):
        template = {
            "Globals": {"Function": {"Runtime": "python3.9"}},
            "Resources": {
                "Fn": {"Type": "AWS::Serverless::Function"},
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Runtime"] == "python3.9"

    def test_unknown_globals_section_ignored(self):
        template = {
            "Globals": {"Unknown": {"Foo": "bar"}},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Runtime": "python3.12"},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Runtime"] == "python3.12"

    def test_non_dict_globals_props_ignored(self):
        template = {
            "Globals": {"Function": "not-a-dict"},
            "Resources": {
                "Fn": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {"Runtime": "python3.12"},
                }
            },
        }
        merge_globals(template)
        assert template["Resources"]["Fn"]["Properties"]["Runtime"] == "python3.12"

    def test_api_globals(self):
        template = {
            "Globals": {"Api": {"TracingEnabled": True}},
            "Resources": {
                "MyApi": {
                    "Type": "AWS::Serverless::Api",
                    "Properties": {"StageName": "prod"},
                }
            },
        }
        merge_globals(template)
        props = template["Resources"]["MyApi"]["Properties"]
        assert props["TracingEnabled"] is True
        assert props["StageName"] == "prod"
