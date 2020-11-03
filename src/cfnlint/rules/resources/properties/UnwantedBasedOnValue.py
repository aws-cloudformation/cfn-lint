"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.BasedOnValue import BasedOnValue


class UnwantedBasedOnValue(BasedOnValue):
    """Check Unwanted Properties are supplied when another property has a certain value"""
    id = 'E3018'
    shortdesc = 'Property is unwanted based on another properties value'
    description = 'When certain properties have a certain value it results in other properties not being needed. ' \
        'This rule will validate those unwanted properties are not specified when those values are supplied'
    tags = ['resources']
    spec_type = 'UnwantedProperties'
    message = 'should not be specified'

    def _check_prop(self, prop, scenario):
        return prop in scenario.get('Object')
