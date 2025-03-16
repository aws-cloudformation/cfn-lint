"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os
import subprocess

import cfnlint
import cfnlint.data.AdditionalSpecs
from cfnlint.helpers import get_url_content
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER

LOGGER = logging.getLogger(__name__)

REGISTRY_SCHEMA_ZIP = (
    "https://schema.cloudformation.us-east-1.amazonaws.com/CloudformationSchema.zip"
)


def update_resource_specs(force: bool = False):
    # Pool() uses cpu count if no number of processors is specified
    # Pool() only implements the Context Manager protocol from Python3.3 onwards,
    # so it will fail Python2.7 style linting, as well as throw AttributeError

    # Update provider Schemas
    PROVIDER_SCHEMA_MANAGER.update(force)


def patch_resource_specs():
    # Pool() uses cpu count if no number of processors is specified
    # Pool() only implements the Context Manager protocol from Python3.3 onwards,
    # so it will fail Python2.7 style linting, as well as throw AttributeError

    # Update provider Schemas
    PROVIDER_SCHEMA_MANAGER.patch_schemas()


def update_documentation(rules):
    # Update the overview of all rules in the linter
    filename = "docs/rules.md"

    # Sort rules by the Rule ID
    sorted_rules = sorted(rules.values(), key=lambda obj: obj.id)
    data = []

    # Read current file up to the Rules part, everything up to that point is
    # static documentation.
    with open(filename, "r", encoding="utf-8") as original_file:
        line = original_file.readline()
        while line:
            data.append(line)

            if line == "## Rules\n":
                break

            line = original_file.readline()

    # Rebuild the file content
    with open(filename, "w", encoding="utf-8") as new_file:
        # Rewrite the static documentation
        for line in data:
            new_file.write(line)

        # Add the rules
        new_file.write(
            "(_This documentation is generated by running `cfn-lint"
            " --update-documentation`, do not alter this manually_)\n\n"
        )
        new_file.write(
            f"The following **{len(sorted_rules) + 3}** rules are applied by this"
            " linter:\n\n"
        )
        new_file.write(
            "| Rule ID  | Title | Description | Config<br />(Name:Type:Default) |"
            " Source | Tags |\n"
        )
        new_file.write(
            "| -------- | ----- | ----------- | ---------- | ------ | ---- |\n"
        )

        rule_output = (
            '| [{0}<a name="{0}"></a>]({6}) | {1} | {2} | {3} | [Source]({4}) | {5} |\n'
        )

        for rule in sorted_rules:
            rule_source_code_file = (
                "../"
                + subprocess.check_output(
                    [
                        "git",
                        "grep",
                        "-l",
                        'id = "' + rule.id + '"',
                        "src/cfnlint/rules/",
                    ]
                )
                .decode("ascii")
                .strip()
            )
            rule_id = rule.id + "*" if rule.experimental else rule.id
            tags = ",".join(f"`{tag}`" for tag in rule.tags)
            config = "<br />".join(
                f'{key}:{values.get("type")}:{values.get("default")}'
                for key, values in rule.config_definition.items()
            )
            new_file.write(
                rule_output.format(
                    rule_id,
                    rule.shortdesc,
                    rule.description,
                    config,
                    rule.source_url,
                    tags,
                    rule_source_code_file,
                )
            )
        new_file.write("\n\\* experimental rules\n")


def update_iam_policies():
    """update iam policies file"""

    url = "https://servicereference.us-east-1.amazonaws.com"

    filename = os.path.join(
        os.path.dirname(cfnlint.data.AdditionalSpecs.__file__), "Policies.json"
    )
    LOGGER.debug("Downloading policies %s into %s", url, filename)

    services = json.loads(get_url_content(url))

    def _clean_arn_formats(arn):
        arn_parts = arn.split(":", 5)

        resource = arn_parts[5]
        delimiter = None
        for d in [":", "/"]:
            if d in resource:
                delimiter = d

        if delimiter:
            resource_parts = []
            for resource_part in resource.split(delimiter):
                if "${" in resource_part:
                    resource_parts.append(".*")
                    break

                resource_parts.append(resource_part)

            arn_parts[5] = delimiter.join(resource_parts)

        return ":".join(arn_parts)

    def _processes_a_service(data):
        results = {
            "Actions": {},
            "Resources": {},
        }

        for action in data.get("Actions", []):
            results["Actions"][action.get("Name").lower()] = {}
            if "Resources" in action:
                results["Actions"][action.get("Name").lower()] = {
                    "Resources": list([i["Name"] for i in action["Resources"]])
                }

        for resource in data.get("Resources", []):
            results["Resources"][resource.get("Name").lower()] = {
                "ARNFormats": [
                    _clean_arn_formats(arn) for arn in resource.get("ARNFormats")
                ],
            }
            if "ConditionKeys" in resource:
                results["Resources"][resource.get("Name").lower()]["ConditionKeys"] = (
                    resource.get("ConditionKeys")
                )

        return results

    data = {}
    for service in services:
        name = service.get("service")
        content = json.loads(get_url_content(service.get("url")))
        data[name] = _processes_a_service(content)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True, separators=(",", ": "))
        f.write("\n")
