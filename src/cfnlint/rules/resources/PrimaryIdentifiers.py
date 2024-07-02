"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from copy import copy
from dataclasses import dataclass, field
from typing import Any, Dict, Set

from cfnlint._typing import RuleMatches
from cfnlint.jsonschema._utils import equal
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, ResourceNotFoundError
from cfnlint.template import Template


@dataclass
class _Seen:
    conditions: Dict[str, Set[bool]] = field(init=True, default_factory=dict)
    resources: Set[str] = field(init=True, default_factory=set)
    instance: Dict[str, Any] = field(init=True, default_factory=dict)


class PrimaryIdentifiers(CloudFormationLintRule):
    id = "E3019"
    shortdesc = "Validate that all resources have unique primary identifiers"
    description = (
        "Use the primary identifiers in a resource schema to validate that "
        "resources inside the template are unique"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html"
    tags = ["parameters", "resources"]

    def _merge_conditions(
        self, conditions1: Dict[str, Set[bool]], conditions2: Dict[str, Set[bool]]
    ):
        for k2, v2 in conditions2.items():
            if k2 in conditions1:
                if v2 != conditions1[k2]:
                    raise ValueError("Condition mismatch")
            conditions1[k2] = v2

        return conditions1

    def _validate_resource_type_uniqueness(self, cfn, resource_type, ids):
        matches = []
        seens = []
        for resource_name, resource_attributes in cfn.get_resources(
            resource_type
        ).items():
            condition = resource_attributes.get("Condition")
            properties = resource_attributes.get("Properties", {})
            path = ["Resources", resource_name, "Properties"]
            for scenario in cfn.get_object_without_conditions(properties):
                object = scenario.get("Object")
                conditions = scenario.get("Scenario")
                if conditions is None:
                    conditions = {}
                # we need to change this to a set for implies to work
                conditions = {k: set([v]) for k, v in conditions.items()}

                # if there is a resource level condition lets see if its valid
                # and add it to the scenario as needed
                if condition:
                    if scenario:
                        if not cfn.conditions.check_implies(scenario, condition):
                            continue
                    conditions[condition] = set([True])

                # validate object is an object just in case it was emptied out
                # from the condition (Ref: AWS::NoValue)
                if not isinstance(object, dict):
                    continue

                # get_object_without_conditions will return all elements
                # so we are going to filter down to the ids that we care about
                identifiers = {id: object.get(id) for id in ids}
                # if any of the identifiers are None that means the service
                # will define it and we can skip this test
                if any(identifier is None for identifier in identifiers.values()):
                    continue

                # build the element
                element = _Seen(conditions, set([resource_name]), identifiers)

                found = False
                for seen in seens:
                    if equal(seen.instance, element.instance):
                        try:
                            merged_conditions = self._merge_conditions(
                                copy(seen.conditions), copy(element.conditions)
                            )
                            # if conditions are empty we found it
                            if not merged_conditions:
                                found = True
                                seen.resources.add(resource_name)
                            for _ in cfn.conditions.build_scenarios(merged_conditions):
                                seen.resources.add(resource_name)
                                # because the conditions could be unique
                                # we will validate conditions being equal
                                # and only say found if they match
                                if equal(element.conditions, seen.conditions):
                                    found = True
                                break

                        except ValueError:
                            continue

                # add anything not already Found to the seens element
                if not found:
                    seens.append(element)

        for seen in seens:
            # build errors for any seen items with more than 1 resource
            if len(seen.resources) > 1:
                for resource in seen.resources:
                    path = ["Resources", resource, "Properties"]
                    if len(seen.instance) == 1:
                        key = list(seen.instance.keys())[0]
                        path.append(key)

                    message = (
                        f"Primary identifiers {seen.instance!r} should "
                        "have unique values across the resources "
                        f"{seen.resources!r}"
                    )

                    matches.append(RuleMatch(path, message))

        return matches

    def match(self, cfn: Template) -> RuleMatches:
        tS = set()
        for _, resource_properties in cfn.get_resources().items():
            t = resource_properties.get("Type")
            if isinstance(t, str):
                tS.add(t)

        matches = []
        for t in tS:
            try:
                schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(cfn.regions[0], t)

                # we are worried about primary identifiers that can be set
                # by the customer so if any primary identifiers are read
                # only we have to skip evaluation
                primary_ids = schema.schema.get("primaryIdentifier", [])
                if not primary_ids:
                    continue

                read_only_ids = schema.schema.get("readOnlyProperties", [])

                if any(id in read_only_ids for id in primary_ids):
                    continue

                primary_ids = [id.replace("/properties/", "") for id in primary_ids]
                # most primaryIdentifiers are at the root level. At this time
                # we can only validate if they are at the root of Properties
                if any("/" in id for id in primary_ids):
                    continue
                matches.extend(
                    self._validate_resource_type_uniqueness(cfn, t, primary_ids)
                )
            except ResourceNotFoundError:
                continue
        return matches
