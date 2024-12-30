"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.rules import RulesCollection
from cfnlint.runner.template import run_template_by_data


@pytest.mark.parametrize(
    "name, config, runner_results, expected_parameters",
    [
        (
            "A standard template",
            ConfigMixIn(),
            [
                iter([]),
            ],
            [None],
        ),
        (
            "One set of parameters",
            ConfigMixIn(parameters=[{"Foo": "Bar"}]),
            [
                iter([]),
            ],
            [{"Foo": "Bar"}],
        ),
        (
            "Multiple parameters",
            ConfigMixIn(parameters=[{"A": "B"}, {"C": "D"}]),
            [
                iter([]),
                iter([]),
            ],
            [
                {"A": "B"},
                {"C": "D"},
            ],
        ),
    ],
)
def test_runner(
    name,
    config,
    runner_results,
    expected_parameters,
):

    with patch(
        "cfnlint.rules._rules.RulesCollection.run", side_effect=runner_results
    ) as mock_run:
        list(run_template_by_data({}, config, RulesCollection()))

        calls = mock_run.call_args_list
        for index, call in enumerate(calls):
            assert call.kwargs["cfn"].parameters == expected_parameters[index], (
                f"{name}: {call.kwargs['cfn'].parameters} "
                f"!= {expected_parameters[index]}"
            )
