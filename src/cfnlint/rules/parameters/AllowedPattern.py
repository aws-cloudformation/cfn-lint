"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Generator, Iterable

import regex as re

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.template import Template


class AllowedPattern(CloudFormationLintRule):
    """Check if parameters have a valid value"""

    id = "W2031"
    shortdesc = "Check if parameters have a valid value based on an allowed pattern"
    description = "Check if parameters have a valid value in a pattern. The Parameter's allowed pattern is based on the usages in property (Ref)"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern"
    tags = ["parameters", "resources", "property", "allowed pattern"]

    def __init__(self):
        super().__init__()
        self.parameters = {}

    def initialize(self, cfn: Template):
        """Initialize the rule"""
        self.parameters = cfn.get_parameters()

    def _pattern(
        self, instance: str, patrn: str, path: Iterable[str]
    ) -> Generator[ValidationError]:
        if not re.search(patrn, instance):
            yield ValidationError(
                f"{instance!r} does not match {patrn!r}",
                rule=self,
                path_override=path,
            )

    def validate(self, ref: str, patrn: str):
        p = self.parameters.get(ref, {})
        if isinstance(p, dict):
            p_default = p.get("Default", None)
            if isinstance(p_default, (str)):
                yield from self._pattern(
                    p_default, patrn, ["Parameters", ref, "Default"]
                )

            p_avs = p.get("AllowedValues", [])
            if isinstance(p_avs, list):
                for p_av_index, p_av in enumerate(p_avs):
                    yield from self._pattern(
                        p_av, patrn, ["Parameters", ref, "AllowedValues", p_av_index]
                    )
