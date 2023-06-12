import unittest

from cfnlint.context import Value, ValueType
from cfnlint.template.functions import Ref
from cfnlint.template.functions.exceptions import Unpredictable


class TestRef(unittest.TestCase):
    def test_ref_pseudo(self):
        ref = Ref("AWS::Region", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [Value(value="us-east-1", value_type=ValueType.PSEUDO_PARAMETER)],
        )

        ref = Ref("AWS::AccountId", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [Value(value="123456789012", value_type=ValueType.PSEUDO_PARAMETER)],
        )

        ref = Ref("AWS::NotificationARNs", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [
                Value(
                    value=["arn:aws:sns:us-east-1:123456789012:notification"],
                    value_type=ValueType.PSEUDO_PARAMETER,
                )
            ],
        )

        ref = Ref("AWS::NoValue", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), [])

        ref = Ref("AWS::Partition", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [Value(value="aws", value_type=ValueType.PSEUDO_PARAMETER)],
        )
        self.assertListEqual(
            list(ref.get_value(None, "us-gov-east-1")),
            [Value(value="aws-us-gov", value_type=ValueType.PSEUDO_PARAMETER)],
        )
        self.assertListEqual(
            list(ref.get_value(None, "cn-north-1")),
            [Value(value="aws-cn", value_type=ValueType.PSEUDO_PARAMETER)],
        )

        ref = Ref("AWS::StackId", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [
                Value(
                    value="arn:aws:cloudformation:us-east-1:123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123",
                    value_type=ValueType.PSEUDO_PARAMETER,
                )
            ],
        )

        ref = Ref("AWS::StackName", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [Value(value="teststack", value_type=ValueType.PSEUDO_PARAMETER)],
        )

        ref = Ref("AWS::URLSuffix", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [Value(value="amazonaws.com", value_type=ValueType.PSEUDO_PARAMETER)],
        )
        self.assertListEqual(
            list(ref.get_value(None, "cn-north-1")),
            [Value(value="amazonaws.com.cn", value_type=ValueType.PSEUDO_PARAMETER)],
        )

    def test_ref_invalid(self):
        # dict
        ref = Ref({"Foo": "Bar"})
        self.assertFalse(ref.is_valid)

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(ref.get_value(None, "us-east-1"))
