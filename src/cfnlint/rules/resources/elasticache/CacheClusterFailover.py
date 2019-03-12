"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint.helpers import bool_compare
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class CacheClusterFailover(CloudFormationLintRule):
    """Check automatic failover on a cache cluster"""
    id = 'E3026'
    shortdesc = 'Check Elastic Cache Redis Cluster settings'
    description = 'Evaluate Redis Cluster groups to make sure automatic failover is ' \
                  'enabled when cluster mode is enabled'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources', 'elasticcache']

    def __init__(self):
        """Init"""
        super(CacheClusterFailover, self).__init__()
        self.resource_property_types.append('AWS::ElastiCache::ReplicationGroup')

    def is_cluster_enabled(self, properties):
        """Test if cluster is enabled """
        if isinstance(properties, dict):
            for property_name, property_value in properties.items():
                if property_name == 'cluster-enabled' and property_value == 'yes':
                    return True

        return False

    def _test_cluster_settings(self, properties, path, pg_properties, pg_path, cfn, scenario):
        """ test for each scenario """
        results = []
        pg_conditions = cfn.get_conditions_from_path(cfn.template, pg_path)
        # test to make sure that any condition that may apply to the path for the Ref
        # is not applicable
        if pg_conditions:
            for c_name, c_value in scenario.items():
                if c_name in pg_conditions:
                    if c_value not in pg_conditions.get(c_name):
                        return results
        if self.is_cluster_enabled(cfn.get_value_from_scenario(pg_properties, scenario)):
            c_props = cfn.get_value_from_scenario(properties, scenario)
            automatic_failover = c_props.get('AutomaticFailoverEnabled')
            if bool_compare(automatic_failover, False):
                pathmessage = path[:] + ['AutomaticFailoverEnabled']
                if scenario is None:
                    message = '"AutomaticFailoverEnabled" must be misssing or True when setting up a cluster at {0}'
                    results.append(
                        RuleMatch(pathmessage, message.format('/'.join(map(str, pathmessage)))))
                else:
                    message = '"AutomaticFailoverEnabled" must be misssing or True when setting up a cluster when {0} at {1}'
                    scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                    results.append(
                        RuleMatch(pathmessage, message.format(scenario_text, '/'.join(map(str, pathmessage)))))
            num_cach_nodes = c_props.get('NumCacheClusters', 0)
            if num_cach_nodes <= 1:
                pathmessage = path[:] + ['NumCacheClusters']
                if scenario is None:
                    message = '"NumCacheClusters" must be greater than one when creating a cluster at {0}'
                    results.append(
                        RuleMatch(pathmessage, message.format('/'.join(map(str, pathmessage)))))
                else:
                    message = '"NumCacheClusters" must be greater than one when creating a cluster when {0} at {1}'
                    scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                    results.append(
                        RuleMatch(pathmessage, message.format(scenario_text, '/'.join(map(str, pathmessage)))))

        return results

    def test_cluster_settings(self, properties, path, pg_resource_name, pg_path, cfn):
        """ Test cluster settings for the parameter group and Replication Group """
        results = []
        pg_properties = cfn.template.get('Resources', {}).get(pg_resource_name, {}).get('Properties', {}).get('Properties', {})
        scenarios = cfn.get_conditions_scenarios_from_object([
            properties,
            pg_properties
        ])
        for scenario in scenarios:
            results.extend(
                self._test_cluster_settings(properties, path, pg_properties, pg_path, cfn, scenario))
        return results

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        parameter_groups = properties.get_safe('CacheParameterGroupName', '', path)
        for parameter_group in parameter_groups:
            pg_value = parameter_group[0]
            pg_path = parameter_group[1]
            if isinstance(pg_value, dict):
                for pg_key, pg_resource in pg_value.items():
                    if pg_key == 'Ref' and pg_resource in cfn.get_resources():
                        matches.extend(
                            self.test_cluster_settings(
                                properties, path,
                                pg_resource, pg_path,
                                cfn
                            ))

        return matches
