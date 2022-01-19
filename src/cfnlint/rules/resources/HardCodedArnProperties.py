"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class HardCodedArnProperties(CloudFormationLintRule):
    """Checks Resources if ARNs use correctly placed Pseudo Parameters instead of hardcoded Partition, Region, and Account Number"""
    id = 'I3042'
    shortdesc = 'ARNs should use correctly placed Pseudo Parameters'
    description = 'Checks Resources if ARNs use correctly placed Pseudo Parameters instead of hardcoded Partition, Region, and Account Number'
    source_url = ''
    tags = ['resources']
    regex = re.compile(r'arn:(\$\{[^:]*::[^:]*}|[^:]*):[^:]+:(\$\{[^:]*::[^:]*}|[^:]*):(\$\{[^:]*::[^:]*}|[^:]*)')

    def __init__(self):
        """Init"""
        super(HardCodedArnProperties, self).__init__()
        self.config_definition = {
            'partition': {
                'default': True,
                'type': 'boolean',
            },
            'region': {
                'default': False,
                'type': 'boolean',
            },
            'accountId': {
                'default': False,
                'type': 'boolean',
            },
        }
        self.configure()

    def _match_values(self, cfnelem, path):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfnelem, dict):
            for key in cfnelem:
                pathprop = path[:]
                pathprop.append(key)
                values.extend(self._match_values(cfnelem[key], pathprop))
        elif isinstance(cfnelem, list):
            for index, item in enumerate(cfnelem):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values(item, pathprop))
        else:
            # Leaf node
            if isinstance(cfnelem, str):  # and re.match(searchRegex, cfnelem):
                for variable in re.findall(self.regex, cfnelem):
                    if 'Fn::Sub' in path:
                        values.append(path + [variable])

        return values

    def match_values(self, cfn):
        """
            Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values(cfn.template.get('Resources', {}), []))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values(cfn.template.get('Globals', {}), []))
        return results

    def match(self, cfn):
        """Check CloudFormation Resources"""
        matches = []

        # Get a list of paths to every leaf node string containing at least one ${parameter}
        parameter_string_paths = self.match_values(cfn)
        # We want to search all of the paths to check if each one contains an 'Fn::Sub'
        for parameter_string_path in parameter_string_paths:
            path = ['Resources'] + parameter_string_path[:-1]
            candidate = parameter_string_path[-1]

            # !Sub arn:${AWS::Partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
            # is valid even with aws as the account #.  This handles empty string
            if self.config['partition'] and not re.match(r'^\$\{\w+}|\$\{AWS::Partition}|$', candidate[0]):
                # or not re.match(r'^(\$\{\w+}|\$\{AWS::Region}|)$', candidate[1]) or not re.match(r'^\$\{\w+}|\$\{AWS::AccountId}|aws|$', candidate[2]):
                message = 'ARN in Resource {0} contains hardcoded Partition in ARN or incorrectly placed Pseudo Parameters'
                matches.append(RuleMatch(
                    path,
                    message.format(path[1])
                ))
            if self.config['region'] and not re.match(r'^(\$\{\w+}|\$\{AWS::Region}|)$', candidate[1]):
                # or  or not re.match(r'^\$\{\w+}|\$\{AWS::AccountId}|aws|$', candidate[2]):
                message = 'ARN in Resource {0} contains hardcoded Region in ARN or incorrectly placed Pseudo Parameters'
                matches.append(RuleMatch(
                    path,
                    message.format(path[1])
                ))
            if self.config['accountId'] and not re.match(r'^\$\{\w+}|\$\{AWS::AccountId}|aws|$', candidate[2]):
                message = 'ARN in Resource {0} contains hardcoded AccountId in ARN or incorrectly placed Pseudo Parameters'
                matches.append(RuleMatch(
                    path,
                    message.format(path[1])
                ))

        return matches
