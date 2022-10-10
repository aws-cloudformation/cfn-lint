"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers

LOGGER = logging.getLogger('cfnlint')


class GetAtt(CloudFormationLintRule):
    """Check if GetAtt values are correct"""

    id = 'E1010'
    shortdesc = 'GetAtt validation of parameters'
    description = 'Validates that GetAtt parameters are to valid resources and properties of those resources'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html'
    tags = ['functions', 'getatt']

    def __init__(self):
        """Init"""
        super().__init__()
        self.propertytypes = []
        self.resourcetypes = []

    def initialize(self, cfn):
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[cfn.regions[0]]
        self.resourcetypes = resourcespecs['ResourceTypes']
        self.propertytypes = resourcespecs['PropertyTypes']

    def match(self, cfn):
        matches = []

        getatts = cfn.search_deep_keys('Fn::GetAtt')
        valid_getatts = cfn.get_valid_getatts()

        valid_attribute_functions = ['Ref']

        for getatt in getatts:
            if len(getatt[-1]) < 2:
                message = 'Invalid GetAtt for {0}'
                matches.append(
                    RuleMatch(getatt, message.format('/'.join(map(str, getatt[:-1]))))
                )
                continue
            if isinstance(getatt[-1], str):
                resname, restype = getatt[-1].split('.', 1)
            else:
                resname = None
                restype = None
                if isinstance(getatt[-1][1], str):
                    resname = getatt[-1][0]
                    restype = '.'.join(getatt[-1][1:])
                elif isinstance(getatt[-1][1], dict):
                    # You can ref the secondary part of a getatt

                    resname = getatt[-1][0]
                    restype = getatt[-1][1]
                    if len(restype) == 1:
                        for k in restype.keys():
                            if k not in valid_attribute_functions:
                                message = 'GetAtt only supports functions "{0}" for attributes at {1}'
                                matches.append(
                                    RuleMatch(
                                        getatt,
                                        message.format(
                                            ', '.join(
                                                map(str, valid_attribute_functions)
                                            ),
                                            '/'.join(map(str, getatt[:-1])),
                                        ),
                                    )
                                )
                    else:
                        message = 'Invalid GetAtt structure {0} at {1}'
                        matches.append(
                            RuleMatch(
                                getatt,
                                message.format(
                                    getatt[-1], '/'.join(map(str, getatt[:-1]))
                                ),
                            )
                        )

                    # setting restype to None as we can't validate that anymore
                    restype = None
                else:
                    message = 'Invalid GetAtt structure {0} at {1}'
                    matches.append(
                        RuleMatch(
                            getatt,
                            message.format(getatt[-1], '/'.join(map(str, getatt[:-1]))),
                        )
                    )

            # only check resname if its set.  if it isn't it is because of bad structure
            # and an error is already provided
            if resname:
                if resname in valid_getatts:
                    if restype is not None:
                        # Check for maps
                        restypeparts = restype.split('.')
                        if (
                            restypeparts[0] in valid_getatts[resname]
                            and len(restypeparts) >= 2
                        ):
                            if (
                                valid_getatts[resname][restypeparts[0]].get('Type')
                                != 'Map'
                            ):
                                message = 'Invalid GetAtt {0}.{1} for resource {2}'
                                matches.append(
                                    RuleMatch(
                                        getatt[:-1],
                                        message.format(resname, restype, getatt[1]),
                                    )
                                )
                            else:
                                continue
                        if (
                            restype not in valid_getatts[resname]
                            and '*' not in valid_getatts[resname]
                        ):
                            message = 'Invalid GetAtt {0}.{1} for resource {2}'
                            matches.append(
                                RuleMatch(
                                    getatt[:-1],
                                    message.format(resname, restype, getatt[1]),
                                )
                            )
                else:
                    modules = cfn.get_modules()
                    if any(resname.startswith(s) for s in modules.keys()):
                        LOGGER.debug(
                            'Will consider valid getatt %s because it references a resource within a module',
                            resname,
                        )
                    else:
                        message = 'Invalid GetAtt {0}.{1} for resource {2}'
                        matches.append(
                            RuleMatch(
                                getatt, message.format(resname, restype, getatt[1])
                            )
                        )

        return matches
