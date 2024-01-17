"""
Copyright (c) 2013 Julian Berman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

SPDX-License-Identifier: MIT
"""
# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/python-jsonschema/jsonschema
from typing import Any, Callable, Deque, Dict, Iterator, Optional, Tuple

from cfnlint.jsonschema.exceptions import ValidationError

ValidationResult = Iterator[ValidationError]
V = Optional[Callable[[Any, Any, Any, Dict[str, Any]], ValidationResult]]
ResolutionResult = Iterator[Tuple[Any, Deque]]
