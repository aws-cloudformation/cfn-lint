"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class DependsOnObsolete(CloudFormationLintRule):
    """Check unneeded DepensOn Resource Configuration"""
    id = 'W3005'
    shortdesc = 'Check obsolete DependsOn configuration for Resources'
    description = 'Check if DependsOn is specified if not needed. ' \
                  'A Ref or a Fn::GetAtt already is an implicit dependency.'
    source_url = 'https://aws.amazon.com/blogs/devops/optimize-aws-cloudformation-templates/'
    tags = ['resources', 'dependson', 'ref', 'getatt']

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
                matches.append(RuleMatch(path, message.format(key, '/'.join(map(str, tree[:-1])))))

        # Get the GetAtt
        trees = self.get_resource_references(cfn, 'Fn::GetAtt', resource)

        for tree in trees:
            # GettAtt formation is "resource : Attribute", just check the resource
            if tree[-1][0] == key:
                message = 'Obsolete DependsOn on resource ({0}), dependency already enforced by a "Fn:GetAtt" at {1}'
                matches.append(RuleMatch(path, message.format(key, '/'.join(map(str, tree[:-1])))))

        return matches

    def match(self, cfn):
        matches = []

        resources = cfn.get_resources()

        for resource_name, resource_values in resources.items():
            depends_ons = resource_values.get('DependsOn')
            if depends_ons:
                path = ['Resources', resource_name, 'DependsOn']
                self.logger.debug('Validating unneeded DependsOn for %s', resource_name)
                if isinstance(depends_ons, list):
                    for index, depends_on in enumerate(depends_ons):
                        matches.extend(self.check_depends_on(
                            cfn, resource_name, depends_on, path[:] + [index]))
                else:
                    matches.extend(self.check_depends_on(cfn, resource_name, depends_ons, path))

        return matches
