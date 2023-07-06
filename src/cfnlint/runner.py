"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from typing import List, Optional, Sequence, Union

from cfnlint.rules import Match, RulesCollection
from cfnlint.template import Template

LOGGER = logging.getLogger(__name__)


class Runner:
    """Run all the rules"""

    def __init__(
        self,
        rules: RulesCollection,
        filename: Optional[str],
        template: str,
        regions: Sequence[str],
        verbosity=0,
        mandatory_rules: Union[Sequence[str], None] = None,
    ):
        self.rules = rules
        self.filename = filename
        self.verbosity = verbosity
        self.mandatory_rules = mandatory_rules or []
        self.cfn = Template(filename, template, regions)

    def transform(self):
        """Transform logic"""
        matches = self.cfn.transform()
        return matches

    def run(self) -> List[Match]:
        """Run rules"""
        LOGGER.info("Run scan of template %s", self.filename)
        matches = []
        if self.cfn.template is not None:
            matches.extend(self.rules.run(self.filename, self.cfn))
        return self.check_metadata_directives(matches)

    def check_metadata_directives(self, matches: Sequence[Match]) -> List[Match]:
        # uniq the list of incidents and filter out exceptions from the template
        directives = self.cfn.get_directives()
        return_matches: List[Match] = []
        for match in matches:
            if not any(match == u for u in return_matches):
                if match.rule.id not in directives:
                    return_matches.append(match)
                else:
                    for mandatory_rule in self.mandatory_rules:
                        if match.rule.id.startswith(mandatory_rule):
                            return_matches.append(match)
                            break
                    else:
                        for directive in directives.get(match.rule.id):
                            start = directive.get("start")
                            end = directive.get("end")
                            if start[0] < match.linenumber < end[0]:
                                break
                            if (
                                start[0] == match.linenumber
                                and start[1] <= match.columnnumber
                            ):
                                break
                            if (
                                end[0] == match.linenumber
                                and end[1] >= match.columnnumberend
                            ):
                                break
                        else:
                            return_matches.append(match)

        return return_matches
