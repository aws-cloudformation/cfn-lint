"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule, RuleMatch


@dataclass(frozen=True, eq=True)
class Match:
    """
    Represents a match found by a CloudFormationLintRule.

    Attributes:
        linenumber (int): The line number where the match was found.
        columnnumber (int): The column number where the match was found.
        linenumberend (int): The ending line number of the match.
        columnnumberend (int): The ending column number of the match.
        filename (str): The name of the file where the match was found.
        rule (CloudFormationLintRule): The rule that found the match.
        message (str): The message associated with the match.
        id (str): A unique identifier for the match.
        parent_id (str): The ID of the parent match,
            if this match is a child of another.

    Methods:
        create(message: str, filename: str, rule: CloudFormationLintRule,
            linenumber: int = None, columnnumber: int = None,
            linenumberend: int = None, columnnumberend: int = None,
            rulematch_obj: RuleMatch = None, parent_id: str = None) -> Match:
            Factory method to create a new Match instance.

    """

    message: str = field(init=True)
    rule: CloudFormationLintRule = field(init=True)
    filename: str | None = field(init=True, default=None)
    linenumber: int = field(init=True, default=1)
    columnnumber: int = field(init=True, default=1)
    linenumberend: int = field(init=True, default=1)
    columnnumberend: int = field(init=True, default=1)
    id: str = field(init=False)
    parent_id: str | None = field(init=True, default=None)
    rulematch_obj: InitVar[RuleMatch | None] = None

    def __post_init__(self, rulematch_obj):
        hex_string = hashlib.md5(
            f"{self}".encode("UTF-8"), usedforsecurity=False
        ).hexdigest()
        super().__setattr__("id", str(uuid.UUID(hex=hex_string)))

        if rulematch_obj:
            for k, v in vars(rulematch_obj).items():
                if not hasattr(self, k):
                    super().__setattr__(k, v)

    def __repr__(self):
        # use the Posix path to keep things consistent across platforms
        file_str = Path(self.filename).as_posix() + ":" if self.filename else ""
        return f"[{self.rule}] ({self.message}) matched {file_str}{self.linenumber}"

    @classmethod
    def create(
        cls,
        message: str,
        filename: str,
        rule: CloudFormationLintRule,
        linenumber: int | None = None,
        columnnumber: int | None = None,
        linenumberend: int | None = None,
        columnnumberend: int | None = None,
        rulematch_obj: RuleMatch | None = None,
        parent_id: str | None = None,
    ) -> "Match":
        """
        Factory method to create a new Match instance.

        Args:
            message (str): The message associated with the match.
            filename (str): The name of the file where the match was found.
            rule (CloudFormationLintRule): The rule that found the match.
            linenumber (int, optional): The line number where the match
                was found.
            columnnumber (int, optional): The column number where the
                match was found.
            linenumberend (int, optional): The ending line number of
                the match.
            columnnumberend (int, optional): The ending column number of
                the match.
            rulematch_obj (RuleMatch, optional): The RuleMatch object that
                generated this Match.
            parent_id (str, optional): The ID of the parent match, if this
                match is a child of another.

        Returns:
            Match: A new Match instance.
        """

        if columnnumber is None:
            columnnumber = 1
        if columnnumberend is None:
            columnnumberend = columnnumber + 1
        if linenumber is None:
            linenumber = 1
        if linenumberend is None:
            linenumberend = linenumber

        return cls(
            linenumber=linenumber,
            columnnumber=columnnumber,
            linenumberend=linenumberend,
            columnnumberend=columnnumberend,
            filename=filename,
            rule=rule,
            message=message,
            rulematch_obj=rulematch_obj,
            parent_id=parent_id,
        )
