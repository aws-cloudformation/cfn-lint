"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

from cfnlint.data import CloudSpecs
from cfnlint.helpers import RESOURCE_SPECS, load_resource


class TestPatchedSpecs(BaseTestCase):
    """Test Patched spec files"""

    found_value_types = []

    def setUp(self):
        """SetUp template object"""

        self.spec = RESOURCE_SPECS["us-east-1"]

    def _test_property_type_values(self, values, r_name, p_name, r_type):
        p_value_type = values.get("Value", {}).get("ValueType")
        if p_value_type:
            self.found_value_types.append(p_value_type)
            self.assertIn(
                p_value_type,
                self.spec.get("ValueTypes"),
                "%s: %s, Property: %s. %s not found"
                % (r_type, r_name, p_name, p_value_type),
            )
            # List Value if a singular value is set and the type is List
            if values.get("Type") == "List":
                p_list_value_type = values.get("Value", {}).get("ListValueType")
                if p_list_value_type:
                    self.found_value_types.append(p_list_value_type)
                    self.assertIn(
                        p_list_value_type,
                        self.spec.get("ValueTypes"),
                        "%s: %s, Property: %s. %s not found"
                        % (r_type, r_name, p_name, p_value_type),
                    )

    def test_resource_type_values(self):
        """Test Resource Type Value"""
        r_type = "ResourceTypes"
        for r_name, r_values in self.spec.get("ResourceTypes").items():
            for p_name, p_values in r_values.get("Properties").items():
                self._test_property_type_values(p_values, r_name, p_name, r_type)

    def test_property_type_values(self):
        """Test Property Type Values"""
        r_type = "PropertyTypes"
        for r_name, r_values in self.spec.get(r_type).items():
            if r_values.get("Properties") is None:
                self._test_property_type_values(r_values, r_name, "", r_type)
            else:
                for p_name, p_values in r_values.get("Properties", {}).items():
                    self._test_property_type_values(p_values, r_name, p_name, r_type)

    def _test_sub_properties(self, resource_name, v_propertyname, v_propertyvalues):
        property_types = self.spec.get("PropertyTypes").keys()
        if (
            "PrimitiveType" not in v_propertyvalues
            and "PrimitiveItemType" not in v_propertyvalues
        ):
            v_propertytype = ""
            if "ItemType" in v_propertyvalues:
                v_propertytype = v_propertyvalues["ItemType"]
            elif "Type" in v_propertyvalues:
                v_propertytype = v_propertyvalues["Type"]

            v_subproperty_type = str.format("{0}.{1}", resource_name, v_propertytype)

            property_exists = False
            if v_subproperty_type in property_types:
                property_exists = True
            elif v_propertytype in property_types:
                # Special: There is a "Tag" Property type that's used as a "CatchAll" mechanism for Tags,
                # If the subproperty is not found, check if it exists with the resource in the property
                property_exists = True

            self.assertEqual(
                property_exists,
                True,
                "Specified property type {} not found for property {}".format(
                    v_subproperty_type, v_propertyname
                ),
            )

    def test_sub_properties(self):
        """Test Resource sub-Property definitions"""
        # Test properties from resources
        for v_name, v_values in self.spec.get("ResourceTypes").items():
            v_value_properties = v_values.get("Properties", {})
            for p_name, p_values in v_value_properties.items():
                self._test_sub_properties(v_name, p_name, p_values)

        # Test properties from subproperties
        for v_name, v_values in self.spec.get("PropertyTypes").items():
            # Grab the resource part from the subproperty
            resource_name = v_name.split(".", 1)[0]
            if resource_name:
                v_value_properties = v_values.get("Properties", {})
                if v_value_properties is None:
                    self._test_sub_properties(resource_name, "", v_values)
                else:
                    for p_name, p_values in v_value_properties.items():
                        self._test_sub_properties(resource_name, p_name, p_values)

    def test_intrinsic_value_types(self):
        """Test Intrinsic Types"""

        for _, i_value in self.spec.get("IntrinsicTypes").items():
            self.assertIn("Documentation", i_value)
            self.assertIn("ReturnTypes", i_value)
            for return_type in i_value.get("ReturnTypes"):
                self.assertIn(return_type, ["Singular", "List"])

    def test_z_property_value_types(self):
        """Test Property Value Types"""
        for v_name, v_values in self.spec.get("ValueTypes").items():
            self.assertIn(
                v_name,
                self.found_value_types,
                "Value type {} is not used".format(v_name),
            )
            list_count = 0
            number_count = 0
            string_count = 0

            number_max = 0
            number_min = 0
            for p_name, p_values in v_values.items():
                self.assertIn(
                    p_name,
                    [
                        "Ref",
                        "GetAtt",
                        "AllowedValues",
                        "AllowedPattern",
                        "AllowedPatternRegex",
                        "ListMin",
                        "ListMax",
                        "JsonMax",
                        "NumberMax",
                        "NumberMin",
                        "StringMax",
                        "StringMin",
                    ],
                )

                if p_name == "NumberMin":
                    number_min = p_values
                if p_name == "NumberMax":
                    number_max = p_values
                if p_name in ["ListMin", "ListMax"]:
                    list_count += 1
                if p_name in ["NumberMin", "NumberMax"]:
                    number_count += 1
                if p_name in ["StringMin", "StringMax"]:
                    string_count += 1
                if p_name == "Ref":
                    self.assertIsInstance(
                        p_values, dict, "ValueTypes: %s, Type: %s" % (v_name, p_name)
                    )
                    for r_name, r_value in p_values.items():
                        self.assertIn(
                            r_name,
                            ["Resources", "Parameters"],
                            "ValueTypes: %s, Type: %s, Additional Type: %s"
                            % (v_name, p_name, r_name),
                        )
                        self.assertIsInstance(
                            r_value,
                            list,
                            "ValueTypes: %s, Type: %s, Additional Type: %s"
                            % (v_name, p_name, r_name),
                        )
                        if r_name == "Parameters":
                            for r_list_value in r_value:
                                self.assertIsInstance(
                                    r_list_value,
                                    str,
                                    "ValueTypes: %s, Type: %s, Additional Type: %s"
                                    % (v_name, p_name, r_name),
                                )
                                self.assertIn(
                                    r_list_value,
                                    self.spec.get("ParameterTypes"),
                                    "ValueTypes: %s, Type: %s, Additional Type: %s"
                                    % (v_name, p_name, r_name),
                                )
                        elif r_name == "Resources":
                            for r_list_value in r_value:
                                self.assertIsInstance(
                                    r_list_value,
                                    str,
                                    "ValueTypes: %s, Type: %s, Additional Type: %s"
                                    % (v_name, p_name, r_name),
                                )
                                self.assertIn(
                                    r_list_value,
                                    self.spec.get("ResourceTypes"),
                                    "ValueTypes: %s, Type: %s, Additional Type: %s"
                                    % (v_name, p_name, r_name),
                                )

                elif p_name == "GetAtt":
                    self.assertIsInstance(
                        p_values, dict, "ValueTypes: %s, Type: %s" % (v_name, p_name)
                    )
                    for g_name, g_value in p_values.items():
                        self.assertIsInstance(
                            g_value,
                            (str, list),
                            "ValueTypes: %s, Type: %s, Additional Type: %s"
                            % (v_name, p_name, g_name),
                        )
                        self.assertIn(
                            g_name,
                            self.spec.get("ResourceTypes"),
                            "ValueTypes: %s, Type: %s, Additional Type: %s"
                            % (v_name, p_name, g_name),
                        )
                        values = g_value
                        if isinstance(values, str):
                            values = [values]
                        for value in values:
                            self.assertIn(
                                value,
                                self.spec.get("ResourceTypes", {})
                                .get(g_name, {})
                                .get("Attributes", {}),
                                "ValueTypes: %s, Type: %s, Additional Type: %s"
                                % (v_name, p_name, g_name),
                            )
                elif p_name == "AllowedValues":
                    self.assertIsInstance(p_values, list)
                    for l_value in p_values:
                        self.assertIsInstance(
                            l_value, str, "ValueTypes: %s, Type: %s" % (v_name, p_name)
                        )
            self.assertIn(
                list_count, [0, 2], "Both ListMin and ListMax must be specified"
            )
            self.assertIn(
                number_count, [0, 2], "Both NumberMin and NumberMax must be specified"
            )
            self.assertIn(
                string_count, [0, 2], "Both StringMin and StringMax must be specified"
            )
            if number_count == 2:
                self.assertTrue(
                    (number_max > number_min),
                    "NumberMax must be greater than NumberMin",
                )

    def test_parameter_types(self):
        """Test Parameter Types"""
        aws_parameter_types = [
            "AWS::EC2::AvailabilityZone::Name",
            "AWS::EC2::Image::Id",
            "AWS::EC2::Instance::Id",
            "AWS::EC2::KeyPair::KeyName",
            "AWS::EC2::SecurityGroup::GroupName",
            "AWS::EC2::SecurityGroup::Id",
            "AWS::EC2::Subnet::Id",
            "AWS::EC2::Volume::Id",
            "AWS::EC2::VPC::Id",
            "AWS::Route53::HostedZone::Id",
        ]
        valid_types = [
            "String",
            "Number",
            "List<Number>",
            "CommaDelimitedList",
            "List<String>",
            "AWS::SSM::Parameter::Name",
            "AWS::SSM::Parameter::Value<String>",
            "AWS::SSM::Parameter::Value<List<String>>",
            "AWS::SSM::Parameter::Value<CommaDelimitedList>",
        ]
        for aws_parameter_type in aws_parameter_types:
            valid_types.append(aws_parameter_type)
            valid_types.append("List<%s>" % aws_parameter_type)
            valid_types.append("AWS::SSM::Parameter::Value<%s>" % aws_parameter_type)
            valid_types.append(
                "AWS::SSM::Parameter::Value<List<%s>>" % aws_parameter_type
            )

        for v_name, v_values in self.spec.get("ParameterTypes").items():
            self.assertIsInstance(v_values, list, "Parameter Type: %s" % (v_name))
