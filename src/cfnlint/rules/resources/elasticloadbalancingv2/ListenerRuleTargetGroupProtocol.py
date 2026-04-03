"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_listenerrule
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ListenerRuleTargetGroupProtocol(CfnLintJsonSchema):
    id = "E3711"
    shortdesc = "Validate ListenerRule target group protocol is not GENEVE"
    description = (
        "When a ListenerRule forwards to a TargetGroup, the TargetGroup "
        "protocol must not be GENEVE. GENEVE is only supported with "
        "Gateway Load Balancers, not Application or Network Load Balancers."
    )
    source_url = "https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/target-groups.html"
    tags = ["resources", "elasticloadbalancingv2"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ElasticLoadBalancingV2::ListenerRule/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_listenerrule,
                filename="listener_rule_target_group_protocol.json",
            ),
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "TargetGroup protocol 'GENEVE' is not compatible with "
            "ListenerRule forwarding actions. GENEVE is only supported "
            "with Gateway Load Balancers."
        )

    def _clean_error(self, err: ValidationError) -> ValidationError:
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
