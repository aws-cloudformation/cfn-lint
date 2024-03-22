"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import hashlib
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cfnlint.rules import CloudFormationLintRule, RuleMatch


class Match:
    """Match Classes"""

    def __init__(
        self,
        linenumber: int,
        columnnumber: int,
        linenumberend: int,
        columnnumberend: int,
        filename: str,
        rule: CloudFormationLintRule,
        message=None,
        rulematch_obj=None,
        parent_id=None,
    ):
        """Init"""
        self.linenumber = linenumber
        """Starting line number of the region this match spans"""
        self.columnnumber = columnnumber
        """Starting line number of the region this match spans"""
        self.linenumberend = linenumberend
        """Ending line number of the region this match spans"""
        self.columnnumberend = columnnumberend
        """Ending column number of the region this match spans"""
        self.filename = filename
        """Name of the filename associated with this match, or
          None if there is no such file"""
        self.rule = rule
        """The rule of this match"""
        self.message = message  # or rule.shortdesc

        hex_string = hashlib.md5(f"{self}".encode("UTF-8")).hexdigest()
        self.id: str = str(uuid.UUID(hex=hex_string))

        self.parent_id = parent_id
        """The message of this match"""
        if rulematch_obj:
            for k, v in vars(rulematch_obj).items():
                if not hasattr(self, k):
                    setattr(self, k, v)

    def __repr__(self):
        """Represent"""
        file_str = self.filename + ":" if self.filename else ""
        return f"[{self.rule}] ({self.message}) matched {file_str}{self.linenumber}"

    def __eq__(self, item):
        """Override equal to compare matches"""
        return (self.linenumber, self.columnnumber, self.rule.id, self.message) == (
            item.linenumber,
            item.columnnumber,
            item.rule.id,
            item.message,
        )

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
        if columnnumber is None:
            columnnumber = 1
        if columnnumberend is None:
            columnnumberend = columnnumber + 1
        if linenumber is None:
            linenumber = 1
        if linenumberend is None:
            linenumberend = linenumber

        return Match(
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
