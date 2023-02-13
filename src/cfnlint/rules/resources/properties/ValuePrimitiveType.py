"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, List

from cfnlint.helpers import FUNCTIONS, FUNCTIONS_MULTIPLE
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.template.template import Template


class ValuePrimitiveType(CloudFormationLintRule):
    """Check if Resource PrimitiveTypes are correct"""

    id = "E3012"
    shortdesc = "Check resource properties values"
    description = "Checks resource property values with Primitive Types for values that match those types."
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#valueprimitivetype"
    tags = ["resources"]

    strict_exceptions = {
        "AWS::CloudFormation::Stack": ["Parameters"],
        "AWS::Lambda::Function.Environment": ["Variables"],
    }

    def __init__(self):
        """Init"""
        super().__init__()
        self.config_definition = {
            "strict": {"default": False, "type": "boolean"},
        }
        self.configure()
        self.cfn = None

    # pylint: disable=too-many-return-statements
    def _schema_value_check(
        self, value: Any, item_type: str, strict_check: bool
    ) -> bool:
        """Checks non strict"""
        if not strict_check:
            try:
                if item_type in ["string"]:
                    return isinstance(value, (str, bool, int, float))
                if item_type in ["boolean"]:
                    if value not in ["True", "true", "False", "false"]:
                        return False
                elif item_type in ["integer", "number"]:
                    if isinstance(value, bool):
                        return False
                    if item_type in ["integer"]:
                        int(value)
                    else:  # has to be a Double
                        float(value)
                else:
                    return False
            except Exception:  # pylint: disable=W0703
                return False
        else:
            return False

        return True

    def _schema_check_primitive_type(self, value: Any, types: List[str]) -> bool:
        """Chec item type"""
        strict_check = self.config.get("strict")
        result = False
        for t in types:
            if t == "string":
                if not isinstance(value, (str)):
                    if self._schema_value_check(value, "string", strict_check):
                        result = True
                else:
                    result = True
            elif t == "boolean":
                if not isinstance(value, (bool)):
                    if self._schema_value_check(value, "boolean", strict_check):
                        result = True
                else:
                    result = True
            elif t == "number":
                if not isinstance(value, (float, int)) or isinstance(value, (bool)):
                    if self._schema_value_check(value, "number", strict_check):
                        result = True
                else:
                    result = True
            elif t == "integer":
                # bool is an int in python
                if not isinstance(value, (int)) or isinstance(value, (bool)):
                    if self._schema_value_check(value, "integer", strict_check):
                        result = True
                else:
                    result = True
            elif isinstance(value, list):
                if self._schema_value_check(value, "list", strict_check):
                    result = True

        return result

    def validate_configure(self, cfn: Template):
        self.cfn = cfn

    # pylint: disable=unused-argument
    def type(self, validator, types, instance, schema):
        types = ensure_list(types)
        reprs = ", ".join(repr(type) for type in types)
        if not any(validator.is_type(instance, type) for type in types):
            if isinstance(instance, dict):
                if len(instance) == 1:
                    for k, v in instance.items():
                        # Most conditions should be eliminated but sometimes they trickle through because
                        # of different issues including a person providing a condition name that doesn't exist
                        if k == "Fn::If":
                            if len(v) == 3:
                                for i in range(1, 3):
                                    for v_err in self.type(
                                        validator=validator,
                                        types=types,
                                        instance=v[i],
                                        schema=schema,
                                    ):
                                        v_err.path.append("Fn::If")
                                        v_err.path.append(i)
                                        yield v_err
                            return
                        if k == "Ref":
                            valid_refs = self.cfn.get_valid_refs()
                            for t in types:
                                if t == "array":
                                    if v in valid_refs:
                                        ref_type = valid_refs.get(v).get("Type")
                                        if "List" in ref_type:
                                            return
                                elif t in ["string", "number", "integer", "boolean"]:
                                    if v in valid_refs:
                                        ref_type = valid_refs.get(v).get("Type")
                                        if "List" not in ref_type:
                                            return
                            if v not in valid_refs:
                                # Picked up by another rule
                                return
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                            return
                        if k in FUNCTIONS_MULTIPLE:
                            for t in types:
                                if t == "array":
                                    return
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                            return
                        if k in FUNCTIONS:
                            for t in types:
                                if t in ["string", "integer", "boolean"]:
                                    return
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                            return
                        yield ValidationError(
                            f"{instance!r} is not of type {reprs}", extra_args={}
                        )
                        return
            if not self._schema_check_primitive_type(instance, types):
                extra_args = {
                    "actual_type": type(instance).__name__,
                    "expected_type": reprs,
                }
                yield ValidationError(
                    f"{instance!r} is not of type {reprs}", extra_args=extra_args
                )


def ensure_list(thing):
    """
    Wrap ``thing`` in a list if it's a single str.
    Otherwise, return it unchanged.
    """

    if isinstance(thing, str):
        return [thing]
    return thing
