"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import List

from cfnlint.formatters.base import BaseFormatter
from cfnlint.match import Match
from cfnlint.rules import Rules
from cfnlint.version import __version__

Matches = List[Match]


class SARIFFormatter(BaseFormatter):
    """
    SARIF formatter

    This formatter outputs results according to the Static Analysis Results
    Interchange Format (SARIF) Version 2.1.0.

    https://docs.oasis-open.org/sarif/sarif/v2.1.0/csprd01/sarif-v2.1.0-csprd01.html
    """

    schema = "https://docs.oasis-open.org/sarif/sarif/v2.1.0/cos02/schemas/sarif-schema-2.1.0.json"
    version = "2.1.0"

    # The spec defines error, note, warning, and none, see section 3.27.10.
    levelMap = {
        "error": "error",
        "informational": "note",
        "warning": "warning",
    }

    uri_base_id = "EXECUTIONROOT"

    def _to_sarif_level(self, severity):
        return self.levelMap.get(severity, "none")

    def print_matches(self, matches, rules, config):
        """Output all the matches"""

        try:
            import sarif_om as sarif
            from jschema_to_python.to_json import to_json
        except ImportError as e:
            raise ImportError("Missing optional dependencies sarif") from e

        if not rules:
            rules = Rules()

        results = []
        for match in matches:
            results.append(
                sarif.Result(
                    rule_id=match.rule.id,
                    message=sarif.Message(text=match.message),
                    level=self._to_sarif_level(match.rule.severity),
                    locations=[
                        sarif.Location(
                            physical_location=sarif.PhysicalLocation(
                                artifact_location=sarif.ArtifactLocation(
                                    uri=match.filename,
                                    uri_base_id=self.uri_base_id,
                                ),
                                region=sarif.Region(
                                    start_column=match.columnnumber,
                                    start_line=match.linenumber,
                                    end_column=match.columnnumberend,
                                    end_line=match.linenumberend,
                                ),
                            )
                        )
                    ],
                )
            )

        # Output only the rules that have matches
        matched_rules = set(r.rule_id for r in results)

        rules = [
            sarif.ReportingDescriptor(
                id=rule_id,
                short_description=sarif.MultiformatMessageString(
                    text=rules[rule_id].shortdesc
                ),
                full_description=sarif.MultiformatMessageString(
                    text=rules[rule_id].description
                ),
                help_uri=(
                    rules[rule_id].source_url
                    if rules[rule_id]
                    else "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md"
                ),
            )
            for rule_id in matched_rules
        ]

        run = sarif.Run(
            tool=sarif.Tool(
                driver=sarif.ToolComponent(
                    name="cfn-lint",
                    short_description=sarif.MultiformatMessageString(
                        text=(
                            "Validates AWS CloudFormation templates against"
                            " the resource specification and additional"
                            " checks."
                        )
                    ),
                    information_uri="https://github.com/aws-cloudformation/cfn-lint",
                    rules=rules,
                    version=__version__,
                ),
            ),
            original_uri_base_ids={
                self.uri_base_id: sarif.ArtifactLocation(
                    description=sarif.MultiformatMessageString(
                        "The directory in which cfn-lint was run."
                    )
                )
            },
            results=results,
        )

        log = sarif.SarifLog(version=self.version, schema_uri=self.schema, runs=[run])

        # IMPORTANT: 'warning' is the default level in SARIF and will be
        # stripped by serialization.
        return to_json(log)
