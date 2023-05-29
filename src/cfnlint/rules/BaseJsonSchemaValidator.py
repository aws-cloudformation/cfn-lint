"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generator, Optional

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule

LOGGER = logging.getLogger("cfnlint.rules.JsonSchema")


# missing kwargs argument
V = Callable[[Any, Any, Any, Dict[str, Any]], Generator[ValidationError, None, None]]


# to help with rule writing and type hinting
@dataclass
class Validators:  # pylint: disable=too-many-instance-attributes
    Value: V
    Ref: Optional[V] = None
    GetAtt: Optional[V] = None
    Base64: Optional[V] = None
    GetAZs: Optional[V] = None
    ImportValue: Optional[V] = None
    Join: Optional[V] = None
    Split: Optional[V] = None
    FindInMap: Optional[V] = None
    Select: Optional[V] = None
    If: Optional[V] = None
    Contains: Optional[V] = None
    Sub: Optional[V] = None
    Cidr: Optional[V] = None
    Length: Optional[V] = None
    ToJsonString: Optional[V] = None


class BaseJsonSchemaValidator(CloudFormationLintRule):
    """The base JSON schema validator package to handle
    cloudformation functions
    """

    def __init__(self) -> None:
        """Init"""
        super().__init__()
        self.validators: Validators = Validators(
            Value=self.validate_value,
            Ref=self.validate_ref,
            GetAtt=self.validate_getatt,
            Base64=self.validate_base64,
            GetAZs=self.validate_getazs,
            ImportValue=self.validate_importvalue,
            Join=self.validate_join,
            Split=self.validate_split,
            FindInMap=self.validate_findinmap,
            Select=self.validate_select,
            If=self.validate_if,
            Sub=self.validate_sub,
            Cidr=self.validate_cidr,
            Length=self.validate_length,
            ToJsonString=self.validate_tojsonstring,
        )

    # pylint: disable=unused-argument
    def validate_value(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_ref(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_getatt(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_base64(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_getazs(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_importvalue(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_join(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_split(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_findinmap(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_select(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    def validate_if(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        if validator.is_type(instance, "array") and len(instance) == 3:
            yield from self.validate_instance(
                validator, s, instance[1], schema, **kwargs
            )
            yield from self.validate_instance(
                validator, s, instance[2], schema, **kwargs
            )

    # pylint: disable=unused-argument
    def validate_sub(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_cidr(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_length(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    # pylint: disable=unused-argument
    def validate_tojsonstring(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        return
        yield  # pragma: no cover

    def validate_instance(
        self,
        validator: Any,
        s: Any,
        instance: Any,
        schema: Dict[str, Any],
        **kwargs,
    ) -> Generator[ValidationError, None, None]:
        """Takes an instance and removes possible functions calling validation
        functions as needed.

        Args:
            validator (Any): This is the JSON Schema Validator
            s (Any): The sub schema being validated
            instance (Any): The instance being evaluated
            schema (Dict[str, Any]): The JSON Schema being validated
            **kwargs (Any): Additional values to pass to validation functions and
              additional functions for doing validation.
        Returns:
            yields ValidationErrors
        """

        if isinstance(instance, dict):
            if len(instance) == 1:
                for k, v in instance.items():
                    # If this is a function we shouldn't fall
                    # back to a check_value check
                    if k in FUNCTIONS:
                        # convert the function name from camel case to underscore
                        # Example: Fn::FindInMap becomes check_find_in_map
                        function_name = k.replace("Fn::", "")
                        yield from getattr(self.validators, function_name)(
                            validator,
                            s,
                            v,
                            schema,
                            original_instance=instance,
                            **kwargs,
                        )
                        return

        yield from self.validators.Value(validator, s, instance, schema, **kwargs)
