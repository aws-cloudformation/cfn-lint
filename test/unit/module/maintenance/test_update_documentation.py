"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import call, mock_open, patch

import cfnlint.maintenance
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules

LOGGER = logging.getLogger("cfnlint.maintenance")
LOGGER.addHandler(logging.NullHandler())


class TestUpdateDocumentation(BaseTestCase):
    """Used for Testing Updating the Documentation"""

    TEST_TEXT = """
Regular Text
## Rules
"""

    def test_update_docs(self):
        collection = Rules.create_from_directory(_DEFAULT_RULESDIR + "/errors")
        builtin_module_name = "builtins"

        mo = mock_open(read_data=self.TEST_TEXT)
        mo.return_value.__iter__ = lambda self: self
        mo.return_value.__iter__ = lambda self: iter(self.readline, "")
        with patch("{}.open".format(builtin_module_name), mo) as mock_builtin_open:
            cfnlint.maintenance.update_documentation(collection)

            expected_calls = [
                call("\n"),
                call("Regular Text\n"),
                call("## Rules\n"),
                call(
                    "(_This documentation is generated by running `cfn-lint"
                    " --update-documentation`, do not alter this manually_)\n\n"
                ),
                call(
                    "The following **{}** rules are applied by this linter:\n\n".format(
                        len(collection) + 3
                    )
                ),
                call(
                    "| Rule ID  | Title | Description | Config<br />(Name:Type:Default)"
                    " | Source | Tags |\n"
                ),
                call(
                    "| -------- | ----- | ----------- | ---------- | ------ | ---- |\n"
                ),
                call(
                    '| [E0000<a name="E0000"></a>]'
                    "(../src/cfnlint/rules/errors/parse.py) |"
                    " Parsing error found when parsing the template | Checks for"
                    " JSON/YAML formatting errors in your template |  |"
                    " [Source](https://github.com/aws-cloudformation/cfn-lint) |"
                    " `base` |\n"
                ),
                call(
                    '| [E0001<a name="E0001"></a>]'
                    "(../src/cfnlint/rules/errors/transform.py) |"
                    " Error found when transforming the template | Errors found when"
                    " performing transformation on the template |  |"
                    " [Source](https://github.com/aws-cloudformation/cfn-lint) |"
                    " `base`,`transform` |\n"
                ),
                call(
                    '| [E0002<a name="E0002"></a>]'
                    "(../src/cfnlint/rules/errors/rule.py) |"
                    " Error processing rule on the template | Errors found when"
                    " processing a rule on the template |  |"
                    " [Source](https://github.com/aws-cloudformation/cfn-lint) |"
                    " `base`,`rule` |\n"
                ),
                call(
                    '| [E0003<a name="E0003"></a>]'
                    "(../src/cfnlint/rules/errors/config.py) | "
                    "Error with cfn-lint configuration | "
                    "Error as a result of the cfn-lint configuration |  | "
                    "[Source](https://github.com/aws-cloudformation/cfn-lint) "
                    "| `base`,`rule` |\n"
                ),
                call("\n\\* experimental rules\n"),
            ]
            mock_builtin_open.return_value.write.assert_has_calls(expected_calls)
            self.assertEqual(
                len(expected_calls), mock_builtin_open.return_value.write.call_count
            )
