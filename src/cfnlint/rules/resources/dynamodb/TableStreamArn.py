"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class TableStreamArn(CloudFormationLintRule):
    """Check Fn::GetAtt uses of StreamArn on DynamoDB tables"""

    id = "E3727"
    shortdesc = "StreamArn is only available on tables with streaming enabled"
    description = (
        "Fn::GetAtt returns a value for StreamArn only when the table has "
        "a stream configured. A table without a StreamSpecification has no "
        "StreamArn, so Fn::GetAtt fails at deploy time. Add a "
        "StreamSpecification to enable streaming, or use Arn instead."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html"
    tags = ["resources", "dynamodb"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.resource_property_types.append("AWS::DynamoDB::Table")

    def _has_stream(self, properties):
        """Determine if a table has a stream configured.

        Returns True when streaming is provably enabled, False when the
        table provably has no stream, and None when it cannot be
        determined from the template.
        """
        if not isinstance(properties, dict):
            return None

        spec = properties.get("StreamSpecification")
        if spec is None:
            return False
        if not isinstance(spec, dict):
            # Ref or any other undetermined value
            return None
        if "Ref" in spec or any(k.startswith("Fn::") for k in spec):
            # An intrinsic function left unresolved, not a specification
            return None
        # The current resource schema has no StreamEnabled flag:
        # including StreamSpecification enables streaming. A literal
        # StreamEnabled: false is still treated as no stream, for
        # templates written against the older property shape.
        stream_enabled = spec.get("StreamEnabled")
        if isinstance(stream_enabled, bool):
            return stream_enabled
        if stream_enabled is not None:
            return None
        return True

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

        # Only flag when the table provably has no stream in every
        # scenario. Enabled or undetermined stays silent.
        if any(self._has_stream(props) is not False for props in resolved):
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
            if attribute != "StreamArn":
                continue
            message = (
                "'{0}' is not available on a table without a stream. "
                "'StreamArn' is only returned when the table has a "
                "StreamSpecification. Add a StreamSpecification to enable "
                "streaming, or use 'Arn' instead."
            )
            matches.append(
                RuleMatch(getatt_path[:-1], message.format(f"{resource}.{attribute}"))
            )

        return matches
