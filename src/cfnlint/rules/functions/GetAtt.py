"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import re
from typing import Dict, Union

from cfnlint.jsonschema import StandardValidator, ValidationError
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

LOGGER = logging.getLogger("cfnlint")


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""

    id = "E1010"
    shortdesc = "GetAtt validation of parameters"
    description = (
        "Validates that GetAtt parameters are to valid resources and properties of"
        " those resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html"
    tags = ["functions", "getatt"]
