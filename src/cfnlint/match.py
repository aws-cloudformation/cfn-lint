"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


class Match:
    """Match Classes"""

    def __init__(
        self,
        linenumber,
        columnnumber,
        linenumberend,
        columnnumberend,
        filename,
        rule,
        message=None,
        rulematch_obj=None,
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
        """Name of the filename associated with this match, or None if there is no such file"""
        self.rule = rule
        """The rule of this match"""
        self.message = message  # or rule.shortdesc
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
