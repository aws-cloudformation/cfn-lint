"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Ebs(CloudFormationLintRule):
    """Check if Ec2 Ebs Resource Properties"""
    id = 'E2504'
    shortdesc = 'Check Ec2 Ebs Properties'
    description = 'See if Ec2 Eb2 Properties are valid'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-blockdev-template.html'
    tags = ['properties', 'ec2', 'ebs']

    def _checkEbs(self, ebs, path):
        matches = []

        if isinstance(ebs, dict):
            volume_types_obj = ebs.get_safe('VolumeType', None, path)
            iops_obj = ebs.get_safe('Iops', None, path)
            if volume_types_obj is not None:
                for vt_value, vt_path in volume_types_obj:
                    if isinstance(vt_value, six.string_types):
                        if vt_value not in ['standard', 'io1', 'gp2', 'sc1', 'st1']:
                            message = 'VolumeType should be of standard | io1 | gp2 | sc1 | st1] for {0}'
                            matches.append(
                                RuleMatch(vt_path, message.format('/'.join(map(str, vt_path)))))
                        elif vt_value == 'io1':
                            if iops_obj is None:
                                message = 'VolumeType io1 requires Iops to be specified for {0}'
                                matches.append(
                                    RuleMatch(vt_path, message.format('/'.join(map(str, vt_path)))))
                            else:
                                for iop_value, iop_path in iops_obj:
                                    try:
                                        if isinstance(iop_value, (six.string_types, int)):
                                            iops_value = int(iop_value)
                                            if iops_value < 100 or iops_value > 2000:
                                                message = 'Property Iops should be Int between 100 to 20000 {0}'
                                                matches.append(
                                                    RuleMatch(
                                                        iop_path,
                                                        message.format('/'.join(map(str, iop_path)))))
                                    except ValueError:
                                        message = 'Property Iops should be Int between 100 to 20000 {0}'
                                        matches.append(
                                            RuleMatch(iop_path, message.format('/'.join(map(str, iop_path)))))
                        elif vt_value:
                            if iops_obj:
                                message = 'Iops shouldn\'t be defined for type {0} for {1}'
                                matches.append(
                                    RuleMatch(
                                        path[:] + ['Iops'],
                                        message.format(vt_value, '/'.join(map(str, path[:] + ['Iops'])))))

        return matches

    def match(self, cfn):
        """Check Ec2 Ebs Resource Parameters"""

        matches = []

        results = cfn.get_resource_properties(['AWS::EC2::Instance', 'BlockDeviceMappings'])
        results.extend(cfn.get_resource_properties(['AWS::AutoScaling::LaunchConfiguration', 'BlockDeviceMappings']))
        for result in results:
            path = result['Path']
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
                    matches.extend(self._checkEbs(ebs, path[:] + [index, 'Ebs']))
        return matches
