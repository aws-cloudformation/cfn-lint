"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any, List

import jsonschema

import cfnlint.helpers
from cfnlint.helpers import FUNCTIONS, FUNCTIONS_MULTIPLE
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


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
        self.cfn = None
        self.resource_specs = []
        self.property_specs = []
        self.config_definition = {
            "strict": {"default": False, "type": "boolean"},
            "experimental": {"default": False, "type": "boolean"},
        }
        self.configure()

    def initialize(self, cfn):
        """Initialize the rule"""
        specs = cfnlint.helpers.RESOURCE_SPECS.get(cfn.regions[0])
        self.property_specs = specs.get("PropertyTypes")
        self.resource_specs = specs.get("ResourceTypes")
        for resource_spec in self.resource_specs:
            self.resource_property_types.append(resource_spec)
        for property_spec in self.property_specs:
            self.resource_sub_property_types.append(property_spec)

    def _value_check(self, value, path, item_type, strict_check, extra_args):
        """Checks non strict"""
        matches = []
        if not strict_check:
            try:
                if item_type in ["String"]:
                    str(value)
                elif item_type in ["Boolean"]:
                    if value not in ["True", "true", "False", "false"]:
                        message = f'Property {"/".join(map(str, path))} should be of type {item_type}'
                        matches.append(RuleMatch(path, message, **extra_args))
                elif item_type in ["Integer", "Long", "Double"]:
                    if isinstance(value, bool):
                        message = f'Property {"/".join(map(str, path))} should be of type {item_type}'
                        matches.append(RuleMatch(path, message, **extra_args))
                    elif item_type in ["Integer"]:
                        int(value)
                    elif item_type in ["Long"]:
                        # Some times python will strip the decimals when doing a conversion
                        if isinstance(value, float):
                            message = f'Property {"/".join(map(str, path))} should be of type {item_type}'
                            matches.append(RuleMatch(path, message, **extra_args))
                        int(value)
                    else:  # has to be a Double
                        float(value)
            except Exception:  # pylint: disable=W0703
                message = (
                    f'Property {"/".join(map(str, path))} should be of type {item_type}'
                )
                matches.append(RuleMatch(path, message, **extra_args))
        else:
            message = (
                f'Property {"/".join(map(str, path))} should be of type {item_type}'
            )
            matches.append(RuleMatch(path, message, **extra_args))

        return matches

    def check_primitive_type(self, value, item_type, path, strict_check):
        """Chec item type"""
        matches = []
        if isinstance(value, (dict, list)) and item_type == "Json":
            return matches
        if item_type in ["String"]:
            if not isinstance(value, (str)):
                extra_args = {
                    "actual_type": type(value).__name__,
                    "expected_type": str.__name__,
                }
                matches.extend(
                    self._value_check(value, path, item_type, strict_check, extra_args)
                )
        elif item_type in ["Boolean"]:
            if not isinstance(value, (bool)):
                extra_args = {
                    "actual_type": type(value).__name__,
                    "expected_type": bool.__name__,
                }
                matches.extend(
                    self._value_check(value, path, item_type, strict_check, extra_args)
                )
        elif item_type in ["Double"]:
            if not isinstance(value, (float, int)):
                extra_args = {
                    "actual_type": type(value).__name__,
                    "expected_type": [float.__name__, int.__name__],
                }
                matches.extend(
                    self._value_check(value, path, item_type, strict_check, extra_args)
                )
        elif item_type in ["Integer"]:
            if not isinstance(value, (int)):
                extra_args = {
                    "actual_type": type(value).__name__,
                    "expected_type": int.__name__,
                }
                matches.extend(
                    self._value_check(value, path, item_type, strict_check, extra_args)
                )
        elif item_type in ["Long"]:
            integer_types = (int,)
            if not isinstance(value, integer_types):
                extra_args = {
                    "actual_type": type(value).__name__,
                    "expected_type": " or ".join([x.__name__ for x in integer_types]),
                }
                matches.extend(
                    self._value_check(value, path, item_type, strict_check, extra_args)
                )
        elif isinstance(value, list):
            message = (
                f'Property should be of type {item_type} at {"/".join(map(str, path))}'
            )
            extra_args = {
                "actual_type": type(value).__name__,
                "expected_type": list.__name__,
            }
            matches.append(RuleMatch(path, message, **extra_args))

        return matches

    def check_value(self, value, path, **kwargs):
        """Check Value"""
        matches = []
        primitive_type = kwargs.get("primitive_type", {})
        item_type = kwargs.get("item_type", {})
        strict_check = kwargs.get("non_strict", self.config["strict"])

        if value is None:
            message = f'Property value cannot be null {"/".join(map(str, path))}'
            matches.append(RuleMatch(path, message))
        elif item_type in ["Map"]:
            if isinstance(value, dict):
                for map_key, map_value in value.items():
                    if not isinstance(map_value, dict):
                        matches.extend(
                            self.check_primitive_type(
                                map_value,
                                primitive_type,
                                path + [map_key],
                                strict_check,
                            )
                        )
                    else:
                        # types that represent a singular value (not json)
                        cfnlint.helpers.FUNCTIONS_SINGLE.sort()
                        if primitive_type in ["String", "Boolean", "Integer", "Double"]:
                            if len(map_value) != 1:
                                matches.append(
                                    RuleMatch(
                                        path,
                                        f'Use a valid function [{", ".join(cfnlint.helpers.FUNCTIONS_SINGLE)}] when providing a value of type [{primitive_type}]',
                                    )
                                )
                            else:
                                for k in map_value.keys():
                                    if k not in cfnlint.helpers.FUNCTIONS_SINGLE:
                                        matches.append(
                                            RuleMatch(
                                                path,
                                                f'Use a valid function [{", ".join(cfnlint.helpers.FUNCTIONS_SINGLE)}] when providing a value of type [{primitive_type}]',
                                            )
                                        )
        else:
            # some properties support primitive types and objects
            # skip in the case it could be an object and the value is a object
            if (item_type or primitive_type) and isinstance(value, dict):
                return matches
            matches.extend(
                self.check_primitive_type(value, primitive_type, path, strict_check)
            )

        return matches

    def check(self, cfn, properties, specs, spec_type, path):
        """Check itself"""
        matches = []

        for prop in properties:
            if prop in specs:
                primitive_type = specs.get(prop).get("PrimitiveType")
                if not primitive_type:
                    primitive_type = specs.get(prop).get("PrimitiveItemType")
                if specs.get(prop).get("Type") in ["List", "Map"]:
                    item_type = specs.get(prop).get("Type")
                else:
                    item_type = None
                if primitive_type:
                    strict_check = self.config["strict"]
                    if spec_type in self.strict_exceptions:
                        if prop in self.strict_exceptions[spec_type]:
                            strict_check = False
                    matches.extend(
                        cfn.check_value(
                            properties,
                            prop,
                            path,
                            check_value=self.check_value,
                            primitive_type=primitive_type,
                            item_type=item_type,
                            non_strict=strict_check,
                            pass_if_null=True,
                        )
                    )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        if self.config.get("experimental"):
            return matches

        if self.property_specs.get(property_type, {}).get("Properties"):
            property_specs = self.property_specs.get(property_type, {}).get(
                "Properties", {}
            )
            matches.extend(
                self.check(cfn, properties, property_specs, property_type, path)
            )

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        if self.config.get("experimental"):
            return matches

        resource_specs = self.resource_specs.get(resource_type, {}).get(
            "Properties", {}
        )
        matches.extend(self.check(cfn, properties, resource_specs, resource_type, path))

        return matches

    # pylint: disable=too-many-return-statements
    def _schema_value_check(
        self, value: Any, item_type: str, strict_check: bool
    ) -> bool:
        """Checks non strict"""
        if not strict_check:
            try:
                if item_type in ["string"]:
                    str(value)
                elif item_type in ["boolean"]:
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
    def validate(self, validator, types, instance, schema):
        types = ensure_list(types)
        reprs = ", ".join(repr(type) for type in types)
        if not any(validator.is_type(instance, type) for type in types):
            if isinstance(instance, dict):
                if len(instance) == 1:
                    for k, v in instance.items():
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
                                continue
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                        elif k in FUNCTIONS_MULTIPLE:
                            for t in types:
                                if t == "array":
                                    return
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                        elif k in FUNCTIONS:
                            for t in types:
                                if t in ["string", "integer", "boolane"]:
                                    return
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
                        else:
                            yield ValidationError(
                                f"{instance!r} is not of type {reprs}", extra_args={}
                            )
            if not self._schema_check_primitive_type(instance, types):
                extra_args = {
                    "actual_type": type(instance).__name__,
                    "expected_type": reprs,
                }
                yield ValidationError(
                    f"{instance!r} is not of type {reprs}", extra_args=extra_args
                )


class ValidationError(jsonschema.ValidationError):
    def __init__(self, message, extra_args):
        super().__init__(message)
        self.extra_args = extra_args


def ensure_list(thing):
    """
    Wrap ``thing`` in a list if it's a single str.
    Otherwise, return it unchanged.
    """

    if isinstance(thing, str):
        return [thing]
    return thing
