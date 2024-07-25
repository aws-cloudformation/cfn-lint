"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Iterator


def _get_new_status_message(
    current_status: dict[str, bool], new_status: dict[str, bool]
) -> Iterator[str]:
    for k, v in new_status.items():
        if v is not None:
            if current_status.get(k) is not None and current_status.get(k) != v:
                yield (
                    f"condition {k!r} to {v!r} from current "
                    f"status {current_status.get(k)!r}"
                )
            else:
                yield f"condition {k!r} to {v!r}"


def _get_current_status_message(
    current_status: dict[str, bool], new_status: dict[str, bool]
) -> Iterator[str]:
    for k, v in current_status.items():
        if v is not None and k not in new_status:
            yield f"condition {k!r} is {v!r}"


def _build_message(current_status: dict[str, bool], new_status: dict[str, bool]) -> str:
    message = ", and ".join(_get_new_status_message(current_status, new_status))

    current_message = " and ".join(
        _get_current_status_message(current_status, new_status)
    )

    if current_message:
        message += f". Where existing status for {current_message}"

    return f"When setting {message}"


class Unsatisfiable(ValueError):

    def __init__(
        self,
        new_status: dict[str, bool],
        current_status: dict[str, bool],
    ) -> None:
        message = _build_message(current_status, new_status)
        super().__init__(message)
        self.message = message
        self.current_status = current_status
        self.new_status = new_status

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.message!r}>"
