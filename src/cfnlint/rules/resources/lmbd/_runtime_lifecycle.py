"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any


def deprecated_message(runtime: str, runtime_data: dict[str, Any]) -> str:
    create_block = runtime_data["create-block"]
    update_block = runtime_data["update-block"]

    if create_block and update_block:
        blocks = (
            f"Creation was disabled on {create_block!r} and update on {update_block!r}."
        )
    elif create_block:
        blocks = (
            f"Creation was disabled on {create_block!r} and update blocking is "
            "not yet scheduled."
        )
    elif update_block:
        blocks = (
            "Creation blocking is not yet scheduled and update was disabled on "
            f"{update_block!r}."
        )
    else:
        blocks = "Creation and update blocking are not yet scheduled."

    return (
        f"Runtime {runtime!r} was deprecated on "
        f"{runtime_data['deprecated']!r}. {blocks} "
        f"Please consider updating to {runtime_data['successor']!r}"
    )
