"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Ebs(CloudFormationLintRule):
    """Check if Ec2 Ebs Resource Properties"""
    id = 'E2504'
    shortdesc = 'Check Ec2 Ebs Properties'
    description = 'See if Ec2 Eb2 Properties are valid'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html'
    tags = ['properties', 'ec2', 'ebs']

    def _checkEbs(self, cfn, ebs, path):
        matches = []

        if isinstance(ebs, dict):
            volume_types_obj = cfn.get_values(ebs, 'VolumeType')
            iops_obj = cfn.get_values(ebs, 'Iops')
            if volume_types_obj is not None:
                for volume_type_obj in volume_types_obj:
                    volume_type = volume_type_obj.get('Value')
                    if isinstance(volume_type, six.string_types):
                        if volume_type == 'io1':
                            if iops_obj is None:
                                pathmessage = path[:] + ['VolumeType']
                                message = 'VolumeType io1 requires Iops to be specified for {0}'
                                matches.append(
                                    RuleMatch(pathmessage, message.format('/'.join(map(str, pathmessage)))))
                        elif volume_type:
                            if iops_obj is not None:
                                pathmessage = path[:] + ['Iops']
                                message = 'Iops shouldn\'t be defined for type {0} for {1}'
                                matches.append(
                                    RuleMatch(
                                        pathmessage,
                                        message.format(volume_type, '/'.join(map(str, pathmessage)))))

        return matches

    def match(self, cfn):
        """Check Ec2 Ebs Resource Parameters"""

        matches = []

        results = cfn.get_resource_properties(['AWS::EC2::Instance', 'BlockDeviceMappings'])
        results.extend(cfn.get_resource_properties(['AWS::AutoScaling::LaunchConfiguration', 'BlockDeviceMappings']))
        for result in results:
            path = result['Path']
            if isinstance(result['Value'], list):
                for index, properties in enumerate(result['Value']):
                    virtual_name = properties.get('VirtualName')
                    ebs = properties.get('Ebs')
                    if virtual_name:
                        # switch to regex
                        if not re.match(r'^ephemeral[0-9]$', virtual_name):
                            pathmessage = path[:] + [index, 'VirtualName']
                            message = 'Property VirtualName should be of type ephemeral(n) for {0}'
                            matches.append(
                                RuleMatch(pathmessage, message.format('/'.join(map(str, pathmessage)))))
                    elif ebs:
                        matches.extend(self._checkEbs(cfn, ebs, path[:] + [index, 'Ebs']))
        return matches
