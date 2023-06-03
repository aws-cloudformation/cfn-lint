"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.properties.AvailabilityZone import (
    AvailabilityZone,  # pylint: disable=E0401
)


class TestAvailabilityZone(BaseRuleTestCase):
    """Test Password Property Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = AvailabilityZone()

    def test_availability_zones(self):
        validator = CfnTemplateValidator({})

        # hard coded string
        self.assertEqual(
            len(list(self.rule.availabilityzones(validator, {}, ["us-east-1"], {}))), 1
        )

        # proper function
        self.assertEqual(
            len(
                list(
                    self.rule.availabilityzones(
                        validator, {}, {"Fn::GetAZs": "us-east-1"}, {}
                    )
                )
            ),
            0,
        )

        # not a string
        self.assertEqual(
            len(list(self.rule.availabilityzones(validator, {}, True, {}))), 0
        )

        # not a string
        self.assertEqual(
            len(
                list(
                    self.rule.availabilityzones(
                        validator, {}, [{"Ref": "Parameter"}], {}
                    )
                )
            ),
            0,
        )

        # exception
        self.assertEqual(
            len(list(self.rule.availabilityzones(validator, {}, ["all"], {}))), 0
        )

        # more than 1
        self.assertEqual(
            len(
                list(
                    self.rule.availabilityzones(
                        validator, {}, ["us-east-1", "us-west-2"], {}
                    )
                )
            ),
            2,
        )
