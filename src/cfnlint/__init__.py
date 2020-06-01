"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import cfnlint.helpers
import cfnlint.conditions
from cfnlint.decorators.refactored import refactored
from cfnlint.graph import Graph
from cfnlint.transform import Transform
from cfnlint.decode.node import TemplateAttributeError
from cfnlint.helpers import PSEUDOPARAMS
from cfnlint.rules import RuleMatch as _RuleMatch
from cfnlint.rules import Match as _Match
from cfnlint.rules import RulesCollection as _RulesCollection
from cfnlint.rules import CloudFormationLintRule as _CloudFormationLintRule
from cfnlint.rules import ParseError as _ParseError
from cfnlint.rules import TransformError as _TransformError
from cfnlint.rules import RuleError as _RuleError
from cfnlint.runner import Runner as _Runner
from cfnlint.template import Template as _Template


from cfnlint.decode.node import dict_node
import cfnlint.rules

LOGGER = logging.getLogger(__name__)


@refactored('RuleMatch is refactored and deprecated. Please use cfnlint.rules.RuleMatch')
class RuleMatch(_RuleMatch):
    """ Refactored class RuleMatch """


@refactored('Match is refactored and deprecated. Please use cfnlint.rules.Match')
class Match(_Match):
    """ Refactored class Match """


@refactored('RulesCollection is refactored and deprecated. Please use cfnlint.rules.RulesCollection')
class RulesCollection(_RulesCollection):
    """ Refactored class Rules Collection """


@refactored('CloudFormationLintRule is refactored and deprecated. Please use cfnlint.rules.CloudFormationLintRule')
class CloudFormationLintRule(_CloudFormationLintRule):
    """ Refactored class Rules CloudFormationLintRule """


@refactored('ParseError is refactored and deprecated. Please use cfnlint.rules.ParseError')
class ParseError(_ParseError):
    """ Refactored class Rules ParseError """


@refactored('TransformError is refactored and deprecated. Please use cfnlint.rules.TransformError')
class TransformError(_TransformError):
    """ Refactored class Rules TransformError """


@refactored('RuleError is refactored and deprecated. Please use cfnlint.rules.RuleError')
class RuleError(_RuleError):
    """ Refactored class Rules RuleError """

@refactored('Template is refactored and deprecated. Please use Template in cfnlint.template')
class Template(_Template):
    """ Refactored class Template """

@refactored('Runner is refactored and deprecated. Please use Runner in cfnlint.runner')
class Runner(_Runner):
    """ Refactored class Runner """
