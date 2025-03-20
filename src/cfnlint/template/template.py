"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import functools
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Iterator

import regex as re

import cfnlint.conditions
import cfnlint.helpers
from cfnlint._typing import CheckValueFn, Path
from cfnlint.context import Context, create_context_for_template
from cfnlint.context.conditions.exceptions import Unsatisfiable
from cfnlint.decode.node import dict_node, list_node
from cfnlint.graph import Graph
from cfnlint.match import Match
from cfnlint.template.getatts import GetAtts
from cfnlint.template.transforms import Transform

if TYPE_CHECKING:
    from cfnlint.rules import RuleMatch

LOGGER = logging.getLogger(__name__)


class Template:  # pylint: disable=R0904,too-many-lines,too-many-instance-attributes
    """
    Class representing a CloudFormation template.

    This class provides methods to access and manipulate various parts of the template,
    such as resources, parameters, conditions, and transformations. It also includes
    utility methods for checking conditions, resolving references, and more.

    Attributes:
        regions (list[str]): A list of AWS regions associated with the template.
        filename (str | None): The filename of the template file, if available.
        template (dict[str, Any]): The dictionary representing the CloudFormation template.
        sections (list[str]): A list of CloudFormation template sections.
        transform_pre (dict[str, Any]): A dictionary containing pre-processed transformation data.
        conditions (Conditions): An instance of the Conditions class used for managing conditions.
        graph (Graph): An instance of the Graph class used for representing the template structure.
    """

    def __init__(
        self,
        filename: str | None,
        template: dict[str, Any],
        regions: list[str] | None = None,
    ):
        """Initialize a Template instance.

        Args:
            filename (str | None): The filename of the template file, if available.
            template (dict[str, Any]): The dictionary representing the CloudFormation template.
            regions (list[str] | None): A list of AWS regions associated with the template.
        """
        if regions is None:
            self.regions = [cfnlint.helpers.REGION_PRIMARY]
        else:
            self.regions = regions
        self.filename = filename
        self.template = template
        self.transform_pre: dict[str, Any] = {}
        self.transform_pre["Globals"] = {}
        self.transform_pre["Ref"] = self.search_deep_keys("Ref")
        self.transform_pre["Fn::Sub"] = self.search_deep_keys("Fn::Sub")
        self.transform_pre["Fn::If"] = self.search_deep_keys("Fn::If")
        self.transform_pre["Fn::FindInMap"] = self.search_deep_keys("Fn::FindInMap")
        self.transform_pre["Transform"] = cfnlint.helpers.ensure_list(
            self.template.get("Transform", [])
        )
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

    def transform(self) -> list[Match]:
        """
        Transform the template.

        Returns:
            list[Match]: A list of Match objects representing the transformed template.
        """
        transform = Transform()
        results = transform.transform(self)
        self._cache_clear()
        return results

    def build_graph(self) -> None:
        """Generates a DOT representation of the template"""
        filename = self.filename or "cfn-lint"
        path = filename + ".dot"
        if not self.graph:
            return
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

    def has_language_extensions_transform(self) -> bool:
        """Check if the template has the AWS::LanguageExtensions transform declared.

        Returns:
            bool: True if the AWS::LanguageExtensions transform is declared, False otherwise.
        """
        return bool(
            cfnlint.helpers.TRANSFORM_LANGUAGE_EXTENSION
            in self.transform_pre["Transform"]
        )

    def has_serverless_transform(self) -> bool:
        """Check if the template has the AWS::Serverless-2016-10-31 transform declared.

        Returns:
            bool: True if the AWS::Serverless-2016-10-31 transform is declared, False otherwise.
        """
        return bool(cfnlint.helpers.TRANSFORM_SAM in self.transform_pre["Transform"])

    def is_cdk_template(self) -> bool:
        """Check if the template was created by the AWS Cloud Development Kit (CDK).

        Returns:
            bool: True if the template was created by CDK, False otherwise.
        """
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

    def get_resources(
        self, resource_type: list[str] | str = []
    ) -> dict[str, dict[str, Any]]:
        """Get the resources in the template.

        Args:
            resource_type (list[str] | str): An optional list or string of resource types to filter by.

        Returns:
            dict[str, dict[str, Any]]: A dictionary containing the resources, where the keys are resource names
                and the values are the resource dictionaries.
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

    def get_resource_children(
        self, resource_name: str, types: list[str] | None = None
    ) -> Iterator[str]:
        """Get the resource children for a given resource name.

        Args:
            resource_name (str): The name of the resource.
            types (list[str] | None): An optional list of resource types to filter by.

        Yields:
            str: The name of each resource child.
        """
        types = types or []

        if self.graph:
            for node_name in self.graph.graph.predecessors(resource_name):
                node = self.graph.graph.nodes[node_name]
                if node["type"] != "Resource":
                    continue

                if types:
                    if node["resource_type"] in types:
                        yield node_name
                else:
                    yield node_name

    def get_parameters_valid(self) -> dict[str, dict[str, Any]]:
        """Get the valid parameters in the template.

        Returns:
            dict[str, dict[str, Any]]: A dictionary containing the valid parameters, where the keys are parameter names
                and the values are the parameter dictionaries.
        """
        result = {}
        if isinstance(self.template.get("Parameters"), dict):
            parameters = self.template.get("Parameters", {})
            for parameter_name, parameter_value in parameters.items():
                if isinstance(parameter_value, dict):
                    if isinstance(parameter_value.get("Type"), str):
                        result[parameter_name] = parameter_value

        return result

    def get_modules(self) -> dict[str, dict[str, Any]]:
        """Get the modules in the template.

        Returns:
            dict[str, dict[str, Any]]: A dictionary containing the modules, where the keys are module names
                and the values are the module dictionaries.
        """
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
        """Get a dictionary of valid references in the template.

        Returns:
            cfnlint.helpers.RegexDict: A dictionary containing valid references, where the keys are reference names
                and the values are dictionaries with information about the reference type and source.
        """
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

    def get_valid_getatts(self) -> GetAtts:
        """Get an instance of GetAtts containing valid GetAtt references in the template.

        Returns:
            GetAtts: An instance of GetAtts containing valid GetAtt references.
        """
        results = GetAtts(self.regions)

        for name, value in self.context.resources.items():
            results.add(name, value)

        return results

    def get_directives(self) -> dict[str, list[str]]:
        """Get the directives (ignore_checks) in the template.

        Returns:
            dict[str, list[str]]: A dictionary containing directives, where the keys are directive names
                and the values are lists of resource names associated with the directive.
        """
        results: dict[str, list[str]] = {}
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
    def _search_deep_keys(self, searchText: str | re.Pattern, cfndict, path: Path):
        """Search deep for keys and get their values.

        Args:
            searchText (str | re.Pattern): The text or regular expression pattern to search for.
            cfndict (Any): The dictionary or list to search in.
            path (list[Any]): The current path in the dictionary or list.

        Returns:
            list[list[Any]]: A list of paths where the searchText was found.
        """
        keys = []
        if isinstance(cfndict, dict):
            for key in cfndict:
                pathprop: Path = path[:]
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
        """Search for a key in all parts of the template.

        Args:
            searchText (str | re.Pattern): The text or regular expression pattern to search for.
            includeGlobals (bool): Whether to include globals in the search.

        Returns:
            liist[[Any]]: A list of paths where the searchText was found.

        Example:
            If searchText is "Ref", the return value could be something like
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

    def get_cfn_path(
        self, path: list[str], context: Context
    ) -> Iterator[tuple[Any, Context]]:
        """
        Get the value at the specified path in the CloudFormation template.

        Args:
            path (list[str]): The path to the value in the template.
            context (Context): The context object containing the template and other data.

        Returns:
            Any: The value at the specified path in the template.
        """

        def _filter_condition(
            template: Any, context: Context
        ) -> Iterator[tuple[Any, Context]]:
            k, v = cfnlint.helpers.is_function(template)
            if k is None:
                yield template, context
                return

            if k == "Fn::If":
                if isinstance(v, list) and len(v) == 3:
                    condition = v[0]
                    if not isinstance(condition, str):
                        return

                    for i in [1, 2]:
                        b = True if i == 1 else False
                        try:
                            item_context = context.evolve(
                                conditions=context.conditions.evolve({condition: b})
                            )
                            yield from _filter_condition(v[i], item_context)
                        except Unsatisfiable:
                            continue
                return
            if k == "Ref":
                if v == "AWS::NoValue":
                    return
            yield template, context

        def _get_cfn_path(
            path: list[str], template: Any, context: Context
        ) -> Iterator[tuple[Any, Context]]:
            if len(path) == 0:
                yield from _filter_condition(template, context)
                return
            item = path[0]
            if isinstance(template, dict):
                if item in template:
                    for item_template, item_context in _filter_condition(
                        template[item], context
                    ):
                        yield from _get_cfn_path(path[1:], item_template, item_context)
                return
            elif isinstance(template, list):
                if isinstance(template, list):
                    if item == "*":
                        for index, _ in enumerate(template):
                            yield from _get_cfn_path(path[1:], template[index], context)
                return

        # handle resource and output conditions
        if len(path) >= 3 and path[0] in ["Resources", "Outputs"]:
            condition = self.template.get(path[0], {}).get(path[1], {}).get("Condition")
            if condition:
                try:
                    context = context.evolve(
                        conditions=context.conditions.evolve({condition: True})
                    )
                except Unsatisfiable:
                    return

        yield from _get_cfn_path(path, self.template, context)

    def get_condition_values(self, template, path: Path | None) -> list[dict[str, Any]]:
        """
        Evaluates conditions in the provided CloudFormation template and returns the values.

        Args:
            template (list): The CloudFormation template to evaluate.
            path (list, optional): The current path in the template. Defaults to an empty list.

        Returns:
            list: A list of dictionaries, where each dictionary contains the following keys:
                - "Path": The path to the condition value in the template.
                - "Value": The value of the condition.
        """
        path = path or []
        matches: list[dict[str, Any]] = []
        if not isinstance(template, list):
            return matches
        if not len(template) == 3:
            return matches

        for index, item in enumerate(template[1:]):
            result: dict[str, Any] = {}
            result["Path"] = path[:] + [index + 1]
            if not isinstance(item, (dict, list)):
                # Just straight values and pass them through
                result["Value"] = item
                matches.append(result)
            elif len(item) == 1:
                # Checking for conditions inside of conditions
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        if sub_key == cfnlint.helpers.FUNCTION_IF:
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

    def get_values(self, obj, key, path: Path | None = None):
        """
        Logic for getting the value of a key in the provided object.

        Args:
            obj (dict): The object to search for the key.
            key (str): The key to search for in the object.
            path (list, optional): The current path in the object. Defaults to an empty list.

        Returns:
            list: A list of dictionaries, where each dictionary contains the following keys:
            - "Path": The path to the value in the object.
            - "Value": The value found for the key.

            Types of return values
            - Returns None if the item isn't found
            - Returns empty list if the item is found but Ref or GetAtt
            - Returns all the values as a list if condition
            - Returns the value if its just a string, int, boolean, etc.
        """
        path = path or []
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
                    if obj_key == cfnlint.helpers.FUNCTION_IF:
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
                            if obj_key == cfnlint.helpers.FUNCTION_IF:
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

    def _loc(self, obj: Any) -> tuple[int, int, int, int]:
        """Return location of object"""
        return (
            obj.start_mark.line,
            obj.start_mark.column,
            obj.end_mark.line,
            obj.end_mark.column,
        )

    def get_sub_parameters(self, sub_string):
        """
        Gets the parameters out of a Sub String.

        Args:
            sub_string (str): The Sub string to extract parameters from.

        Returns:
            list: A list of the parameter names found in the Sub string.
        """
        results = []
        if not isinstance(sub_string, str):
            return results
        regex = re.compile(r"\${[^!].*?}")
        string_params = regex.findall(sub_string)

        for string_param in string_params:
            results.append(string_param[2:-1].strip())

        return results

    def get_location_yaml(self, text: Any, path: Path):
        """
        Get the location information for the given YAML text and path.

        Args:
            text (str): The YAML text to search.
            path (list): The path to the location within the YAML text.

        Returns:
            dict or None: A dictionary containing the location information, or None if the location could not be found.
            The dictionary has the following keys:
                - "start_mark": A dictionary with "line" and "column" keys indicating the start of the location.
                - "end_mark": A dictionary with "line" and "column" keys indicating the end of the location.
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
        obj: dict[str, Any],
        key: str,
        path: Path,
        check_value: CheckValueFn | None = None,
        check_ref: CheckValueFn | None = None,
        check_get_att: CheckValueFn | None = None,
        check_find_in_map: CheckValueFn | None = None,
        check_split: CheckValueFn | None = None,
        check_join: CheckValueFn | None = None,
        check_import_value: CheckValueFn | None = None,
        check_sub: CheckValueFn | None = None,
        pass_if_null: bool = False,
        **kwargs: dict[str, Any],
    ) -> list[RuleMatch]:
        """
        Check the value of a key in the provided object.

        Args:
            obj (dict): The object to check the value of.
            key (str): The key to check the value of.
            path (list): The path to the current location in the object.
            check_value (callable, optional): A function to check the value of the key.
            check_ref (callable, optional): A function to check the "Ref" function.
            check_get_att (callable, optional): A function to check the "Fn::GetAtt" function.
            check_find_in_map (callable, optional): A function to check the "Fn::FindInMap" function.
            check_split (callable, optional): A function to check the "Fn::Split" function.
            check_join (callable, optional): A function to check the "Fn::Join" function.
            check_import_value (callable, optional): A function to check the "Fn::ImportValue" function.
            check_sub (callable, optional): A function to check the "Fn::Sub" function.
            pass_if_null (bool, optional): Whether to pass if the value is null. Defaults to False.
            **kwargs (dict): Additional keyword arguments to pass to the check functions.

        Returns:
            list[RuleMatch]: A list of matches found during the check.
        """
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

    def is_resource_available(self, path: Path, resource: str) -> list[dict[str, bool]]:
        """
        Compares a path to a resource to see if it is available.

        This function returns scenarios that may result in the resource not existing.

        Args:
            path (list): An array that is a path to the object being checked.
            resource (str): The resource being compared.

        Returns:
            list: If the resource is available, the result is an empty list [].
                If the resource is not available, the function returns a list of dictionaries,
                where each dictionary represents a scenario where the resource is not available.
                The dictionary keys are the condition names, and the values indicate whether
                the condition is True or False.
        """
        results: list[dict[str, bool]] = []
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
                return [{resource_condition: False}]

            # if any condition paths loop back on themselves with the opposite
            # then its unreachable code
            scenario = {}
            for condition_name, condition_bool in path_conditions.items():
                if len(condition_bool) > 1:
                    return results
                scenario[condition_name] = list(condition_bool)[0]

            if not self.conditions.check_implies(scenario, resource_condition):
                return [{**{resource_condition: False}, **scenario}]

        # if resource condition isn't available then the resource is available
        return results

    def get_object_without_nested_conditions(
        self, obj: dict | list, path: Path, region: str | None = None
    ):
        """
        Get a list of object values without conditions included.

        Evaluates deep into the object removing any nested conditions as well.

        Args:
            obj (dict): The object to process.
            path (list): The current path in the object.
            region (str, optional): The AWS region to use for evaluating conditions. Defaults to None.

        Returns:
            list: A list of dictionaries, where each dictionary contains the following keys:
                - "Scenario": The scenario for the object, or None if there are no conditions.
                - "Object": The object with conditions removed.
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
        Get object values from a provided scenario.

        This function recursively processes the provided object, resolving any
        conditional logic (such as Fn::If) based on the given scenario.

        Args:
            obj (dict): The object to process.
            scenario (dict): The scenario to use when resolving conditional logic.

        Returns:
            dict or list or any: The processed object, with conditional logic resolved.
            The return type can be a dictionary, list, or any other data type,
            depending on the structure of the input object.
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
            result = list_node([], obj.start_mark, obj.end_mark)
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
        self,
        path: Path,
        include_if_in_function: bool = False,
        region: str | None = None,
    ) -> list[dict[str, bool]]:
        """
        Get all possible scenarios for the conditions in the provided object.

        This function recursively processes the object, identifying any conditional
        logic (such as Fn::If) and generating all possible scenarios based on the
        conditions.

        Args:
            obj (dict): The object to process.
            region (str, optional): The AWS region to use for evaluating conditions. Defaults to None.

        Returns:
            list: A list of dictionaries, where each dictionary represents a possible
            scenario. The keys in the dictionary are the condition names, and the
            values are boolean values indicating whether the condition is True or False.
        """
        fn_ifs = self.search_deep_keys("Fn::If")
        results: dict[str, set] = {}
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
        Get the conditions that are applicable for the given path in the template.

        This function recursively traverses the template, following the provided path,
        and collects all the conditions that are relevant for the given path.

        Args:
            template (dict): The CloudFormation template to analyze.
            path (list): The path within the template to analyze.

        Returns:
            dict: A dictionary where the keys are the condition names, and the values
            are sets of boolean values (True or False) indicating the possible
            outcomes for that condition.
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
        text: Any,
        path: Path,
        include_resource_conditions: bool = True,
        include_if_in_function: bool = True,
        only_last: bool = False,
    ) -> dict[str, set[bool]]:
        """
        Parent function to handle resources with conditions.

        This function recursively processes the provided text and path to identify
        the conditions that are relevant for the given path.

        Args:
            text (dict): The object to start processing through the path.
            path (list): The path to recursively look for conditions.
            include_resource_conditions (bool, optional): Whether to include conditions
                from the resource itself. Defaults to True.
            include_if_in_function (bool, optional): Whether to include conditions
                from Fn::If functions. Defaults to True.
            only_last (bool, optional): Whether to only return the conditions for the
                last element in the path. Defaults to False.

        Returns:
            dict: A dictionary where the keys are the condition names, and the values
            are sets of boolean values (True or False) indicating the possible
            outcomes for that condition.
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
        self,
        text: Any,
        path: Path,
        include_if_in_function: bool = True,
        only_last: bool = False,
    ) -> dict[str, set[bool]]:
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
        results: dict[str, set[bool]] = {}

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
