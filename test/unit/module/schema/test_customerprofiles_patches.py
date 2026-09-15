"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path

import regex

from cfnlint.schema._schema import Schema


def test_customerprofiles_integration_schedule_expression_patch():
    schema = Schema(
        {
            "typeName": "AWS::CustomerProfiles::Integration",
            "definitions": {
                "ScheduledTriggerProperties": {
                    "properties": {
                        "ScheduleExpression": {
                            "pattern": ".*",
                            "type": "string",
                        }
                    }
                }
            },
        }
    )
    patch = Path(
        "src/cfnlint/data/schemas/patches/extensions/all/"
        "aws_customerprofiles_integration/smithy.json"
    )

    schema.patch(json.loads(patch.read_text(encoding="utf-8")))

    pattern = schema.schema["definitions"]["ScheduledTriggerProperties"]["properties"][
        "ScheduleExpression"
    ]["pattern"]

    for value in ["rate(5minutes)", "RATE(15MINUTES)", "rate(1hours)", "RATE(1DAYS)"]:
        assert regex.search(pattern, value)

    for value in [
        "rate(1 day)",
        "rate(30minutes)",
        "cron(0 6 * * ? *)",
        "rate(1days)\n",
    ]:
        assert not regex.search(pattern, value)
