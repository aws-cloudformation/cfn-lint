"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.helpers import bool_compare
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class NoEcho(CloudFormationLintRule):
    id = 'W4002'
    shortdesc = 'Check for NoEcho References'
    description = 'Check if there is a NoEcho enabled parameter referenced within a resources Metadata section'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-properties'
    tags = ['resources', 'NoEcho']

    def _get_no_echo_params(self, cfn):
        """ Get no Echo Params"""
        no_echo_params = []
        for parameter_name, parameter_value in cfn.get_parameters().items():
            noecho = parameter_value.get('NoEcho', default=False)
            if bool_compare(noecho, True):
                no_echo_params.append(parameter_name)

        return no_echo_params

    def _check_ref(self, cfn, no_echo_params):
        """ Check Refs """
        matches = []
        refs = cfn.search_deep_keys('Ref')
        for ref in refs:
            if ref[-1] in no_echo_params:
                if len(ref) > 3:
                    if ref[0] == 'Resources' and ref[2] == 'Metadata':
                        matches.append(RuleMatch(ref, 'As the resource "metadata" section contains ' +
                                                 'reference to a "NoEcho" parameter ' +
                                                 str(ref[-1]) +
                                                 ', CloudFormation will display the parameter value in ' +
                                                 'plaintext'))

        return matches

    def _check_sub(self, cfn, no_echo_params):
        """ Check Subs """
        matches = []
        subs = cfn.search_deep_keys('Fn::Sub')
        for sub in subs:
            if isinstance(sub[-1], six.string_types):
                params = cfn.get_sub_parameters(sub[-1])
                for param in params:
                    if param in no_echo_params:
                        if len(sub) > 2:
                            if sub[0] == 'Resources' and sub[2] == 'Metadata':

                                matches.append(RuleMatch(sub[:-1], 'As the resource "metadata" section contains ' +
                                                         'reference to a "NoEcho" parameter ' +
                                                         str(param) +
                                                         ', CloudFormation will display the parameter value in ' +
                                                         'plaintext'))

        return matches

    def match(self, cfn):
        matches = []
        no_echo_params = self._get_no_echo_params(cfn)
        if not no_echo_params:
            return matches
        matches.extend(self._check_ref(cfn, no_echo_params))
        matches.extend(self._check_sub(cfn, no_echo_params))

        return matches
