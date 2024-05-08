"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import functools
import logging
from copy import deepcopy
from typing import Any, Dict, List

import regex as re

import cfnlint.conditions
import cfnlint.helpers
from cfnlint.context import create_context_for_template
from cfnlint.decode.node import dict_node, list_node
from cfnlint.graph import Graph
from cfnlint.match import Match
from cfnlint.template.getatts import GetAtts
from cfnlint.template.transforms import Transform

LOGGER = logging.getLogger(__name__)


class Template:  # pylint: disable=R0904,too-many-lines,too-many-instance-attributes
    """Class for a CloudFormation template"""

    def __init__(
        self,
        filename: str | None,
        template: Dict[str, Any],
        regions: List[str] | None = None,
    ):
        if regions is None:
            self.regions = [cfnlint.helpers.REGION_PRIMARY]
        else:
            self.regions = regions
        self.filename = filename
        self.template = template
        self.sections = [
            "AWSTemplateFormatVersion",
            "Description",
            "Metadata",
            "Parameters",
            "Mappings",
            "Conditions",
            "Transform",
            "Hooks",
            "Resources",
            "Outputs",
            "Rules",
        ]
        self.transform_pre: Dict[str, Any] = {}
        self.transform_pre["Globals"] = {}
        self.transform_pre["Ref"] = self.search_deep_keys("Ref")
        self.transform_pre["Fn::Sub"] = self.search_deep_keys("Fn::Sub")
        self.transform_pre["Fn::FindInMap"] = self.search_deep_keys("Fn::FindInMap")
        self.transform_pre["Transform"] = self.template.get("Transform", [])
        self.transform_pre["Fn::ForEach"] = self.search_deep_keys(
            cfnlint.helpers.FUNCTION_FOR_EACH
        )

        self.conditions = cfnlint.conditions.Conditions(self)
        self.graph = None
        try:
            self.graph = Graph(self)
        except KeyError as err:
            LOGGER.debug(
                "Encountered KeyError error while building graph. Ignored as this "
                "should be caught by other rules and is more than likely a template "
                "formatting error: %s",
                err,
            )
        except Exception as err:  # pylint: disable=broad-except
            LOGGER.info("Encountered unknown error while building graph: %s", err)

        self.context = create_context_for_template(self)
        self.search_deep_keys = functools.lru_cache()(self.search_deep_keys)  # type: ignore

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def _cache_clear(self):
        self.search_deep_keys.cache_clear()

    def transform(self) -> List[Match]:
        """
        Transform the template
        """
        transform = Transform()
        results = transform.transform(self)
        self._cache_clear()
        return results

    def build_graph(self):
        """Generates a DOT representation of the template"""
        path = self.filename + ".dot"
        try:
            self.graph.to_dot(path)
            LOGGER.info("DOT representation of the graph written to %s", path)
        except ImportError:
            LOGGER.error(
                (
                    "Could not write the graph in DOT format. "
                    "Please install either `pygraphviz` or `pydot` modules."
                )
            )

    def has_language_extensions_transform(self):
        """Check if the template has language extensions transform declared"""
        lang_extensions_transform = "AWS::LanguageExtensions"
        transform_declaration = self.transform_pre["Transform"]
        transform_type = (
            transform_declaration
            if isinstance(transform_declaration, list)
            else [transform_declaration]
        )
        return bool(lang_extensions_transform in transform_type)

    def has_serverless_transform(self):
        """Check if the template has SAM transform declared"""
        lang_extensions_transform = "AWS::Serverless-2016-10-31"
        transform_declaration = self.transform_pre["Transform"]
        transform_type = (
            transform_declaration
            if isinstance(transform_declaration, list)
            else [transform_declaration]
        )
        return bool(lang_extensions_transform in transform_type)

    def is_cdk_template(self) -> bool:
        """Check if the template was created by CDK"""
        resources = self.template.get("Resources")
        if not isinstance(resources, dict):
            return False

        for _, properties in resources.items():
            if not isinstance(properties, dict):
                continue
            resource_type = properties.get("Type")
            if not isinstance(resource_type, str):
                continue
            if resource_type == "AWS::CDK::Metadata":
                return True

        return False

    def get_resources(self, resource_type=[]):
        """
        Get Resources
        Filter on type when specified
        """
        resources = self.template.get("Resources", {})
        if not isinstance(resources, dict):
            return {}
        if isinstance(resource_type, str):
            resource_type = [resource_type]

        results = {}
        for k, v in resources.items():
            if isinstance(v, dict):
                if (v.get("Type", None) in resource_type) or (
                    not resource_type and v.get("Type") is not None
                ):
                    results[k] = v

        return results

    def get_parameters_valid(self):
        result = {}
        if isinstance(self.template.get("Parameters"), dict):
            parameters = self.template.get("Parameters")
            for parameter_name, parameter_value in parameters.items():
                if isinstance(parameter_value, dict):
                    if isinstance(parameter_value.get("Type"), str):
                        result[parameter_name] = parameter_value

        return result

    def get_modules(self):
        """Get Modules"""
        resources = self.template.get("Resources", {})
        if not resources:
            return {}

        results = {}
        for k, v in resources.items():
            if isinstance(v, dict):
                if v.get("Type") is not None and str(v.get("Type")).endswith(
                    "::MODULE"
                ):
                    results[k] = v

        return results

    def get_valid_refs(self) -> cfnlint.helpers.RegexDict:
        results = cfnlint.helpers.RegexDict()
        parameters = self.template.get("Parameters", {})
        if parameters:
            for name, value in parameters.items():
                if isinstance(value, dict):
                    if "Type" in value:
                        element = {}
                        element["Type"] = value["Type"]
                        element["From"] = "Parameters"
                        results[name] = element
        resources = self.template.get("Resources", {})
        if resources:
            for name, value in resources.items():
                resource_type = value.get("Type", "")
                if not isinstance(resource_type, str):
                    continue
                if resource_type.endswith("::MODULE"):
                    element = {}
                    element["Type"] = "MODULE"
                    element["From"] = "Resources"
                    results[f"{name}.*"] = element
                elif resource_type:
                    element = {}
                    element["Type"] = resource_type
                    element["From"] = "Resources"
                    results[name] = element

        for pseudoparam in cfnlint.helpers.PSEUDOPARAMS:
            element = {}
            element["Type"] = "Pseudo"
            element["From"] = "Pseudo"
            results[pseudoparam] = element
        return results

    def get_valid_getatts(self):
        results = GetAtts(self.regions)

        resources = self.template.get("Resources", {})

        for name, value in resources.items():
            resource_type = value.get("Type")
            if isinstance(resource_type, str):
                results.add(name, resource_type)

        return results

    def get_directives(self):
        results = {}
        resources = self.get_resources()
        if resources:
            for resource_name, resource_values in resources.items():
                if isinstance(resource_values, dict):
                    ignore_rule_ids = (
                        resource_values.get("Metadata", {})
                        .get("cfn-lint", {})
                        .get("config", {})
                        .get("ignore_checks", [])
                    )
                    for ignore_rule_id in ignore_rule_ids:
                        if ignore_rule_id not in results:
                            results[ignore_rule_id] = []
                        results[ignore_rule_id].append(resource_name)
        return results

    # pylint: disable=dangerous-default-value
    def _search_deep_keys(self, searchText: str | re.Pattern, cfndict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(cfndict, dict):
            for key in cfndict:
                pathprop = path[:]
                pathprop.append(key)
                if isinstance(searchText, str):
                    if key == searchText:
                        pathprop.append(cfndict[key])
                        keys.append(pathprop)
                        # pop the last element off for nesting of found elements for
                        # dict and list checks
                        pathprop = pathprop[:-1]
                elif isinstance(searchText, re.Pattern):
                    if isinstance(key, str):
                        if re.match(searchText, key):
                            pathprop.append(cfndict[key])
                            keys.append(pathprop)
                            # pop the last element off for nesting of found elements for
                            # dict and list checks
                            pathprop = pathprop[:-1]
                if isinstance(cfndict[key], dict):
                    keys.extend(
                        self._search_deep_keys(searchText, cfndict[key], pathprop)
                    )
                elif isinstance(cfndict[key], list):
                    for index, item in enumerate(cfndict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(
                            self._search_deep_keys(searchText, item, pathproparr)
                        )
        elif isinstance(cfndict, list):
            for index, item in enumerate(cfndict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(self._search_deep_keys(searchText, item, pathprop))

        return keys

    def search_deep_keys(
        self, searchText: str | re.Pattern, includeGlobals: bool = True
    ):
        """
        Search for a key in all parts of the template.
        :return if searchText is "Ref", an array like
        ['Resources', 'myInstance', 'Properties', 'ImageId', 'Ref', 'Ec2ImageId']
        """
        results = []
        results.extend(self._search_deep_keys(searchText, self.template, []))
        # Globals are removed during a transform.  They need to be checked manually
        if includeGlobals:
            pre_results = self._search_deep_keys(
                searchText, self.transform_pre.get("Globals"), []
            )
            for pre_result in pre_results:
                results.append(["Globals"] + pre_result)
        return results

    def get_condition_values(self, template, path=[]):
        """Evaluates conditions and brings back the values"""
        matches = []
        if not isinstance(template, list):
            return matches
        if not len(template) == 3:
            return matches

        for index, item in enumerate(template[1:]):
            result = {}
            result["Path"] = path[:] + [index + 1]
            if not isinstance(item, (dict, list)):
                # Just straight values and pass them through
                result["Value"] = item
                matches.append(result)
            elif len(item) == 1:
                # Checking for conditions inside of conditions
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                            results = self.get_condition_values(
                                sub_value, result["Path"] + [sub_key]
                            )
                            if isinstance(results, list):
                                matches.extend(results)
                        elif sub_key == "Ref":
                            if sub_value != "AWS::NoValue":
                                result["Value"] = item
                                matches.append(result)
                        else:
                            # Return entire Item
                            result["Value"] = item
                            matches.append(result)
                else:
                    # Return entire Item
                    result["Value"] = item
                    matches.append(result)
            else:
                # Length longer than 1 means a list or object that
                # should be fully returned
                result["Value"] = item
                matches.append(result)

        return matches

    def get_values(self, obj, key, path=[]):
        """
        Logic for getting the value of a key
        Returns None if the item isn't found
        Returns empty list if the item is found but Ref or GetAtt
        Returns all the values as a list if condition
        Returns the value if its just a string, int, boolean, etc.

        """
        matches = []

        if not isinstance(obj, dict):
            return None
        value = obj.get(key)
        if value is None:
            return None
        if isinstance(value, (dict)):
            if len(value) == 1:
                is_condition = False
                is_no_value = False
                for obj_key, obj_value in value.items():
                    if obj_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                        is_condition = True
                        results = self.get_condition_values(
                            obj_value, path[:] + [obj_key]
                        )
                        if isinstance(results, list):
                            for result in results:
                                check_obj = obj.copy()
                                check_obj[key] = result["Value"]
                                matches.extend(
                                    self.get_values(check_obj, key, result["Path"])
                                )
                    elif obj_key == "Ref" and obj_value == "AWS::NoValue":
                        is_no_value = True
                if not is_condition and not is_no_value:
                    result = {}
                    result["Path"] = path[:]
                    result["Value"] = value
                    matches.append(result)
            else:
                result = {}
                result["Path"] = path[:]
                result["Value"] = value
                matches.append(result)
        elif isinstance(value, (list)):
            for list_index, list_value in enumerate(value):
                if isinstance(list_value, dict):
                    if len(list_value) == 1:
                        is_condition = False
                        is_no_value = False
                        for obj_key, obj_value in list_value.items():
                            if obj_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                                is_condition = True
                                results = self.get_condition_values(
                                    obj_value, path[:] + [list_index, obj_key]
                                )
                                if isinstance(results, list):
                                    matches.extend(results)
                            elif obj_key == "Ref" and obj_value == "AWS::NoValue":
                                is_no_value = True
                        if not is_condition and not is_no_value:
                            result = {}
                            result["Path"] = path[:] + [list_index]
                            result["Value"] = list_value
                            matches.append(result)
                    else:
                        result = {}
                        result["Path"] = path[:] + [list_index]
                        result["Value"] = list_value
                        matches.append(result)
                else:
                    result = {}
                    result["Path"] = path[:] + [list_index]
                    result["Value"] = list_value
                    matches.append(result)
        else:
            result = {}
            result["Path"] = path[:]
            result["Value"] = value
            matches.append(result)

        return matches

    def _loc(self, obj):
        """Return location of object"""
        return (
            obj.start_mark.line,
            obj.start_mark.column,
            obj.end_mark.line,
            obj.end_mark.column,
        )

    def get_sub_parameters(self, sub_string):
        """Gets the parameters out of a Sub String"""
        results = []
        if not isinstance(sub_string, str):
            return results
        regex = re.compile(r"\${[^!].*?}")
        string_params = regex.findall(sub_string)

        for string_param in string_params:
            results.append(string_param[2:-1].strip())

        return results

    def get_location_yaml(self, text, path):
        """
        Get the location information
        """
        result = None
        if not path:
            result = self._loc(text)
        elif len(path) > 1:
            try:
                result = self.get_location_yaml(text[path[0]], path[1:])
            except KeyError:
                pass
            # TypeError will help catch string indices must be integers for when
            # we parse JSON string and get a path inside that json string
            except TypeError:
                pass
            if not result:
                try:
                    for key in text:
                        if key == path[0]:
                            result = self._loc(key)
                except AttributeError as err:
                    LOGGER.debug(err)
        else:
            # If the last item of the path is an integer, and the vaue is an array,
            # Get the location of the item in the array
            if isinstance(text, list) and isinstance(path[0], int):
                try:
                    result = self._loc(text[path[0]])
                except AttributeError as err:
                    LOGGER.debug(err)
            else:
                try:
                    for key in text:
                        if key == path[0]:
                            result = self._loc(key)
                except AttributeError as err:
                    LOGGER.debug(err)

        return result

    # pylint: disable=W0613,too-many-locals
    def check_value(
        self,
        obj,
        key,
        path,
        check_value=None,
        check_ref=None,
        check_get_att=None,
        check_find_in_map=None,
        check_split=None,
        check_join=None,
        check_import_value=None,
        check_sub=None,
        pass_if_null=False,
        **kwargs,
    ):
        matches = []
        values_obj = self.get_values(obj=obj, key=key)
        new_path = path[:] + [key]
        if values_obj is None and pass_if_null:
            if check_value:
                matches.extend(
                    check_value(value=values_obj, path=new_path[:], **kwargs)
                )
        elif not values_obj:
            return matches
        else:
            for value_obj in values_obj:
                value = value_obj["Value"]
                child_path = value_obj["Path"]
                if not isinstance(value, dict):
                    if check_value:
                        matches.extend(
                            check_value(
                                value=value, path=new_path[:] + child_path, **kwargs
                            )
                        )
                else:
                    if len(value) == 1:
                        for dict_name, _ in value.items():
                            # If this is a function we shouldn't fall
                            # back to a check_value check
                            if dict_name in cfnlint.helpers.FUNCTIONS:
                                # convert the function name from camel case
                                # to underscore
                                # Example: Fn::FindInMap becomes
                                # check_find_in_map
                                # ruff: noqa: E501
                                function_name = f'check_{camel_to_snake(dict_name.replace("Fn::", ""))}'
                                if function_name == "check_ref":
                                    if check_ref:
                                        matches.extend(
                                            check_ref(
                                                value=value.get("Ref"),
                                                path=new_path[:] + child_path + ["Ref"],
                                                parameters=self.template.get(
                                                    "Parameters", {}
                                                ),
                                                resources=self.get_resources(),
                                                **kwargs,
                                            )
                                        )
                                else:
                                    if locals().get(function_name):
                                        matches.extend(
                                            locals()[function_name](
                                                value=value.get(dict_name),
                                                path=new_path[:]
                                                + child_path
                                                + [dict_name],
                                                **kwargs,
                                            )
                                        )
                            else:
                                if check_value:
                                    matches.extend(
                                        check_value(
                                            value=value,
                                            path=new_path[:] + child_path,
                                            **kwargs,
                                        )
                                    )
                    else:
                        if check_value:
                            matches.extend(
                                check_value(
                                    value=value, path=new_path[:] + child_path, **kwargs
                                )
                            )

        return matches

    def is_resource_available(self, path, resource):
        """
        Compares a path to resource to see if its available
        Returns scenarios that may result in the resource doesn't exist
        Input:
            Path: An array that is a Path to the object being checked
            Resource: The resource being compared to
        Output:
            If the resource is available the result is an empty array []
            If the resource is not available you will get a an array of Condition Names
                and when that condition is True or False will result in the resource
                not being available when trying to be associated.
                [{'ConditionName'}: False]
        """
        results = []
        path_conditions = self.get_conditions_from_path(self.template, path)
        resource_condition = (
            self.template.get("Resources", {}).get(resource, {}).get("Condition")
        )
        if isinstance(resource_condition, str):
            # if path conditions are empty that means its always true
            if not path_conditions:
                return [{resource_condition: False}]

            # resource conditions are always true.  If the same resource condition
            # exists in the path with the True then nothing else matters
            if True in path_conditions.get(resource_condition, {False}):
                return []

            # resource conditions are always true.  If the same resource condition
            # exists in the path with the False then nothing else matters
            if False in path_conditions.get(resource_condition, {True}):
                return [path_conditions]

            # if any condition paths loop back on themselves with the opposite
            # then its unreachable code
            scenario = {}
            for condition_name, condition_bool in path_conditions.items():
                if len(condition_bool) > 1:
                    return results
                scenario[condition_name] = list(condition_bool)[0]

            if self.conditions.check_implies(scenario, resource_condition):
                return [{**{resource_condition: False}, **scenario}]

        # if resource condition isn't available then the resource is available
        return results

    def get_object_without_nested_conditions(self, obj, path, region=None):
        """
        Get a list of object values without conditions included.
        Evaluates deep into the object removing any nested conditions as well
        """
        results = []
        scenarios = self.get_condition_scenarios_below_path(path, False, region)
        if not isinstance(obj, (dict, list)):
            return results

        def get_value(value, scenario):  # pylint: disable=R0911
            """Get the value based on the scenario resolving nesting"""
            if isinstance(value, dict):
                if len(value) == 1:
                    if "Fn::If" in value:
                        if_values = value.get("Fn::If")
                        if len(if_values) == 3:
                            if_path = scenario.get(if_values[0], None)
                            if if_path is not None:
                                if if_path:
                                    return get_value(if_values[1], scenario)
                                return get_value(if_values[2], scenario)
                    elif value.get("Ref") == "AWS::NoValue":
                        return None

                new_object = {}
                for k, v in value.items():
                    new_v = get_value(v, scenario)
                    if new_v is not None:
                        new_object[k] = get_value(v, scenario)
                return new_object
            if isinstance(value, list):
                new_list = []
                for item in value:
                    new_value = get_value(item, scenario)
                    if new_value is not None:
                        new_list.append(get_value(item, scenario))

                return new_list

            return value

        if not scenarios:
            if isinstance(obj, dict):
                if len(obj) == 1:
                    if obj.get("Ref") == "AWS::NoValue":
                        return [{"Scenario": None, "Object": {}}]
            return [{"Scenario": None, "Object": get_value(obj, {})}]

        for scenario in scenarios:
            results.append({"Scenario": scenario, "Object": get_value(obj, scenario)})

        return results

    def get_value_from_scenario(self, obj, scenario):
        """
        Get object values from a provided scenario
        """

        def get_value(value, scenario):  # pylint: disable=R0911
            """Get the value based on the scenario resolving nesting"""
            if isinstance(value, dict):
                if len(value) == 1:
                    if "Fn::If" in value:
                        if_values = value.get("Fn::If")
                        if len(if_values) == 3:
                            if_path = scenario.get(if_values[0], None)
                            if if_path is not None:
                                if if_path:
                                    return get_value(if_values[1], scenario)
                                return get_value(if_values[2], scenario)
                    elif value.get("Ref") == "AWS::NoValue":
                        return None
                    else:
                        return value

                return value
            if isinstance(value, list):
                new_list = []
                for item in value:
                    new_value = get_value(item, scenario)
                    if new_value is not None:
                        new_list.append(get_value(item, scenario))

                return new_list

            return value

        if isinstance(obj, dict):
            result = dict_node({}, obj.start_mark, obj.end_mark)
            if len(obj) == 1:
                if obj.get("Fn::If"):
                    new_value = get_value(obj, scenario)
                    if new_value is not None:
                        result = new_value
                else:
                    for key, value in obj.items():
                        new_value = get_value(value, scenario)
                        if new_value is not None:
                            result[key] = new_value
            else:
                for key, value in obj.items():
                    new_value = get_value(value, scenario)
                    if new_value is not None:
                        result[key] = new_value
            return result
        if isinstance(obj, list):
            result = list_node({}, obj.start_mark, obj.end_mark)
            for item in obj:
                element = get_value(item, scenario)
                if element is not None:
                    result.append(element)

            return result

        return obj

    def get_object_without_conditions(self, obj, property_names=None, region=None):
        """
        Gets a list of object values without conditions included
        Input:
            obj: The object/dict that makes up a set of properties
            Example:
                {
                    "DBSnapshotIdentifier" : {
                        "Fn::If" : [
                            "UseDBSnapshot",
                            {"Ref" : "DBSnapshotName"},
                            {"Ref" : "AWS::NoValue"}
                        ]
                    }
                }
        Output:
            A list of objects with scenarios for the conditions played out.
            If Ref to AWS::NoValue remove the property
            Example: [
                {
                    Object: {
                        "DBSnapshotIdentifier" : {"Ref" : "DBSnapshotName"}
                    },
                    Scenario: {UseDBSnapshot: True}
                }, {
                    Object: {
                    },
                    Scenario: {UseDBSnapshot: False}
                }
            ]
        """
        if not isinstance(obj, (dict, list)):
            return [{"Scenario": None, "Object": obj}]
        property_names = [] if property_names is None else property_names
        if getattr(obj, "start_mark", None):
            start_mark = obj.start_mark
            end_mark = obj.end_mark
        else:
            start_mark = (0, 0)
            end_mark = (0, 0)
        if isinstance(obj, list):
            o = list_node(deepcopy(obj), start_mark=start_mark, end_mark=end_mark)
        else:
            if property_names:
                o = dict_node({}, start_mark=start_mark, end_mark=end_mark)
                for property_name in property_names:
                    o[property_name] = deepcopy(obj.get(property_name))
            else:
                o = dict_node(deepcopy(obj), start_mark=start_mark, end_mark=end_mark)

        results = []

        scenarios = self.get_conditions_scenarios_from_object(o, region)

        if isinstance(obj, list):
            if not scenarios:
                return [
                    {"Scenario": None, "Object": self.get_value_from_scenario(o, {})}
                ]
            for scenario in scenarios:
                result_list = []
                for o in obj:
                    result_obj = self.get_value_from_scenario(o, scenario)
                    if result_obj:
                        result_list.append(result_obj)
                results.append({"Scenario": scenario, "Object": result_list})
        if isinstance(obj, dict):
            if not scenarios:
                if len(obj) == 1:
                    if obj.get("Ref") == "AWS::NoValue":
                        return []
                return [
                    {"Scenario": None, "Object": self.get_value_from_scenario(o, {})}
                ]

            for scenario in scenarios:
                result_obj = self.get_value_from_scenario(o, scenario)
                if result_obj:
                    results.append({"Scenario": scenario, "Object": result_obj})

        return results

    def get_condition_scenarios_below_path(
        self, path, include_if_in_function=False, region=None
    ):
        """
        get Condition Scenarios from below path
        """
        fn_ifs = self.search_deep_keys("Fn::If")
        results = {}
        for fn_if in fn_ifs:
            if len(fn_if) >= len(path):
                if path == fn_if[0 : len(path)]:
                    # This needs to handle items only below the Path
                    result = self.get_conditions_from_path(
                        self.template, fn_if[0:-1], True, include_if_in_function
                    )
                    for condition_name, condition_values in result.items():
                        if condition_name in results:
                            results[condition_name].union(condition_values)
                        else:
                            results[condition_name] = condition_values

        return list(self.conditions.build_scenarios(results, region))

    def get_conditions_scenarios_from_object(self, objs, region=None):
        """
        Get condition from objects
        """

        def get_conditions_from_property(value):
            """Recursively get conditions"""
            results = set()
            if isinstance(value, dict):
                if len(value) == 1:
                    for k, v in value.items():
                        if k == "Fn::If":
                            if isinstance(v, list) and len(v) == 3:
                                if isinstance(v[0], str):
                                    results.add(v[0])
                                    results = results.union(
                                        get_conditions_from_property(v[1])
                                    )
                                    results = results.union(
                                        get_conditions_from_property(v[2])
                                    )
            elif isinstance(value, list):
                for v in value:
                    results = results.union(get_conditions_from_property(v))

            return results

        con = set()

        if isinstance(objs, dict):
            objs = [objs]

        for obj in objs:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    # handle conditions directly under the object
                    if len(obj) == 1 and k == "Fn::If" and len(v) == 3:
                        con.add(v[0])
                        for r_c in v[1:]:
                            if isinstance(r_c, dict):
                                for s_k, s_v in r_c.items():
                                    if s_k == "Fn::If":
                                        con = con.union(
                                            get_conditions_from_property({s_k: s_v})
                                        )
                    else:
                        con = con.union(get_conditions_from_property(v))

        return list(self.conditions.build_scenarios(dict.fromkeys(list(con)), region))

    def get_conditions_from_path(
        self,
        text,
        path,
        include_resource_conditions=True,
        include_if_in_function=True,
        only_last=False,
    ):
        """
        Parent function to handle resources with conditions.
        Input:
            text: The object to start processing through the Path
            path: The path to recursively look for
        Output:
            An Object with keys being the Condition Names and the values are what
                if its in the True or False part of the path.
                {'condition': {True}}
        """

        results = self._get_conditions_from_path(
            text, path, include_if_in_function, only_last
        )
        if include_resource_conditions:
            if len(path) >= 2:
                if path[0] in ["Resources", "Outputs"]:
                    condition = text.get(path[0], {}).get(path[1], {}).get("Condition")
                    if isinstance(condition, str):
                        if not results.get(condition):
                            results[condition] = set()
                        results[condition].add(True)

        return results

    def _get_conditions_from_path(
        self, text, path, include_if_in_function=True, only_last=False
    ):
        """
        Get the conditions and their True/False value for the path provided
        Input:
            text: The object to start processing through the Path
            path: The path to recursively look for
        Output:
            An Object with keys being the Condition Names and the values are what
                if its in the True or False part of the path.
                {'condition': {True}}
        """
        results = {}

        def get_condition_name(value, num=None):
            """Test conditions for validity before providing the name"""
            con_path = set()
            if num == 1:
                con_path.add(True)
            elif num == 2:
                con_path.add(False)
            else:
                con_path = con_path.union((True, False))

            if value:
                if isinstance(value, list):
                    if len(value) == 3:
                        if not results.get(value[0]):
                            results[value[0]] = set()
                        results[value[0]] = results[value[0]].union(con_path)

        try:
            # Found a condition at the root of the Path
            if path[0] == "Fn::If" and (
                (len(path) == 1 and only_last) or not only_last
            ):
                condition = text.get("Fn::If")
                if len(path) > 1:
                    if path[1] in [1, 2]:
                        get_condition_name(condition, path[1])
                else:
                    get_condition_name(condition)
            # Iterate if the Path has more than one value
            if len(path) > 1:
                if (
                    path[0] in cfnlint.helpers.FUNCTIONS and path[0] != "Fn::If"
                ) and not include_if_in_function:
                    return results
                child_results = self._get_conditions_from_path(
                    text[path[0]], path[1:], include_if_in_function, only_last
                )
                for c_r_k, c_r_v in child_results.items():
                    if not results.get(c_r_k):
                        results[c_r_k] = set()
                    results[c_r_k] = results[c_r_k].union(c_r_v)

        except KeyError:
            pass

        return results


def camel_to_snake(s):
    """
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    _underscorer1 = re.compile(r"(.)([A-Z][a-z]+)")
    _underscorer2 = re.compile("([a-z0-9])([A-Z])")
    subbed = _underscorer1.sub(r"\1_\2", s)
    return _underscorer2.sub(r"\1_\2", subbed).lower()
