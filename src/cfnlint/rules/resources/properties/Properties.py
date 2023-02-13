"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class Properties(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = "E3002"
    shortdesc = "Resource properties are invalid"
    description = "Making sure that resources properties are properly configured"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#properties"
    tags = ["resources"]

    # pylint: disable=unused-argument
    def properties(self, validator, properties, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        if len(instance) == 1:
            for k, v in instance.items():
                if k != "Fn::If":
                    break
                if not isinstance(v, list):
                    break
                if len(v) == 3:
                    yield from validator.descend(
                        v[0],
                        schema,
                        path=k[0] if len(k) > 0 else "Fn::If",
                        schema_path=None,
                    )
                    yield from validator.descend(
                        v[1],
                        schema,
                        path=k[0] if len(k) > 0 else "Fn::If",
                        schema_path=None,
                    )
                return

        for p, subschema in properties.items():
            # use the instance keys because it gives us the start_mark
            k = [k for k in instance.keys() if k == p]
            if p in instance:
                yield from validator.descend(
                    instance[p],
                    subschema,
                    path=k[0] if len(k) > 0 else p,
                    schema_path=p,
                )

    def _find_additional_properties(self, instance, schema):
        """
        Return the set of additional properties for the given ``instance``.
        Weeds out properties that should have been validated by ``properties`` and
        / or ``patternProperties``.
        Assumes ``instance`` is dict-like already.
        """

        properties = schema.get("properties", {})
        patterns = "|".join(schema.get("patternProperties", {}))
        for p in instance:
            if p not in properties:
                if patterns and re.search(patterns, p):
                    continue
                yield p

    def additionalProperties(self, validator, aP, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        extras = set(self._find_additional_properties(instance, schema))

        if validator.is_type(aP, "object"):
            for extra in extras:
                yield from validator.descend(instance[extra], aP, path=extra)
        elif not aP and extras:
            if "patternProperties" in schema:
                if len(extras) == 1:
                    verb = "does"
                else:
                    verb = "do"

                joined = ", ".join(repr(each) for each in sorted(extras))
                patterns = ", ".join(
                    repr(each) for each in sorted(schema["patternProperties"])
                )
                error = f"{joined} {verb} not match any of the regexes: {patterns}"
                yield ValidationError(error)
            else:
                for extra in extras:
                    error = "Additional properties are not allowed (%s unexpected)"
                    yield ValidationError(error % extra, path=[extra])
