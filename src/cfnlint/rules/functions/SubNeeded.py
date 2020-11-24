"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
import cfnlint.helpers
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.data import AdditionalSpecs


class SubNeeded(CloudFormationLintRule):
    """
        Check if a substitution string exists without a substitution function

        Found a false-positive or false-negative? All configuration for this rule
        is contained in `src/cfnlint/data/AdditionalSpecs/SubNeededExcludes.json`
        so you can add new entries to fix false-positives or amend existing
        entries for false-negatives.
    """
    id = 'E1029'
    shortdesc = 'Sub is required if a variable is used in a string'
    description = 'If a substitution variable exists in a string but isn\'t wrapped with the Fn::Sub function the deployment will fail.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def __init__(self):
        """Init"""
        super(SubNeeded, self).__init__()

        self.excludes = cfnlint.helpers.load_resource(AdditionalSpecs, 'SubNeededExcludes.json')
        self.global_excludes = {
            'Properties': self.excludes['GlobalPropertyTypes'],
            'Metadata': self.excludes['GlobalMetadataTypes']
        }

        self.config_definition = {
            'custom_excludes': {
                'default': '',
                'type': 'string'
            }
        }
        self.configure()
        self.subParameterRegex = re.compile(r'(\$\{[A-Za-z0-9_:\.]+\})')


    def _match_values_recursive(self, cfnelem, path):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfnelem, dict):
            for key in cfnelem:
                pathprop = path[:]
                pathprop.append(key)
                values.extend(self._match_values_recursive(cfnelem[key], pathprop))
        elif isinstance(cfnelem, list):
            for index, item in enumerate(cfnelem):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values_recursive(item, pathprop))
        else:
            # Leaf node
            if isinstance(cfnelem, six.string_types):  # and re.match(searchRegex, cfnelem):
                for variable in re.findall(self.subParameterRegex, cfnelem):
                    values.append(path + [variable])

        return values


    def _match_values(self, cfn):
        """
            Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values_recursive(cfn.template, []))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values_recursive(cfn.template.get('Globals', {}), []))
        return results


    def _variable_custom_excluded(self, value):
        """ User-defined exceptions for variables, anywhere in the file """
        custom_excludes = self.config['custom_excludes']
        if custom_excludes:
            custom_search = re.compile(custom_excludes)
            return re.match(custom_search, value)
        return False


    def _excluded_by_additional_resource_specs(self, variable, path, cfn):
        """
            Should the variable be excluded due to the resource
            configuration in the AdditionalSpecs file
            'SubNeededExcludes.json'?
        """
        resource_name = path[0]
        resource_type = cfn.template.get('Resources').get(resource_name).get('Type')

        exclusions = {}

        if resource_type in self.excludes['ResourceTypes']:
            exclusions.update(self.excludes['ResourceTypes'][resource_type])

        if self._excluded_by_additional_resource_specs_recursive(variable, path, path[2:], exclusions, cfn):
            return True

        return self._excluded_by_global_excludes_recursive(variable, path, path[2:], path[1], cfn)


    def _excluded_by_global_excludes_recursive(self, variable, full_path, path, exclusion_type, cfn):
        # Make sure the path is well-defined
        if not path:
            return False

        # Is this something we exclude globally on?
        if not exclusion_type in self.global_excludes:
            return False

        # Should we exclude the variable based on the global property exclusion criteria defined in the specs?
        if path[0] in self.global_excludes[exclusion_type]:
            if self._excluded_by_criteria(variable, full_path, self.global_excludes[exclusion_type][path[0]], cfn):
                return True

        path = path[1:]

        # Traverse over any arrays, path should never end with an integer
        while path and isinstance(path[0], int):
            path = path[1:]

        return self._excluded_by_global_excludes_recursive(variable, full_path, path, exclusion_type, cfn)


    def _excluded_by_criteria(self, variable, full_path, exclusions, cfn):
        """
           Run the exclusion logic, and because pylint too-many-return-statements complains
        """
        # Have we excluded all variables for this resource?
        if 'ExcludeAll' in exclusions and exclusions['ExcludeAll']:
            return True

        # Have we excluded the specific variable
        if 'ExcludeValues' in exclusions:
            if variable in exclusions['ExcludeValues']:
                return True

        if 'ExcludeRegex' in exclusions:
            exclude_regex = re.compile(r'^{}$'.format(exclusions['ExcludeRegex']))
            if re.match(exclude_regex, variable):
                return True

        if 'ExcludeBasedOnProperties' in exclusions:
            for exclude_based_on_property in exclusions['ExcludeBasedOnProperties']:
                exclude_based_on_property_path = exclude_based_on_property.split('.')[1:]

                current_property = cfn.template.get('Resources').get(full_path[0]).get('Properties')

                while exclude_based_on_property_path and current_property:
                    current_property = current_property.get(exclude_based_on_property_path[0])
                    exclude_based_on_property_path = exclude_based_on_property_path[1:]

                if current_property and variable in current_property:
                    return True

        return False


    def _excluded_by_additional_resource_specs_recursive(self, variable, full_path, path, exclusions, cfn):
        """
            Should the variable be excluded due to the resource
            configuration in the AdditionalSpecs file
            'SubNeededExcludes.json'?
        """
        # Make sure the path is well-defined
        if not path:
            return False

        # Should we exclude the variable based on the current criteria defined in the specs?
        if self._excluded_by_criteria(variable, full_path, exclusions, cfn):
            return True

        # Recursively check the exclusion critera based on the property tree
        sub_fields = ['Metadata', 'Properties']

        for sub_field in sub_fields:
            if sub_field in exclusions:

                # Traverse over any arrays, path should never end with an integer
                while isinstance(path[0], int):
                    path = path[1:]

                # Recurse
                if path[0] in exclusions[sub_field]:
                    if self._excluded_by_additional_resource_specs_recursive(variable, full_path, path[1:], exclusions[sub_field][path[0]], cfn):
                        return True

        return False


    def _excluded_by_additional_specs(self, variable, path, cfn):
        """
            Should the variable be excluded due to the configuration
            in the AdditionalSpecs file 'SubNeededExcludes.json'?
        """
        if path[0] == 'Resources':
            # Check exclusion at the resource level first
            return self._excluded_by_additional_resource_specs(variable[2:-1], path[1:], cfn)

        return False


    def match(self, cfn):
        matches = []

        # Get a list of paths to every leaf node string containing at least one ${parameter}
        parameter_string_paths = self._match_values(cfn)
        # We want to search all of the paths to check if each one contains an 'Fn::Sub'
        for parameter_string_path in parameter_string_paths:
            if parameter_string_path[0] in ['Parameters']:
                continue

            # The variable to be substituted
            variable = parameter_string_path[-1]

            # Exclude variables that match custom exclude filters, if configured
            # (for third-party tools that pre-process templates before uploading them to AWS)
            if self._variable_custom_excluded(variable):
                continue

            if self._excluded_by_additional_specs(variable, parameter_string_path, cfn):
                continue

            found_sub = False
            # Does the path contain an 'Fn::Sub'?
            for step in parameter_string_path:
                if step == 'Fn::Sub':
                    found_sub = True

            # If we didn't find an 'Fn::Sub' it means a string containing a ${parameter} may not be evaluated correctly
            if not found_sub:
                # Remove the last item (the variable) to prevent multiple errors on 1 line errors
                path = parameter_string_path[:-1]
                message = 'Found an embedded parameter "{}" outside of an "Fn::Sub" at {}'.format(
                    variable, '/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))

        return matches
