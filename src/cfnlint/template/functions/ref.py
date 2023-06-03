from typing import Any, Iterable, List

from cfnlint.template.functions.exceptions import Unpredictable
from cfnlint.template.functions.fn import Fn


class Ref(Fn):
    def __init__(self, instance: Any, template: Any = None) -> None:
        super().__init__(instance)
        self._supported_functions: List[str] = []
        if not isinstance(self._instance, str):
            return

        self._value = instance
        self._account_id = "123456789012"

    @property
    def is_valid(self) -> bool:
        if not isinstance(self._instance, str):
            return False
        return True

    def _get_aws_partition(self, region: str) -> str:
        if region in ("us-gov-east-1", "us-gov-west-1"):
            return "aws-us-gov"
        if region in ("cn-north-1", "cn-northwest-1"):
            return "aws-cn"
        else:
            return "aws"

    def _get_url_suffix(self, region: str) -> str:
        if region in ("cn-north-1", "cn-northwest-1"):
            return "amazonaws.com.cn"

        return "amazonaws.com"

    def get_value(self, fns, region: str) -> Iterable[Any]:
        if not self.is_valid:
            raise Unpredictable(f"Ref is not valid {self._instance!r}")

        if self._value == "AWS::Region":
            yield region
            return

        if self._value == "AWS::AccountId":
            yield self._account_id
            return

        if self._value == "AWS::NotificationARNs":
            yield [
                f"arn:{self._get_aws_partition(region)}:sns:{region}:{self._account_id}:notification"
            ]
            return

        if self._value == "AWS::NoValue":
            return

        if self._value == "AWS::Partition":
            yield self._get_aws_partition(region)
            return

        if self._value == "AWS::StackId":
            yield (
                f"arn:{self._get_aws_partition(region)}:cloudformation:"
                f"{region}:{self._account_id}:"
                "stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"
            )
            return

        if self._value == "AWS::StackName":
            yield "teststack"
            return

        if self._value == "AWS::URLSuffix":
            yield self._get_url_suffix(region)
            return
