"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.context import ParameterSet
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
            [],
        ),
        (
            "One set of parameters",
            ConfigMixIn(
                parameters=[ParameterSet(source=None, parameters={"Foo": "Bar"})]
            ),
            [
                iter([]),
            ],
            [ParameterSet(source=None, parameters={"Foo": "Bar"})],
        ),
        (
            "Multiple parameters",
            ConfigMixIn(
                parameters=[
                    ParameterSet(source=None, parameters={"A": "B"}),
                    ParameterSet(source=None, parameters={"C": "D"}),
                ]
            ),
            [
                iter([]),
                iter([]),
            ],
            [
                ParameterSet(
                    source=None,
                    parameters={"A": "B"},
                ),
                ParameterSet(
                    source=None,
                    parameters={"C": "D"},
                ),
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

        assert mock_run.call_count == 1
        call = mock_run.call_args
        assert call.kwargs["cfn"].context.parameter_sets == expected_parameters, (
            f"{name}: {call.kwargs['cfn'].context.parameter_sets} "
            f"!= {expected_parameters}"
        )
