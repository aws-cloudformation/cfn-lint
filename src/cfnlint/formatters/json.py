"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

from cfnlint.formatters.base import BaseFormatter
from cfnlint.rules import Match


class JsonFormatter(BaseFormatter):
    """Json Formatter"""

    class CustomEncoder(json.JSONEncoder):
        """Custom Encoding for the Match Object"""

        # pylint: disable=E0202

        def default(self, o):
            if isinstance(o, Match):
                return {
                    "Id": o.id,
                    "ParentId": o.parent_id,
                    "Rule": {
                        "Id": o.rule.id,
                        "Description": o.rule.description,
                        "ShortDescription": o.rule.shortdesc,
                        "Source": o.rule.source_url,
                    },
                    "Location": {
                        "Start": {
                            "ColumnNumber": o.columnnumber,
                            "LineNumber": o.linenumber,
                        },
                        "End": {
                            "ColumnNumber": o.columnnumberend,
                            "LineNumber": o.linenumberend,
                        },
                        "Path": getattr(o, "path", None),
                    },
                    "Level": o.rule.severity.capitalize(),
                    "Message": o.message,
                    "Filename": o.filename,
                }
            return {f"__{o.__class__.__name__}__": o.__dict__}

    def print_matches(self, matches, rules, config):
        # JSON formatter outputs a single JSON object
        # Unused argument http://pylint-messages.wikidot.com/messages:w0613
        del rules

        return json.dumps(
            list(matches),
            indent=4,
            cls=self.CustomEncoder,
            sort_keys=True,
            separators=(",", ": "),
        )
