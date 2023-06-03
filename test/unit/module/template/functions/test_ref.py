import unittest

from cfnlint.template.functions import Ref
from cfnlint.template.functions.exceptions import Unpredictable


class TestRef(unittest.TestCase):
    def test_ref_pseudo(self):
        ref = Ref("AWS::Region", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), ["us-east-1"])

        ref = Ref("AWS::AccountId", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), ["123456789012"])

        ref = Ref("AWS::NotificationARNs", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [["arn:aws:sns:us-east-1:123456789012:notification"]],
        )

        ref = Ref("AWS::NoValue", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), [])

        ref = Ref("AWS::Partition", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), ["aws"])
        self.assertListEqual(list(ref.get_value(None, "us-gov-east-1")), ["aws-us-gov"])
        self.assertListEqual(list(ref.get_value(None, "cn-north-1")), ["aws-cn"])

        ref = Ref("AWS::StackId", None)
        self.assertListEqual(
            list(ref.get_value(None, "us-east-1")),
            [
                "arn:aws:cloudformation:us-east-1:123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
            ],
        )

        ref = Ref("AWS::StackName", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), ["teststack"])

        ref = Ref("AWS::URLSuffix", None)
        self.assertListEqual(list(ref.get_value(None, "us-east-1")), ["amazonaws.com"])
        self.assertListEqual(
            list(ref.get_value(None, "cn-north-1")), ["amazonaws.com.cn"]
        )

    def test_ref_invalid(self):
        # dict
        ref = Ref({"Foo": "Bar"})
        self.assertFalse(ref.is_valid)

        # invalid should raise unpredictable
        with self.assertRaises(Unpredictable):
            list(ref.get_value(None, "us-east-1"))
