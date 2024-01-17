"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules import CloudFormationLintRule


class Value(CloudFormationLintRule):
    """Check if Outputs have string values"""

    id = "E6101"
    shortdesc = "Outputs have values of strings"
    description = "Making sure the outputs have strings as values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def cfnoutputvalue(self, validator, tS, instance, schema):
        validator = validator.extend(
            context=validator.context.evolve(
                functions=FUNCTIONS,
            ),
        )({"type": "string"})

        for err in validator.iter_errors(instance):
            if not err.validator.startswith("fn"):
                err.rule_override = self
            yield err

    # pylint: disable=unused-argument
    def _type(self, validator, types, instance, schema):
        yield from cfn_type(validator, types, instance, schema, False)
