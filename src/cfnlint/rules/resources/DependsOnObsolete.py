"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class DependsOnObsolete(CloudFormationLintRule):
    """Check unneeded DepensOn Resource Configuration"""
    id = 'W3005'
    shortdesc = 'Check obsolete DependsOn configuration for Resources'
    description = 'Check if DependsOn is specified if not needed. ' \
                  'A Ref or a Fn::GetAtt already is an implicit dependency.'
    source_url = 'https://aws.amazon.com/blogs/devops/optimize-aws-cloudformation-templates/'
    tags = ['resources', 'dependson']

    def get_resource_references(self, cfn, ref_function, resource):
        """Get tree of all resource references of a resource"""
        trees = cfn.search_deep_keys(ref_function)

        # Filter only resoureces
        # Disable pylint for Pylint 2
        # pylint: disable=W0110
        trees = filter(lambda x: x[0] == 'Resources', trees)
        # Filter on the given resource only
        # Disable pylint for Pylint 2
        # pylint: disable=W0110
        trees = filter(lambda x: x[1] == resource, trees)

        return trees

    def check_depends_on(self, cfn, resource, key, path):
        """Check if the DependsOn is already specified"""
        matches = []

        # Get references
        trees = self.get_resource_references(cfn, 'Ref', resource)

        for tree in trees:
            if tree[-1] == key:
                message = 'Obsolete DependsOn on resource ({0}), dependency already enforced by a "Ref" at {1}'
                matches.append(RuleMatch(path, message.format(key, '/'.join(map(str, tree)))))

        # Get the GetAtt
        trees = self.get_resource_references(cfn, 'Fn::GetAtt', resource)

        for tree in trees:
            # GettAtt formation is "resource : Attribute", just check the resource
            if tree[-1][0] == key:
                message = 'Obsolete DependsOn on resource ({0}), dependency already enforced by a "Fn:GetAtt" at {1}'
                matches.append(RuleMatch(path, message.format(key, '/'.join(map(str, tree)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        resources = cfn.get_resources()

        for resource_name, resource_values in resources.items():
            depends_ons = resource_values.get('DependsOn')
            if depends_ons:
                path = ['Resources', resource_name, 'DependsOn']
                self.logger.debug('Validating unneeded DependsOn for %s', resource_name)
                if isinstance(depends_ons, list):
                    for index, depends_on in enumerate(depends_ons):
                        matches.extend(self.check_depends_on(cfn, resource_name, depends_on, path[:] + [index]))
                else:
                    matches.extend(self.check_depends_on(cfn, resource_name, depends_ons, path))

        return matches
