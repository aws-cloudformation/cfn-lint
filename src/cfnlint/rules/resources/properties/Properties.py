"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from collections import deque
from typing import Any

from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.helpers import FUNCTIONS, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER

LOGGER = logging.getLogger(__name__)

# Properties that an AWS::RDS::DBInstance read replica silently ignores,
# inheriting the values from the source DB instance instead. The enhanced
# schema expresses these as a hard dependentExcluded error (E3020) when
# SourceDBInstanceIdentifier is set, but setting them is not a deploy
# failure, so they are reported by W3692 at warning severity instead.
_READ_REPLICA_IGNORED_PROPERTIES = frozenset(
    {
        "DBName",
        "MasterUsername",
        "StorageEncrypted",
    }
)


def _is_rds_read_replica_ignored_exclusion(
    resource_type: str, err: ValidationError
) -> bool:
    """Whether a dependentExcluded error covers a property a read replica ignores.

    Only suppresses the exclusion when it is triggered by
    SourceDBInstanceIdentifier on AWS::RDS::DBInstance and the excluded
    property is one a read replica silently ignores (inherited from the
    source). MasterUserPassword and CharacterSetName keep their hard error.
    """
    if resource_type != "AWS::RDS::DBInstance":
        return False
    if err.validator != "dependentExcluded":
        return False
    if not err.path or err.path[-1] not in _READ_REPLICA_IGNORED_PROPERTIES:
        return False
    exclusions = err.validator_value
    if not isinstance(exclusions, dict):
        return False
    if err.path[-1] not in exclusions.get("SourceDBInstanceIdentifier", []):
        return False
    instance = err.instance if isinstance(err.instance, dict) else {}
    return "SourceDBInstanceIdentifier" in instance


class Properties(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3002"
    shortdesc = "Resource properties are invalid"
    description = "Making sure that resources properties are properly configured"
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/cfn-schema-specification.md#properties"
    tags = ["resources"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Resources/*"],
            all_matches=True,
        )
        self.rule_set = {
            "additionalProperties": "E3002",
            "anyOf": "E3017",
            "properties": "E3002",
            "dependentExcluded": "E3020",
            "dependentRequired": "E3021",
            "required": "E3003",
            "requiredOr": "E3058",
            "requiredXor": "E3014",
            "enum": "E3030",
            "enumCaseInsensitive": "E3030",
            "type": "E3012",
            "minLength": "E3033",
            "maxLength": "E3033",
            "uniqueItems": "E3037",
            "maximum": "E3034",
            "minimum": "E3034",
            "exclusiveMaximum": "E3034",
            "exclusiveMinimum": "E3034",
            "maxItems": "E3032",
            "maxUniqueItems": "E3065",
            "minItems": "E3032",
            "pattern": "E3031",
            "prefixItems": "E3008",
            "oneOf": "E3018",
            "cfnLint": "E1101",
            "tagging": "E3024",
            "lifecycle": "E3710",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        resolved_conditions = {}
        if validator.is_type(instance.get("Condition"), "string"):
            resolved_conditions = {instance.get("Condition"): True}

        try:
            conditions = validator.context.conditions.evolve(resolved_conditions)
        except Unsatisfiable:
            # The resource's own condition can never be true (for example
            # `X and not X` over two identical conditions).  Validate without
            # pinning the condition instead of surfacing an E3001 exception,
            # consistent with a statically false condition used directly.
            conditions = validator.context.conditions

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTIONS),
                strict_types=False,
                conditions=conditions,
            ),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            ),
        )

        t = instance.get("Type")
        if not validator.is_type(t, "string"):
            return

        if "Properties" not in instance:
            # assume properties is an empty object
            # this helps with validating if the resource
            # has required properties
            properties = {}
        else:
            # covers if Properties is null
            properties = instance.get("Properties")
        # Properties needs to be an object
        if not validator.is_type(properties, "object"):
            yield ValidationError(
                # Expected an object
                message=f"{properties!r} is not of type object",
                path=deque(["Properties"]),
                rule=self.child_rules.get(self.rule_set.get("type")),  # type: ignore
                validator="type",
            )
            return
        fn_k, fn_v = is_function(properties)
        if fn_k == "Ref" and fn_v == "AWS::NoValue":
            yield ValidationError(
                # Expected an object, received {"Ref":"AWS::NoValue"}
                message=f"{properties!r} is not of type object",
                path=deque(["Properties", fn_k]),
                rule=self.child_rules.get(self.rule_set.get("type")),  # type: ignore
                validator="type",
            )
            return

        for regions, schema in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
            t, validator.context.regions
        ):
            region_validator = validator.evolve(
                context=validator.context.evolve(
                    regions=regions,
                    path=validator.context.path.evolve(
                        cfn_path=deque(["Resources", t, "Properties"]),
                    ).descend(path="Properties"),
                ),
            )

            region_validator = self.extend_validator(
                region_validator, schema.schema, region_validator.context.evolve()
            )
            for err in self._validate(region_validator, properties):
                err.path.appendleft("Properties")
                if _is_rds_read_replica_ignored_exclusion(t, err):
                    # Not a deploy failure: a read replica silently ignores
                    # these properties and inherits them from the source DB
                    # instance. W3692 reports them at warning severity.
                    continue
                yield err
