"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from jsonschema import RefResolver
from jsonschema.exceptions import best_match
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.BaseJsonSchema import BaseJsonSchema

from cfnlint.helpers import load_resource


class IdentityPolicy(BaseJsonSchema):
    """Check IAM identity Policies"""

    id = "E3510"
    shortdesc = "Validate identity based IAM polices"
    description = "IAM identity polices are embedded JSON in CloudFormation. This rule validates those embedded policies."
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["parameters", "availabilityzone"]

    def __init__(self):
        super().__init__()
        self.cfn = None
        self.validators = {
            "anyOf": self._any_of,
            "oneOf": self._one_of,
        }
        policy_schema = load_resource("cfnlint.data.schemas.nested", "iam_policy.json")
        self.identity_schema = load_resource(
            "cfnlint.data.schemas.nested", "iam_policy_identity.json"
        )
        store = {
            "policy": policy_schema,
            "identity": self.identity_schema,
        }
        self.resolver = RefResolver.from_schema(self.identity_schema, store=store)

    def initialize(self, cfn):
        self.cfn = cfn
        return super().initialize(cfn)

    def _match_longer_path(self, error):
        return len(error.path)

    def _one_of(self, validator, oO, instance, schema):
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
            yield best_err

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
    def _any_of(self, validator, aO, instance, schema):
        all_errors = []
        for index, subschema in enumerate(aO):
            errs = list(validator.descend(instance, subschema, schema_path=index))
            if not errs:
                break
            all_errors.extend(errs)
        else:
            best_err = best_match(all_errors, key=self._match_longer_path)
            yield best_err

    # pylint: disable=unused-argument
    def iamidentitypolicy(self, validator, _, policy, schema):
        # First time child rules are configured against the rule
        # so we can run this now
        self.setup_validator(
            cfn=self.cfn,
        )

        if isinstance(policy, str):
            try:
                policy = json.loads(policy)
            except Exception:
                return
        cfn_validator = self.validator(self.identity_schema, resolver=self.resolver)

        for err in cfn_validator.iter_errors(policy):
            err.rule = self
            yield err
