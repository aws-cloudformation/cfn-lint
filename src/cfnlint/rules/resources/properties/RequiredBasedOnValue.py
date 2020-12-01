"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.BasedOnValue import BasedOnValue


class RequiredBasedOnValue(BasedOnValue):
    """Check Required Properties are supplied when another property has a certain value"""
    id = 'E3017'
    shortdesc = 'Property is required based on another properties value'
    description = 'When certain properties have a certain value it results in other properties being required. ' \
        'This rule will validate those required properties are specified when those values are supplied'
    tags = ['resources']
    spec_type = 'RequiredProperties'
    message = 'should be specified'

    def _check_prop(self, prop, scenario):
        return prop not in scenario.get('Object')
