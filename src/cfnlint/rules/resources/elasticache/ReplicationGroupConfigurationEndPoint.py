"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class ReplicationGroupConfigurationEndPoint(CloudFormationLintRule):
    """Check Fn::GetAtt uses of ConfigurationEndPoint on replication groups"""

    id = "E3726"
    shortdesc = (
        "ConfigurationEndPoint is only available on clustered replication groups"
    )
    description = (
        "Fn::GetAtt returns a value for ConfigurationEndPoint only when the "
        "replication group is clustered. A cluster mode disabled replication "
        "group does not have this attribute, so Fn::GetAtt fails at deploy "
        "time. Use PrimaryEndPoint or ReadEndPoint instead."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html"
    tags = ["resources", "elasticache"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.resource_property_types.append("AWS::ElastiCache::ReplicationGroup")

    def _is_cluster_enabled(self, properties):
        """Determine if cluster mode is enabled for a replication group.

        Returns True when cluster mode is provably enabled, False when it is
        provably disabled, and None when it cannot be determined from the
        template.

        Omitting CacheParameterGroupName gives the engine's non-cluster
        default parameter group, so a group with no parameter group named
        is cluster mode disabled unless the template enables cluster mode
        some other way (an explicit ClusterMode, or more than one shard
        by NumNodeGroups or NodeGroupConfiguration).
        """
        if not isinstance(properties, dict):
            return None

        cluster_mode = properties.get("ClusterMode")
        if isinstance(cluster_mode, str):
            if cluster_mode == "enabled":
                return True
            if cluster_mode == "disabled":
                return False
            # "compatible" and any other value leave the endpoint in doubt
            return None
        if cluster_mode is not None:
            return None

        # A restore inherits cluster mode from the snapshot, and a global
        # datastore secondary inherits it from the global replication
        # group. Neither can be determined from this template.
        if properties.get("SnapshotName") is not None:
            return None
        if properties.get("SnapshotArns") is not None:
            return None
        if properties.get("GlobalReplicationGroupId") is not None:
            return None

        num_node_groups = properties.get("NumNodeGroups")
        if isinstance(num_node_groups, str):
            try:
                num_node_groups = int(num_node_groups)
            except ValueError:
                return None
        if isinstance(num_node_groups, bool):
            return None
        if isinstance(num_node_groups, (int, float)):
            if num_node_groups > 1:
                return True
        elif num_node_groups is not None:
            return None

        # NodeGroupConfiguration sizes the group by shard the same way
        # NumNodeGroups does, so more than one entry means more than one
        # shard and therefore cluster mode. A single entry is one shard,
        # which either mode can have, so it falls through like
        # NumNodeGroups: 1.
        node_group_configuration = properties.get("NodeGroupConfiguration")
        if isinstance(node_group_configuration, list):
            if len(node_group_configuration) > 1:
                return True
        elif node_group_configuration is not None:
            return None

        parameter_group = properties.get("CacheParameterGroupName")
        if isinstance(parameter_group, str):
            name = parameter_group.lower()
            if name.endswith(".cluster.on"):
                return True
            if name.startswith("default."):
                # AWS default parameter groups cannot be modified, so a
                # default group without the .cluster.on suffix has
                # cluster-enabled set to no.
                return False
            # A custom or pre-existing parameter group can have
            # cluster-enabled set either way, so its name alone does not
            # determine cluster mode.
            return None
        if parameter_group is not None:
            return None

        # No parameter group is named, so the AWS default for the engine
        # family applies. That default is cluster mode disabled, and a
        # single node group does not change that.
        return False

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        scenarios = cfn.get_conditions_scenarios_from_object([properties])
        if scenarios:
            resolved = [
                cfn.get_value_from_scenario(properties, scenario)
                for scenario in scenarios
            ]
        else:
            resolved = [properties]

        # Only flag when the group is provably cluster mode disabled in
        # every scenario. Enabled or undetermined stays silent.
        if any(self._is_cluster_enabled(props) is not False for props in resolved):
            return matches

        logical_id = path[1]
        for getatt_path in cfn.search_deep_keys("Fn::GetAtt"):
            if getatt_path and getatt_path[0] == "Globals":
                continue
            # search_deep_keys appends the matched value as the last element
            value = getatt_path[-1]
            if isinstance(value, str):
                if "." not in value:
                    continue
                resource, attribute = value.split(".", 1)
            elif isinstance(value, list) and len(value) == 2:
                resource, attribute = value
            else:
                continue
            if resource != logical_id:
                continue
            if not isinstance(attribute, str):
                continue
            if not attribute.startswith("ConfigurationEndPoint."):
                continue
            message = (
                "'{0}' is not available on a cluster mode disabled "
                "replication group. 'ConfigurationEndPoint' is only "
                "returned when the replication group is clustered. Use "
                "'PrimaryEndPoint' or 'ReadEndPoint' instead."
            )
            matches.append(
                RuleMatch(getatt_path[:-1], message.format(f"{resource}.{attribute}"))
            )

        return matches
