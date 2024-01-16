"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import FUNCTIONS
from cfnlint.rules import CloudFormationLintRule


class Export(CloudFormationLintRule):
    """Check if Output Export values"""

    id = "E6102"
    shortdesc = "Outputs have values of strings"
    description = "Making sure the outputs have strings as values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def cfnoutputexport(self, validator, tS, instance, schema):
        validator = validator.evolve(
            context=validator.context.evolve(
                resources={},
                functions=FUNCTIONS,
            )
        )

        for err in validator.descend(instance, {"type": "string"}):
            if not err.validator.startswith("fn"):
                err.rule = self
            yield err
