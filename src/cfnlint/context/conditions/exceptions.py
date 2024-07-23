"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations


class Unsatisfiable(ValueError):

    def __init__(
        self,
        message: str,
        name: str,
        value: bool | None,
        condition_status: dict[str, bool],
    ) -> None:
        super().__init__(message)
        self.message = message
        self.name = name
        self.value = value
        self.conditions_status = condition_status

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.message!r}>"
