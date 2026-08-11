"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.resources.GlobalsTransform import GlobalsTransform
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    yield GlobalsTransform()


@pytest.mark.parametrize(
    "name,instance,template,path,expected",
    [
        (
            "Valid globals with transform",
            {"Function": {"Runtime": "python3.12"}},
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            0,
        ),
        (
            "Globals without transform",
            {"Function": {"Runtime": "python3.12"}},
            {},
            {"cfn_path": deque(["Globals"])},
            1,
        ),
        (
            "Non-dict instance",
            "not-a-dict",
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            0,
        ),
        (
            "Invalid globals property",
            {"Function": {"Runtime": "python3.12"}, "InvalidKey": {}},
            {"Transform": ["AWS::Serverless-2016-10-31"]},
            {"cfn_path": deque(["Globals"])},
            1,
        ),
    ],
    indirect=["template", "path"],
)
def test_validate_globals(name, instance, template, path, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    assert len(errors) == expected, f"Test {name!r} got {errors!r}"


class TestIgnoreGlobalsMatch:
    """Test IgnoreGlobals validation via match method."""

    def test_valid_ignore_globals(self, rule):
        """Valid IgnoreGlobals entry should produce no matches."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30, "Runtime": "python3.12"}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Timeout"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_wildcard(self, rule):
        """IgnoreGlobals: '*' should always be valid."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": "*",
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_typo(self, rule):
        """Typo in IgnoreGlobals should produce a match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Timeot"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 1
        assert "'Timeot' is not a valid global property" in matches[0].message
        assert matches[0].path == ["Resources", "MyFunction", "IgnoreGlobals", 0]

    def test_ignore_globals_multiple_entries_mixed(self, rule):
        """Multiple entries with one invalid should produce one match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30, "Runtime": "python3.12"}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["InvalidKey", "Runtime"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 1
        assert "'InvalidKey' is not a valid global property" in matches[0].message
        assert matches[0].path == ["Resources", "MyFunction", "IgnoreGlobals", 0]

    def test_ignore_globals_no_matching_globals_section(self, rule):
        """No Globals for resource type should produce no match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Api": {"TracingEnabled": True}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Timeout"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_for_api_resource(self, rule):
        """Valid IgnoreGlobals for Api resource should produce no match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Api": {"TracingEnabled": True}},
                "Resources": {
                    "MyApi": {
                        "Type": "AWS::Serverless::Api",
                        "IgnoreGlobals": ["TracingEnabled"],
                        "Properties": {"StageName": "prod"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_for_api_with_typo(self, rule):
        """Typo in IgnoreGlobals for Api resource should produce a match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Api": {"TracingEnabled": True}},
                "Resources": {
                    "MyApi": {
                        "Type": "AWS::Serverless::Api",
                        "IgnoreGlobals": ["TracingEnable"],
                        "Properties": {"StageName": "prod"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 1
        assert "'TracingEnable' is not a valid global property" in matches[0].message

    def test_ignore_globals_without_sam_transform(self, rule):
        """No SAM transform means no IgnoreGlobals validation."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["InvalidKey"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_non_sam_resource(self, rule):
        """Non-SAM resource types should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Lambda::Function",
                        "IgnoreGlobals": ["InvalidKey"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_intrinsic_entry(self, rule):
        """Intrinsic function entry in IgnoreGlobals should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": [{"Ref": "SomeParam"}],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_http_api(self, rule):
        """Valid IgnoreGlobals for HttpApi should produce no match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"HttpApi": {"Auth": {}}},
                "Resources": {
                    "MyHttpApi": {
                        "Type": "AWS::Serverless::HttpApi",
                        "IgnoreGlobals": ["Auth"],
                        "Properties": {},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_globals_not_dict(self, rule):
        """Globals section not a dict should produce no match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": "not-a-dict",
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Timeout"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_multiple_resources(self, rule):
        """Multiple resources with invalid IgnoreGlobals produce multiple matches."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "Func1": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Typo1"],
                        "Properties": {"Handler": "index.handler"},
                    },
                    "Func2": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Typo2"],
                        "Properties": {"Handler": "index.handler"},
                    },
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 2

    def test_ignore_globals_globals_section_is_intrinsic(self, rule):
        """Globals section that is an intrinsic should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Fn::If": ["Cond", {"Function": {"Timeout": 30}}, {}]},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["InvalidKey"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_resources_not_dict(self, rule):
        """Resources section not a dict should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": "not-a-dict",
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_resource_not_dict(self, rule):
        """Resource that is not a dict should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": "not-a-dict",
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_resource_type_not_string(self, rule):
        """Resource Type not a string should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": {"Ref": "SomeParam"},
                        "IgnoreGlobals": ["InvalidKey"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_global_props_is_intrinsic(self, rule):
        """Global props for resource type that is an intrinsic should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Fn::If": ["Cond", {"Timeout": 30}, {}]}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["InvalidKey"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_entry_not_string(self, rule):
        """IgnoreGlobals entry that is not a string (e.g. number) should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": [123, "Timeout"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        # Only the number entry is skipped; "Timeout" is valid so no error
        assert len(matches) == 0

    def test_ignore_globals_missing_globals_section(self, rule):
        """Missing Globals section should produce no match."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": ["Timeout"],
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_ignore_globals_not_list_or_wildcard(self, rule):
        """IgnoreGlobals that is not a list and not '*' should be skipped."""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Globals": {"Function": {"Timeout": 30}},
                "Resources": {
                    "MyFunction": {
                        "Type": "AWS::Serverless::Function",
                        "IgnoreGlobals": "Timeout",  # string but not "*"
                        "Properties": {"Handler": "index.handler"},
                    }
                },
            },
            ["us-east-1"],
        )
        matches = rule.match(template)
        assert len(matches) == 0
