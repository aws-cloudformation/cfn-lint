from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.ToJsonString import ToJsonString


class TestRulesToJsonString(BaseRuleTestCase):
    def setUp(self):
        super(TestRulesToJsonString, self).setUp()
        self.collection.register(ToJsonString())
        self.success_templates = [
            "test/fixtures/templates/good/functions/toJsonString.yaml"
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/toJsonString.yaml", 3
        )

    def test_file_negative_missing_transform(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/toJsonStringWithoutTransform.yaml", 1
        )
