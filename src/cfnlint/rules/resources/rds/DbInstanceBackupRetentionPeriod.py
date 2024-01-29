"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema



class DbInstanceBackupRetentionPeriod(CfnLintJsonSchema):
    id = "E3683"
    shortdesc = "Check RDS DB instances with auto expiring content have explicit retention period"
    description = (
        "The behaviour for data retention is different across AWS Services.If no"
        " retention period is specified the default for some services is to delete the"
        " data after a period of time.This check requires you to explicitly set the"
        " retention period for those resources to avoid unexpected data losses"
    )
    tags = ["resources", "retentionperiod", "rds"]
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"

    def __init__(self) -> None:
        super().__init__(keywords=["aws_rds_dbinstance/backupretentionperiod"])

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message

    def validate(self, validator, instance):
        # We can't support functions in this schema check as it can be valid
        # but we don't know the values
        validator = validator.evolve(context=validator.context.evolve(functions=[]))
        yield from super().validate(validator, instance)

    

