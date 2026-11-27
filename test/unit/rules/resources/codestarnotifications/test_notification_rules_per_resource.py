"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase
from unittest.mock import patch

from cfnlint.decode.decode import decode_str
from cfnlint.rules.resources.codestarnotifications.NotificationRulesPerResource import (  # noqa: E501
    NotificationRulesPerResource,
)
from cfnlint.template import Template


class TestNotificationRulesPerResource(BaseRuleTestCase):
    """Test the number of notification rules for a resource"""

    def setUp(self):
        """Setup"""
        super().setUp()
        self.collection.register(NotificationRulesPerResource())
        self.success_templates = [
            "test/fixtures/templates/good/resources/codestarnotifications/notification_rules_per_resource.yaml",  # noqa: E501
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/codestarnotifications/notification_rules_per_resource.yaml",  # noqa: E501
            1,
        )


def _template(
    count: int, extra: str = "", condition: str = "", head: str = ""
) -> Template:
    rules = "".join(
        f"""
  Rule{i}:
    Type: AWS::CodeStarNotifications::NotificationRule{condition if i == 0 else ""}
    Properties:
      Resource: arn:aws:codebuild:us-east-1:123456789012:project/build
"""
        for i in range(count)
    )
    tpl, _ = decode_str(f"{head}Resources:{rules}{extra}")
    return Template("", tpl, ["us-east-1"])


def test_limit():
    rule = NotificationRulesPerResource()
    assert rule.match(_template(10)) == []
    matches = rule.match(_template(11))
    assert len(matches) == 1
    assert matches[0].path == ["Resources", "Rule10", "Properties", "Resource"]
    assert matches[0].message.startswith("Up to 11 notification rules")


def test_bad_shapes_are_ignored():
    extra = """
  NoProperties:
    Type: AWS::CodeStarNotifications::NotificationRule
    Properties: []
  NoResource:
    Type: AWS::CodeStarNotifications::NotificationRule
    Properties: {}
"""
    assert NotificationRulesPerResource().match(_template(10, extra)) == []


def test_condition_that_is_not_a_string_is_skipped():
    condition = "\n    Condition: [Bad]"
    assert NotificationRulesPerResource().match(_template(11, "", condition)) == []


def test_too_many_scenarios_is_skipped():
    head = "Conditions:\n  IsProd: !Equals [!Ref AWS::Region, us-east-1]\n"
    tpl = _template(11, "", "\n    Condition: IsProd", head)
    with patch(
        "cfnlint.rules.resources.codestarnotifications."
        "NotificationRulesPerResource._MAX_SCENARIOS",
        0,
    ):
        assert NotificationRulesPerResource().match(tpl) == []
