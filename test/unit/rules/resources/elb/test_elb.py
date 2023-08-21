"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.elb.Elb import Elb  # pylint: disable=E0401


class TestPropertyElb(BaseRuleTestCase):
    """Test Elb Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyElb, self).setUp()
        self.collection.register(Elb())
        self.success_templates = [
            "test/fixtures/templates/good/resources/elb/properties.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/elb/properties.yaml", 6
        )

    def test_alb_subnets(self):
        """Test ALB Subnet Logic"""
        rule = Elb()

        # Failure when 1 subnet defined
        props = {"Subnets": ["subnet-123456"]}

        matches = rule.check_alb_subnets(props, ["Resources", "ALB", "Properties"], {})
        self.assertEqual(len(matches), 1)

        # No Failure when 2 subnets defined
        props = {"Type": "application", "Subnets": ["subnet-123456", "subnet-abcdef"]}

        matches = rule.check_alb_subnets(props, ["Resources", "ALB", "Properties"], {})
        self.assertEqual(len(matches), 0)

        # Failure when 1 SubnetMapping defined
        props = {
            "Type": "application",
            "SubnetMappings": [{"SubnetId": "subnet-123456"}],
        }

        matches = rule.check_alb_subnets(props, ["Resources", "ALB", "Properties"], {})
        self.assertEqual(len(matches), 1)

        # No Failure when 2 SubnetMapping defined
        props = {
            "Type": "application",
            "SubnetMappings": [
                {"SubnetId": "subnet-123456"},
                {"SubnetId": "subnet-abcdef"},
            ],
        }

        matches = rule.check_alb_subnets(props, ["Resources", "ALB", "Properties"], {})
        self.assertEqual(len(matches), 0)

        # No Failure when 1 Subnet and NLB
        props = {"Type": "network", "Subnets": ["subnet-123456"]}

        matches = rule.check_alb_subnets(props, ["Resources", "NLB", "Properties"], {})
        self.assertEqual(len(matches), 0)

    def test_loadbalancer_attributes(self):
        """Test LoadBalancer Attributes logic"""
        rule = Elb()

        props = {"Type": "network"}

        elb_type = rule.get_loadbalancer_type(props)
        self.assertEqual(elb_type, "network")

        props = {"Type": "application"}

        elb_type = rule.get_loadbalancer_type(props)
        self.assertEqual(elb_type, "application")

        props = {}

        elb_type = rule.get_loadbalancer_type(props)
        self.assertEqual(elb_type, "application")

        props = {"Type": {"Ref": "LoadBalancerType"}}

        elb_type = rule.get_loadbalancer_type(props)
        self.assertEqual(elb_type, None)
