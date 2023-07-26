"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule, RuleMatch


class FindInMap(CloudFormationLintRule):
    """Check if FindInMap values are correct"""

    id = "E1011"
    shortdesc = "FindInMap validation of configuration"
    description = "Making sure the function is a list of appropriate config"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html"
    tags = ["functions", "findinmap"]

    supported_functions = ["Fn::FindInMap", "Ref"]
    enhanced_supported_functions = [
        "Fn::FindInMap",
        "Ref",
        "Fn::Select",
        "Fn::Split",
        "Fn::Join",
        "Fn::Sub",
        "Fn::If",
        "Fn::Length",
        "Fn::ToJsonString",
        "Fn::Sub",
    ]
    default_value_key = "DefaultValue"

    def check_dict(self, obj, tree):
        """
        Check that obj is a dict with Ref as the only key
        Mappings only support Ref inside them
        """
        matches = []

        if isinstance(obj, dict):
            if len(obj) == 1:
                for key_name, _ in obj.items():
                    if key_name not in self.supported_functions:
                        message = "FindInMap only supports [{0}] functions at {1}"
                        matches.append(
                            RuleMatch(
                                tree[:] + [key_name],
                                message.format(
                                    ", ".join(map(str, self.supported_functions)),
                                    "/".join(map(str, tree)),
                                ),
                            )
                        )
            else:
                message = (
                    "FindInMap only supports an object of 1 of [{0}] functions at {1}"
                )
                matches.append(
                    RuleMatch(
                        tree[:],
                        message.format(
                            ", ".join(map(str, self.supported_functions)),
                            "/".join(map(str, tree)),
                        ),
                    )
                )

        return matches

    def map_name(self, map_name, mappings, tree):
        """Check the map name"""
        matches = []
        if isinstance(map_name, (str, dict)):
            if isinstance(map_name, dict):
                matches.extend(self.check_dict(map_name, tree[:] + [0]))
            else:
                if map_name not in mappings:
                    message = "Map Name {0} does not exist for {0}"
                    matches.append(
                        RuleMatch(
                            tree[:] + [0],
                            message.format(map_name, "/".join(map(str, tree))),
                        )
                    )
        else:
            message = "Map Name should be a {0}, or string at {1}"
            matches.append(
                RuleMatch(
                    tree[:] + [0],
                    message.format(
                        ", ".join(map(str, self.supported_functions)),
                        "/".join(map(str, tree)),
                    ),
                )
            )

        return matches

    def match_key(self, key, tree, key_name, key_index):
        """Check the validity of a key"""
        matches = []
        if isinstance(key, (str, int)):
            return matches
        if isinstance(key, dict):
            matches.extend(self.check_dict(key, tree[:] + [key_index]))
        else:
            message = "FindInMap {0} should be a {1}, string, or int at {2}"
            matches.append(
                RuleMatch(
                    tree[:] + [key_index],
                    message.format(
                        key_name,
                        ", ".join(map(str, self.supported_functions)),
                        "/".join(map(str, tree)),
                    ),
                )
            )

        return matches

    def validate_intrinsic_function(self, obj, tree):
        matches = []
        if not isinstance(obj, dict):
            return matches
        error_message = (
            "FindInMap only supports an object of 1 of [{0}] functions at {1}"
        )
        if len(obj) != 1:
            matches.append(
                RuleMatch(
                    tree[:],
                    error_message.format(
                        "/".join(map(str, self.enhanced_supported_functions)),
                        "/".join(map(str, tree)),
                    ),
                )
            )
            return matches
        function_name = next(iter(obj))
        if function_name not in self.enhanced_supported_functions:
            matches.append(
                RuleMatch(
                    tree[:],
                    error_message.format(
                        "/".join(map(str, self.enhanced_supported_functions)),
                        "/".join(map(str, tree)),
                    ),
                )
            )
        return matches

    def validate_enhanced_map_name(self, map_name, mappings, tree):
        matches = []
        if isinstance(map_name, str):
            if map_name not in mappings:
                error_message = "Map Name {0} does not exist for {1}"
                matches.append(
                    RuleMatch(
                        tree[:] + [0],
                        error_message.format(map_name, "/".join(map(str, tree))),
                    )
                )
        elif isinstance(map_name, dict):
            return self.validate_intrinsic_function(map_name, tree)
        else:
            error_message = "Map Name should be an intrinsic function that resolves to a string, or a string at {0}"
            matches.append(
                RuleMatch(tree[:] + [0], error_message.format("/".join(map(str, tree))))
            )
        return matches

    def validate_enhanced_key(self, key, tree, key_name, key_index):
        matches = []
        if isinstance(key, (str, int)):
            return matches
        if isinstance(key, dict):
            return self.validate_intrinsic_function(key, tree)
        error_message = "FindInMap {0} should be a string, int or an intrinsic function resolves to a string or int at {1}"
        matches.append(
            RuleMatch(
                tree[:] + [key_index],
                error_message.format(key_name, "/".join(map(str, tree))),
            )
        )
        return matches

    def validate_default_value_shape(self, default_value, tree):
        matches = []
        error_message = "Fn::FindInMap default value must be an object whose key is 'DefaultValue' at {0}"
        if (not isinstance(default_value, dict)) or (len(default_value) != 1):
            matches.append(
                RuleMatch(tree[:], error_message.format("/".join(map(str, tree))))
            )
            return matches
        key = next(iter(default_value))
        if key != self.default_value_key:
            matches.append(
                RuleMatch(tree[:], error_message.format("/".join(map(str, tree))))
            )
        return matches

    def validate_enhanced_default_value(self, default_value_dict, tree):
        matches = []
        matches.extend(self.validate_default_value_shape(default_value_dict, tree))
        if not isinstance(default_value_dict, dict):
            return matches
        if self.default_value_key not in default_value_dict:
            return matches
        default_value = default_value_dict[self.default_value_key]
        if isinstance(default_value, (int, float, str)):
            return matches
        if isinstance(default_value, dict):
            matches.extend(self.validate_intrinsic_function(default_value, tree))
        if isinstance(default_value, list):
            for value in default_value:
                if isinstance(value, dict):
                    matches.extend(self.validate_intrinsic_function(value, tree))
                elif isinstance(value, (int, float, str)):
                    continue
                else:
                    error_message = "Elements in Fn::FindInMap default value must be a string, number or an intrinsic function resolves to string at {0}"
                    matches.append(
                        RuleMatch(
                            tree[:], error_message.format("/".join(map(str, tree)))
                        )
                    )
        return matches

    def validate_enhanced_find_in_map(self, find_in_map, cfn):
        mappings = cfn.get_mappings()
        tree = find_in_map[:-1]
        map_obj = find_in_map[-1]
        matches = []
        if not isinstance(map_obj, list):
            error_message = "FindInMap is a list with 3 or 4 values for {0}"
            matches.append(
                RuleMatch(tree[:], error_message.format("/".join(map(str, tree))))
            )
            return matches
        if len(map_obj) in (3, 4):
            map_name = map_obj[0]
            first_key = map_obj[1]
            second_key = map_obj[2]
            matches.extend(self.validate_enhanced_map_name(map_name, mappings, tree))
            matches.extend(self.validate_enhanced_key(first_key, tree, "first key", 1))
            matches.extend(
                self.validate_enhanced_key(second_key, tree, "second key", 2)
            )
            if len(map_obj) == 4:
                default_value = map_obj[3]
                matches.extend(
                    self.validate_enhanced_default_value(default_value, tree)
                )
        else:
            error_message = "FindInMap is a list with 3 or 4 values for {0}"
            matches.append(
                RuleMatch(tree[:] + [1], error_message.format("/".join(map(str, tree))))
            )
        return matches

    def _match_with_language_extensions(self, cfn):
        matches = []
        find_in_maps = cfn.transform_pre["Fn::FindInMap"]
        for in_map in find_in_maps:
            matches.extend(
                self.validate_enhanced_find_in_map(find_in_map=in_map, cfn=cfn)
            )
        return matches

    def _match(self, cfn):
        matches = []

        findinmaps = cfn.search_deep_keys("Fn::FindInMap")
        mappings = cfn.get_mappings()
        for findinmap in findinmaps:
            tree = findinmap[:-1]
            map_obj = findinmap[-1]
            if not isinstance(map_obj, list):
                message = "FindInMap is a list with 3 values for {0}"
                matches.append(RuleMatch(tree[:], message.format("/".join(tree))))
                continue
            if len(map_obj) == 3:
                map_name = map_obj[0]
                first_key = map_obj[1]
                second_key = map_obj[2]

                matches.extend(self.map_name(map_name, mappings, tree))
                matches.extend(self.match_key(first_key, tree, "first key", 1))
                matches.extend(self.match_key(second_key, tree, "second key", 2))

            else:
                message = "FindInMap is a list with 3 values for {0}"
                matches.append(
                    RuleMatch(tree[:] + [1], message.format("/".join(map(str, tree))))
                )

        return matches

    def match(self, cfn):
        if cfn.has_language_extensions_transform():
            return self._match_with_language_extensions(cfn=cfn)
        return self._match(cfn=cfn)
