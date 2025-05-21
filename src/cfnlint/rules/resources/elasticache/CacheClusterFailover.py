"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import bool_compare
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class CacheClusterFailover(CloudFormationLintRule):
    """Check automatic failover on a cache cluster"""

    id = "E3026"
    shortdesc = "Check Elastic Cache Redis Cluster settings"
    description = (
        "Evaluate Redis Cluster groups to make sure automatic failover is "
        "enabled when cluster mode is enabled"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources", "elasticcache"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.resource_property_types.append("AWS::ElastiCache::ReplicationGroup")

    def is_cluster_enabled(self, properties):
        """Test if cluster is enabled"""
        if isinstance(properties, dict):
            for property_name, property_value in properties.items():
                if property_name == "cluster-enabled" and property_value == "yes":
                    return True

        return False

    def _test_cluster_settings(
        self, properties, path, pg_properties, pg_path, cfn, scenario
    ):
        """test for each scenario"""
        results = []
        pg_conditions = cfn.get_conditions_from_path(cfn.template, pg_path)
        # test to make sure that any condition that may apply to the path for the Ref
        # is not applicable
        if pg_conditions and scenario:
            for c_name, c_value in scenario.items():
                if c_name in pg_conditions:
                    if c_value not in pg_conditions.get(c_name):
                        return results
        if self.is_cluster_enabled(
            cfn.get_value_from_scenario(pg_properties, scenario)
        ):
            c_props = cfn.get_value_from_scenario(properties, scenario)
            automatic_failover = c_props.get("AutomaticFailoverEnabled")
            if bool_compare(automatic_failover, False):
                pathmessage = path[:] + ["AutomaticFailoverEnabled"]
                if scenario is None:
                    message = (
                        '"AutomaticFailoverEnabled" must be misssing or True when'
                        " setting up a cluster at {0}"
                    )
                    results.append(
                        RuleMatch(
                            pathmessage, message.format("/".join(map(str, pathmessage)))
                        )
                    )
                else:
                    message = (
                        '"AutomaticFailoverEnabled" must be misssing or True when'
                        " setting up a cluster when {0} at {1}"
                    )
                    scenario_text = " and ".join(
                        [f'when condition "{k}" is {v}' for (k, v) in scenario.items()]
                    )
                    results.append(
                        RuleMatch(
                            pathmessage,
                            message.format(
                                scenario_text, "/".join(map(str, pathmessage))
                            ),
                        )
                    )
            num_node_groups = c_props.get("NumNodeGroups")
            if not num_node_groups:
                # only test cache nodes if num node groups aren't specified
                num_cache_nodes = c_props.get("NumCacheClusters", 0)
                if num_cache_nodes <= 1:
                    pathmessage = path[:] + ["NumCacheClusters"]
                    if scenario is None:
                        message = (
                            '"NumCacheClusters" must be greater than one when creating'
                            " a cluster at {0}"
                        )
                        results.append(
                            RuleMatch(
                                pathmessage,
                                message.format("/".join(map(str, pathmessage))),
                            )
                        )
                    else:
                        message = (
                            '"NumCacheClusters" must be greater than one when creating'
                            " a cluster when {0} at {1}"
                        )
                        scenario_text = " and ".join(
                            [
                                f'when condition "{k}" is {v}'
                                for (k, v) in scenario.items()
                            ]
                        )
                        results.append(
                            RuleMatch(
                                pathmessage,
                                message.format(
                                    scenario_text, "/".join(map(str, pathmessage))
                                ),
                            )
                        )

        return results

    def test_cluster_settings(self, properties, path, pg_resource_name, pg_path, cfn):
        """Test cluster settings for the parameter group and Replication Group"""
        results = []
        pg_properties = (
            cfn.template.get("Resources", {})
            .get(pg_resource_name, {})
            .get("Properties", {})
            .get("Properties", {})
        )
        scenarios = cfn.get_conditions_scenarios_from_object(
            [properties, pg_properties]
        )
        if scenarios:
            for scenario in scenarios:
                results.extend(
                    self._test_cluster_settings(
                        properties, path, pg_properties, pg_path, cfn, scenario
                    )
                )
        else:
            results.extend(
                self._test_cluster_settings(
                    properties, path, pg_properties, pg_path, cfn, None
                )
            )
        return results

    def _check_ref(self, value, path, **kwargs):
        cfn = kwargs["cfn"]
        properties = kwargs["properties"]
        if value in cfn.get_resources():
            return self.test_cluster_settings(properties, path, value, path, cfn)
        return []

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""

        return cfn.check_value(
            properties,
            "CacheParameterGroupName",
            path,
            check_ref=self._check_ref,
            properties=properties,
            cfn=cfn,
        )
