"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match
from cfnlint.rules.errors import ParseError
from cfnlint.runner import Runner


@pytest.mark.parametrize(
    "name,config,expected",
    [
        (
            "Test decode errors with multiple files",
            ConfigMixIn(
                cli_args=[
                    "-t",
                    "test/fixtures/templates/bad/duplicate.yaml",
                    "test/fixtures/templates/bad/duplicate.json",
                ]
            ),
            [
                Match(
                    'Duplicate found "MySNSTopic"',
                    filename="test/fixtures/templates/bad/duplicate.json",
                    rule=ParseError(),
                    linenumber=16,
                    linenumberend=15,
                    columnnumber=4,
                    columnnumberend=29,
                ),
                Match(
                    'Duplicate found "MySNSTopic"',
                    filename="test/fixtures/templates/bad/duplicate.json",
                    rule=ParseError(),
                    linenumber=4,
                    linenumberend=3,
                    columnnumber=4,
                    columnnumberend=40,
                ),
                Match(
                    'Duplicate found "MySNSTopic"',
                    filename="test/fixtures/templates/bad/duplicate.json",
                    rule=ParseError(),
                    linenumber=22,
                    linenumberend=21,
                    columnnumber=4,
                    columnnumberend=29,
                ),
                Match(
                    'Duplicate found "mySnsTopic" (line 3)',
                    filename="test/fixtures/templates/bad/duplicate.yaml",
                    rule=ParseError(),
                    linenumber=3,
                    linenumberend=3,
                    columnnumber=3,
                    columnnumberend=13,
                ),
                Match(
                    'Duplicate found "mySnsTopic" (line 9)',
                    filename="test/fixtures/templates/bad/duplicate.yaml",
                    rule=ParseError(),
                    linenumber=9,
                    linenumberend=9,
                    columnnumber=3,
                    columnnumberend=13,
                ),
                Match(
                    'Duplicate found "mySnsTopic" (line 13)',
                    filename="test/fixtures/templates/bad/duplicate.yaml",
                    rule=ParseError(),
                    linenumber=13,
                    linenumberend=13,
                    columnnumber=3,
                    columnnumberend=13,
                ),
            ],
        ),
    ],
)
def test_run(name, config, expected):

    runner = Runner(config)

    errs = list(runner.run())

    assert errs == expected, f"{name}: {errs} != {expected}"
