"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceSourceDBInstanceIdentifier(CfnLintJsonSchema):
    id = "W3692"
    shortdesc = "When using a source DB instance certain properties are ignored"
    description = (
        "When creating a DB instance read replica from a source DB instance "
        "certain properties are ignored and inherited from the source, "
        "which could result in drift"
    )
    tags = ["resources", "rds"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html#cfn-rds-dbinstance-sourcedbinstanceidentifier"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="sourcedbinstanceidentifier.json",
            ),
            # The warning is per property, so every ignored property needs
            # its own error instead of only the best match.
            all_matches=True,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        prop = err.path[0] if err.path else "property"
        return (
            f"{prop!r} is ignored on a read replica and inherited "
            "from the source DB instance"
        )

    def _clean_error(self, err: ValidationError) -> ValidationError:
        # all_matches=True surfaces every ignored property, but it bypasses
        # message(), leaving the raw "False schema does not allow ..."
        # text. Apply the per-property message to each error instead.
        err = super()._clean_error(err)
        if err.rule == self:
            err.message = self.message(None, err)
        return err
