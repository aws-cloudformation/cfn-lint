"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from typing import Any, Callable, Dict, Iterator, Optional

from cfnlint.jsonschema.exceptions import ValidationError

V = Optional[Callable[[Any, Any, Any, Dict[str, Any]], Iterator[ValidationError]]]
