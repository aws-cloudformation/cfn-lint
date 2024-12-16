"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, runtime_checkable

from cfnlint.jsonschema._filter import FunctionFilter

if TYPE_CHECKING:
    from cfnlint.context import Context


@runtime_checkable
class DeploymentFilePlugin(Protocol):
    """
    The protocol to which all deployment file plugin classes adhere.

    Arguments:

    """
