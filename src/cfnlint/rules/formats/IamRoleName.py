"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class IamRoleName(FormatKeyword):
    id = "E1165"
    shortdesc = "Validate IAM role name format"
    description = "Validate IAM role name format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::IAM::Role.Name"

    def __init__(self):
        # The optional leading group is the IAM ``Path`` spec
        # ``(\u002F)|(\u002F[\u0021-\u007E]+\u002F)`` and the trailing part is
        # the IAM ``RoleName`` spec ``[\w+=,.@-]{1,64}``, because the accepting
        # APIs take the path and the name concatenated. Printable ASCII includes
        # ``/``, so nested paths match too.
        #
        # ``\w`` is spelled out in ASCII on purpose: it is Unicode-aware in
        # Python but ASCII-only in ECMA-262, and these patterns are consumed by
        # both. See ``test_iam_role_name.py`` for the equivalence test.
        super().__init__(
            format="AWS::IAM::Role.Name",
            pattern=r"^(/[!-~]+/)?[a-zA-Z0-9_+=,.@-]{1,64}$",
        )
