"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import sys
from test.testlib.testcase import BaseTestCase
from unittest.mock import ANY, MagicMock, Mock, call, patch

import cfnlint.maintenance

LOGGER = logging.getLogger("cfnlint.maintenance")
LOGGER.addHandler(logging.NullHandler())


def patch_spec_sideffect(content, region, patch_types="ExtendedSpecs"):
    if region == "all" and patch_types == "ExtendedSpecs":
        return {
            "PropertyTypes": {
                "AWS::Lambda::CodeSigningConfig.AllowedPublishers": {
                    "Properties": {
                        "SigningProfileVersionArns": {},
                    }
                },
                "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies": {
                    "Properties": {
                        "UntrustedArtifactOnDeployment": {},
                    }
                },
            },
            "ResourceTypes": {
                "AWS::Lambda::CodeSigningConfig": {
                    "Attributes": {
                        "CodeSigningConfigArn": {
                            "PrimitiveType": "String",
                        },
                        "CodeSigningConfigId": {
                            "PrimitiveType": "String",
                        },
                    },
                    "Properties": {
                        "AllowedPublishers": {},
                        "CodeSigningPolicies": {},
                        "Description": {},
                    },
                }
            },
            "ValueTypes": {},
        }
    if region in ["us-east-1", "us-west-2"] and patch_types == "ExtendedSpecs":
        return {
            "PropertyTypes": {
                "AWS::Lambda::CodeSigningConfig.AllowedPublishers": {
                    "Properties": {
                        "SigningProfileVersionArns": {},
                    }
                },
                "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies": {
                    "Properties": {
                        "UntrustedArtifactOnDeployment": {},
                    }
                },
            },
            "ResourceTypes": {
                "AWS::Lambda::CodeSigningConfig": {
                    "Attributes": {
                        "CodeSigningConfigArn": {
                            "PrimitiveType": "String",
                        },
                        "CodeSigningConfigId": {
                            "PrimitiveType": "String",
                        },
                    },
                    "Properties": {
                        "AllowedPublishers": {},
                        "CodeSigningPolicies": {},
                        "Description": {},
                    },
                }
            },
            "ValueTypes": {
                "AWS::EC2::Instance.Types": ["m2.medium"],
            },
        }

    return content


class TestUpdateResourceSpecs(BaseTestCase):
    """Used for Testing Resource Specs"""

    @patch("cfnlint.maintenance.url_has_newer_version")
    @patch("cfnlint.maintenance.get_url_content")
    @patch("cfnlint.maintenance.json.dump")
    @patch("cfnlint.maintenance.patch_spec")
    @patch("cfnlint.maintenance.SPEC_REGIONS", {"us-east-1": "http://foo.badurl"})
    @patch("cfnlint.maintenance.urlopen")
    def test_update_resource_spec(
        self,
        mock_urlopen,
        mock_patch_spec,
        mock_json_dump,
        mock_content,
        mock_url_newer_version,
    ):
        """Success update resource spec"""

        mock_url_newer_version.return_value = True
        mock_content.return_value = '{"PropertyTypes": {}, "ResourceTypes": {}}'
        mock_patch_spec.side_effect = patch_spec_sideffect

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.__enter__.return_value = cm

        with open("test/fixtures/registry/schema.zip", "rb") as f:
            byte = f.read()
            cm.read.return_value = byte

        mock_urlopen.return_value = cm
        schema_cache = cfnlint.maintenance.get_schema_value_types()

        builtin_module_name = "builtins"

        with patch("{}.open".format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_resource_spec(
                "us-east-1", "http://foo.badurl", schema_cache
            )
            mock_json_dump.assert_called_with(
                {
                    "PropertyTypes": {
                        "AWS::Lambda::CodeSigningConfig.AllowedPublishers": {
                            "Properties": {
                                "SigningProfileVersionArns": {
                                    "Value": {
                                        "ValueType": "AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns",
                                    }
                                },
                            }
                        },
                        "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies": {
                            "Properties": {
                                "UntrustedArtifactOnDeployment": {
                                    "Value": {
                                        "ValueType": "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment",
                                    }
                                },
                            }
                        },
                    },
                    "ResourceTypes": {
                        "AWS::Lambda::CodeSigningConfig": {
                            "Attributes": {
                                "CodeSigningConfigArn": {
                                    "PrimitiveType": "String",
                                },
                                "CodeSigningConfigId": {
                                    "PrimitiveType": "String",
                                },
                            },
                            "Properties": {
                                "AllowedPublishers": {},
                                "CodeSigningPolicies": {},
                                "Description": {
                                    "Value": {
                                        "ValueType": "AWS::Lambda::CodeSigningConfig.Description"
                                    },
                                },
                            },
                        }
                    },
                    "ValueTypes": {
                        "AWS::EC2::Instance.Types": ["m2.medium"],
                        "AWS::Lambda::CodeSigningConfig.Description": {
                            "StringMin": 0,
                            "StringMax": 256,
                        },
                        "AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns": {
                            "AllowedPatternRegex": "arn:(aws[a-zA-Z0-9-]*):([a-zA-Z0-9\\-])+:([a-z]{2}(-gov)?-[a-z]+-\\d{1})?:(\\d{12})?:(.*)",
                            "StringMin": 12,
                            "StringMax": 1024,
                        },
                        "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment": {
                            "AllowedValues": ["Warn", "Enforce"]
                        },
                    },
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )

    @patch("cfnlint.maintenance.url_has_newer_version")
    @patch("cfnlint.maintenance.get_url_content")
    @patch("cfnlint.maintenance.json.dump")
    @patch("cfnlint.maintenance.patch_spec")
    @patch("cfnlint.maintenance.SPEC_REGIONS", {"us-east-1": "http://foo.badurl"})
    @patch("cfnlint.maintenance.urlopen")
    @patch("cfnlint.maintenance.cfnlint.helpers.load_resource")
    def test_update_resource_spec_cache(
        self,
        mock_load_resource,
        mock_urlopen,
        mock_patch_spec,
        mock_json_dump,
        mock_content,
        mock_url_newer_version,
    ):
        """Success update resource spec with cache"""

        mock_url_newer_version.return_value = True
        mock_content.return_value = '{"PropertyTypes": {}, "ResourceTypes": {}}'
        mock_patch_spec.side_effect = patch_spec_sideffect

        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.__enter__.return_value = cm

        with open("test/fixtures/registry/schema.zip", "rb") as f:
            byte = f.read()
            cm.read.return_value = byte

        mock_urlopen.return_value = cm
        schema_cache = cfnlint.maintenance.get_schema_value_types()

        builtin_module_name = "builtins"

        mock_load_resource.return_value = {
            "PropertyTypes": {
                "AWS::Lambda::CodeSigningConfig.AllowedPublishers": {
                    "Properties": {
                        "SigningProfileVersionArns": {
                            "Value": {
                                "ValueType": "AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns",
                            }
                        },
                    }
                },
                "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies": {
                    "Properties": {
                        "UntrustedArtifactOnDeployment": {
                            "Value": {
                                "ValueType": "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment",
                            }
                        },
                    }
                },
            },
            "ResourceTypes": {
                "AWS::Lambda::CodeSigningConfig": {
                    "Attributes": {
                        "CodeSigningConfigArn": {
                            "PrimitiveType": "String",
                        },
                        "CodeSigningConfigId": {
                            "PrimitiveType": "String",
                        },
                    },
                    "Properties": {
                        "AllowedPublishers": {},
                        "CodeSigningPolicies": {},
                        "Description": {
                            "Value": {
                                "ValueType": "AWS::Lambda::CodeSigningConfig.Description"
                            },
                        },
                    },
                }
            },
            "ValueTypes": {
                "AWS::EC2::Instance.Types": [
                    "m2.medium",
                    "m2.large",
                ],
                "AWS::Lambda::CodeSigningConfig.Description": {
                    "StringMin": 0,
                    "StringMax": 256,
                },
                "AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns": {
                    "AllowedPatternRegex": "arn:(aws[a-zA-Z0-9-]*):([a-zA-Z0-9\\-])+:([a-z]{2}(-gov)?-[a-z]+-\\d{1})?:(\\d{12})?:(.*)",
                    "StringMin": 12,
                    "StringMax": 1024,
                },
                "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment": {
                    "AllowedValues": ["Warn", "Enforce"]
                },
            },
        }

        with patch("{}.open".format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_resource_spec(
                "us-west-2", "http://foo.badurl", schema_cache
            )
            mock_json_dump.assert_called_with(
                {
                    "PropertyTypes": {
                        "AWS::Lambda::CodeSigningConfig.AllowedPublishers": "CACHED",
                        "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies": "CACHED",
                    },
                    "ResourceTypes": {
                        "AWS::Lambda::CodeSigningConfig": "CACHED",
                    },
                    "ValueTypes": {
                        # does not match above
                        "AWS::EC2::Instance.Types": [
                            "m2.medium",
                        ],
                        "AWS::Lambda::CodeSigningConfig.Description": "CACHED",
                        "AWS::Lambda::CodeSigningConfig.AllowedPublishers.SigningProfileVersionArns": "CACHED",
                        "AWS::Lambda::CodeSigningConfig.CodeSigningPolicies.UntrustedArtifactOnDeployment": "CACHED",
                    },
                },
                mock_builtin_open.return_value.__enter__.return_value,
                indent=1,
                separators=(",", ": "),
                sort_keys=True,
            )

    @patch("cfnlint.maintenance.url_has_newer_version")
    @patch("cfnlint.maintenance.get_url_content")
    @patch("cfnlint.maintenance.json.dump")
    @patch("cfnlint.maintenance.patch_spec")
    @patch("cfnlint.maintenance.SPEC_REGIONS", {"us-east-1": "http://foo.badurl"})
    def test_do_not_update_resource_spec(
        self, mock_patch_spec, mock_json_dump, mock_content, mock_url_newer_version
    ):
        """Success update resource spec"""

        mock_url_newer_version.return_value = False

        result = cfnlint.maintenance.update_resource_spec(
            "us-east-1", "http://foo.badurl", ANY
        )
        self.assertIsNone(result)
        mock_content.assert_not_called()
        mock_patch_spec.assert_not_called()
        mock_json_dump.assert_not_called()

    @patch("cfnlint.maintenance.url_has_newer_version")
    @patch("cfnlint.maintenance.get_url_content")
    @patch("cfnlint.maintenance.json.dump")
    @patch("cfnlint.maintenance.patch_spec")
    @patch("cfnlint.maintenance.SPEC_REGIONS", {"us-east-1": "http://foo.badurl"})
    @patch("cfnlint.maintenance.urlopen")
    def test_update_resource_spec_force(
        self,
        mock_urlopen,
        mock_patch_spec,
        mock_json_dump,
        mock_content,
        mock_url_newer_version,
    ):
        """Success update resource spec"""

        mock_url_newer_version.return_value = False
        mock_content.return_value = '{"PropertyTypes": {}, "ResourceTypes": {}}'
        mock_patch_spec.side_effect = patch_spec_sideffect

        mock_urlresponse = Mock()
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.__enter__.return_value = cm

        with open("test/fixtures/registry/schema.zip", "rb") as f:
            byte = f.read()
            cm.read.return_value = byte

        mock_urlopen.return_value = cm
        schema_cache = cfnlint.maintenance.get_schema_value_types()

        builtin_module_name = "builtins"

        with patch("{}.open".format(builtin_module_name)) as mock_builtin_open:
            cfnlint.maintenance.update_resource_spec(
                "us-east-1", "http://foo.badurl", schema_cache, True
            )
            mock_content.assert_called_once()
            mock_patch_spec.assert_called()
            mock_json_dump.assert_called_once()

    @patch("cfnlint.maintenance.multiprocessing.Pool")
    @patch("cfnlint.maintenance.update_resource_spec")
    @patch("cfnlint.maintenance.SPEC_REGIONS", {"us-east-1": "http://foo.badurl"})
    def test_update_resource_specs_python_3(self, mock_update_resource_spec, mock_pool):
        fake_pool = MagicMock()
        mock_pool.return_value.__enter__.return_value = fake_pool

        cfnlint.maintenance.update_resource_specs()

        fake_pool.starmap.assert_called_once()
