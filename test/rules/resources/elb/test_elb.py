"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules.resources.elb.Elb import Elb  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestPropertyElb(BaseRuleTestCase):
    """Test Elb Property Configuration"""
    def setUp(self):
        """Setup"""
        super(TestPropertyElb, self).setUp()
        self.collection.register(Elb())
        self.success_templates = [
            'test/fixtures/templates/good/properties_elb.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_elb.yaml', 7)

    def test_alb_subnets(self):
        """ Test ALB Subnet Logic"""
        rule = Elb()

        # Failure when 1 subnet defined
        props = {
            "Subnets": [
                "subnet-123456"
            ]
        }

        matches = rule.check_alb_subnets(props, ['Resources', 'ALB', 'Properties'])
        self.assertEqual(len(matches), 1)

        # No Failure when 2 subnets defined
        props = {
            "Type": "application",
            "Subnets": [
                "subnet-123456",
                "subnet-abcdef"
            ]
        }

        matches = rule.check_alb_subnets(props, ['Resources', 'ALB', 'Properties'])
        self.assertEqual(len(matches), 0)

        # Failure when 1 SubnetMapping defined
        props = {
            "Type": "application",
            "SubnetMappings": [
                {
                    "SubnetId": "subnet-123456"
                }
            ]
        }

        matches = rule.check_alb_subnets(props, ['Resources', 'ALB', 'Properties'])
        self.assertEqual(len(matches), 1)

        # No Failure when 2 SubnetMapping defined
        props = {
            "Type": "application",
            "SubnetMappings": [
                {"SubnetId": "subnet-123456"},
                {"SubnetId": "subnet-abcdef"}
            ]
        }

        matches = rule.check_alb_subnets(props, ['Resources', 'ALB', 'Properties'])
        self.assertEqual(len(matches), 0)

        # No Failure when 1 Subnet and NLB
        props = {
            "Type": "network",
            "Subnets": [
                "subnet-123456"
            ]
        }

        matches = rule.check_alb_subnets(props, ['Resources', 'NLB', 'Properties'])
        self.assertEqual(len(matches), 0)

    def test_loadbalancer_attributes(self):
        """ Test LoadBalancer Attributes logic """
        rule = Elb()

        props = {
            "Type": "network",
            "LoadBalancerAttributes": [
                {
                    "Key": "load_balancing.cross_zone.enabled",
                    "Value": "true"
                }
            ]
        }

        matches = rule.check_loadbalancer_allowed_attributes(props, ['Resources', 'NLB', 'Properties'])
        self.assertEqual(len(matches), 0)

        props = {
            "LoadBalancerAttributes": [
                {
                    "Key": "idle_timeout.timeout_seconds",
                    "Value": 60
                },
                {
                    "Key": "routing.http2.enabled",
                    "Value": "true"
                }
            ]
        }

        matches = rule.check_loadbalancer_allowed_attributes(props, ['Resources', 'ALB', 'Properties'])
        self.assertEqual(len(matches), 0)

        props = {
            "Type": "network",
            "LoadBalancerAttributes": [
                {
                    "Key": "idle_timeout.timeout_seconds",
                    "Value": 60
                },
                {
                    "Key": "routing.http2.enabled",
                    "Value": "true"
                }
            ]
        }

        matches = rule.check_loadbalancer_allowed_attributes(props, ['Resources', 'NLB', 'Properties'])
        self.assertEqual(len(matches), 2)



