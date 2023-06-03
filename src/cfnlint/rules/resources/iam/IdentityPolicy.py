"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import (
    CfnTemplateValidator,
    RefResolver,
    StandardValidator,
    ValidationError,
)
from cfnlint.jsonschema.exceptions import best_match
from cfnlint.rules.jsonschema.base import BaseJsonSchema


class _BestOf:
    def _match_longer_path(self, error):
        return len(error.path)

    def oneOf(self, validator, oO, instance, schema):
        subschemas = enumerate(oO)
        all_errors = []
        for index, subschema in subschemas:
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                first_valid = subschema
                break
            all_errors.extend(errs)
        else:
            best_err = best_match(all_errors, key=self._match_longer_path)
            schema_path = best_err.schema_path[0]
            for err in all_errors:
                if err.schema_path[0] == schema_path:
                    yield err

        more_valid = [
            each
            for _, each in subschemas
            if validator.evolve(schema=each).is_valid(instance)
        ]
        if more_valid:
            more_valid.append(first_valid)
            reprs = ", ".join(repr(schema) for schema in more_valid)
            yield ValidationError(f"{instance!r} is valid under each of {reprs}")

    # pylint: disable=unused-argument
    def anyOf(self, validator, aO, instance, schema):
        all_errors = []
        for index, subschema in enumerate(aO):
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                break
            all_errors.extend(errs)
        else:
            best_err = best_match(all_errors, key=self._match_longer_path)
            yield best_err


class IdentityPolicy(BaseJsonSchema):
    """Check IAM identity Policies"""

    id = "E3510"
    shortdesc = "Validate identity based IAM polices"
    description = (
        "IAM identity polices are embedded JSON in CloudFormation. "
        "This rule validates those embedded policies."
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["parameters", "availabilityzone"]

    def __init__(self):
        super().__init__()
        self.cfn = None
        self.validators = {
            "anyOf": _BestOf().anyOf,
            "oneOf": _BestOf().oneOf,
        }
        policy_schema = load_resource("cfnlint.data.schemas.other.iam", "policy.json")
        self.identity_schema = load_resource(
            "cfnlint.data.schemas.other.iam", "policy_identity.json"
        )
        store = {
            "policy": policy_schema,
            "identity": self.identity_schema,
        }
        # To reduce reduntant schemas use a schema resolver
        # this is deprecated in 4.18 of jsonschema
        self.resolver = RefResolver.from_schema(self.identity_schema, store=store)

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    # pylint: disable=unused-argument
    def iamidentitypolicy(self, validator, policy_type, policy, schema):
        # First time child rules are configured against the rule
        # so we can run this now

        if validator.is_type(policy, "string"):
            try:
                validator = StandardValidator
                policy = json.loads(policy)
            except json.JSONDecodeError:
                return
        elif validator.is_type(policy, "object"):
            validator = CfnTemplateValidator

        iam_validator = self.setup_validator(
            validator=validator,
            schema=self.identity_schema,
        ).evolve(resolver=self.resolver)

        for err in iam_validator.iter_errors(policy):
            err.rule = self
            yield err
