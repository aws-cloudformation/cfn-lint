"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class OnlyOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""

    id = "E2523"
    shortdesc = "Check Properties that need only one of a list of properties"
    description = (
        "Making sure CloudFormation properties "
        + "that require only one property from a list. "
        + "One has to be specified."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def oneOf(self, validator, oneOf, instance, schema):
        subschemas = enumerate(oneOf)
        all_errors = []
        for index, subschema in subschemas:
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                first_valid = subschema
                break
            all_errors.extend(errs)
        else:
            yield ValidationError(
                f"{instance!r} is not valid under any of the given schemas",
                context=all_errors,
            )

        more_valid = [
            each
            for _, each in subschemas
            if validator.evolve(schema=each).is_valid(instance)
        ]
        if more_valid:
            more_valid.append(first_valid)
            reprs = ", ".join(repr(schema) for schema in more_valid)
            yield ValidationError(f"{instance!r} is valid under each of {reprs}")
