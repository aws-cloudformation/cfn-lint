"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_IPV4, REGEX_IPV6, REGEX_ALPHANUMERIC


class RecordSet(CloudFormationLintRule):
    """Check Route53 Recordset Configuration"""
    id = 'E3020'
    shortdesc = 'Validate Route53 RecordSets'
    description = 'Check if all RecordSets are correctly configured'
    source_url = 'https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html'
    tags = ['resources', 'route53', 'record_set']

    # Regex generated from https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/DomainNameFormat.html
    REGEX_DOMAINNAME = re.compile(
        r'^[a-zA-Z0-9\!\"\#\$\%\&\'\(\)\*\+\,-\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~\.]+$')
    REGEX_TXT = re.compile(r'^("[^"]{1,255}" *)*"[^"]{1,255}"$')
    REGEX_CNAME_VALIDATIONS = re.compile(r'^.*\.acm-validations\.aws\.?$')

    def count_c_names(self, records, path, cfn):
        """ Count C Names """
        matches = []

        scenarios = cfn.get_object_without_nested_conditions(records, path)
        for scenario in scenarios:
            if len(scenario.get('Object')) > 1:
                scenario = scenario.get('Scenario')
                message = 'A CNAME recordset can only contain 1 value'
                if scenario is None:
                    message = 'A CNAME recordset can only contain 1 value'
                    matches.append(
                        RuleMatch(path, message.format('/'.join(map(str, message)))))
                else:
                    message = 'A CNAME recordset can only contain 1 value {0} at {1}'
                    scenario_text = ' and '.join(
                        ['when condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                    matches.append(
                        RuleMatch(path, message.format(scenario_text, '/'.join(map(str, path)))))

        return matches

    def check_record(self, value, path, record_type, regex, regex_name):
        matches = []
        if isinstance(value, str):
            if not re.match(regex, value):
                message = record_type + ' record ({}) is not a valid ' + regex_name
                matches.append(RuleMatch(path, message.format(value)))
        return matches

    def check_a_record(self, value, path):
        return self.check_record(value, path, 'A', REGEX_IPV4, 'IPv4 address')

    def check_aaaa_record(self, value, path):
        return self.check_record(value, path, 'AAAA', REGEX_IPV6, 'IPv6 address')

    def check_caa_record(self, value, path):
        """Check CAA record Configuration"""
        matches = []

        if isinstance(value, str):
            # Split the record up to the mandatory settings (flags tag "value")
            items = value.split(' ', 2)
            # Check if the 3 settings are given.
            if len(items) != 3:
                message = 'CAA record must contain 3 settings (flags tag "value"), record contains {} settings.'
                matches.append(RuleMatch(path, message.format(len(items))))
            else:
                # Check the flag value
                if not items[0].isdigit():
                    message = 'CAA record flag setting ({}) should be of type Integer.'
                    extra_args = {'actual_type': type(
                        items[0]).__name__, 'expected_type': int.__name__}
                    matches.append(RuleMatch(path, message.format(items[0]), **extra_args))
                else:
                    if int(items[0]) not in [0, 128]:
                        message = 'Invalid CAA record flag setting ({}) given, must be 0 or 128.'
                        matches.append(RuleMatch(path, message.format(items[0])))

                # Check the tag value
                if not re.match(REGEX_ALPHANUMERIC, items[1]):
                    message = 'Invalid CAA record tag setting {}. Value has to be alphanumeric.'
                    matches.append(RuleMatch(path, message.format(items[1])))

                # Check the value
                if not items[2].startswith('"') or not items[2].endswith('"'):
                    message = 'CAA record value setting has to be enclosed in double quotation marks (").'
                    matches.append(RuleMatch(path, message))

        return matches

    def check_cname_record(self, value, path):
        """Check CNAME record Configuration"""
        matches = []

        if not isinstance(value, dict):
            if (not re.match(self.REGEX_DOMAINNAME, value) and
                    not re.match(self.REGEX_CNAME_VALIDATIONS, value)):
                # ACM Route 53 validation uses invalid CNAMEs starting with `_`,
                # special-case them rather than complicate the regex.
                message = 'CNAME record ({}) does not contain a valid domain name'
                matches.append(RuleMatch(path, message.format(value)))

        return matches

    def check_mx_record(self, value, path):
        """Check MX record Configuration"""
        matches = []

        if isinstance(value, str):
            # Split the record up to the mandatory settings (priority domainname)
            items = value.split(' ')

            # Check if the 3 settings are given.
            if len(items) != 2:
                message = 'MX record must contain 2 settings (priority domainname), record contains {} settings.'
                matches.append(RuleMatch(path, message.format(len(items), value)))
            else:
                # Check the priority value
                if not items[0].isdigit():
                    message = 'MX record priority setting ({}) should be of type Integer.'
                    extra_args = {'actual_type': type(
                        items[0]).__name__, 'expected_type': int.__name__}
                    matches.append(RuleMatch(path, message.format(items[0], value), **extra_args))
                else:
                    if not 0 <= int(items[0]) <= 65535:
                        message = 'Invalid MX record priority setting ({}) given, must be between 0 and 65535.'
                        matches.append(RuleMatch(path, message.format(items[0], value)))

                # Check the domainname value
                if not re.match(self.REGEX_DOMAINNAME, items[1]):
                    matches.append(RuleMatch(path, message.format(items[1])))

        return matches

    def check_ns_record(self, value, path):
        return self.check_record(value, path, 'NS', self.REGEX_DOMAINNAME, 'domain name')

    def check_ptr_record(self, value, path):
        return self.check_record(value, path, 'PTR', self.REGEX_DOMAINNAME, 'domain name')

    def check_txt_record(self, value, path):
        """Check TXT record Configuration"""
        matches = []

        if not isinstance(value, dict) and not re.match(self.REGEX_TXT, value):
            message = 'TXT record is not structured as one or more items up to 255 characters ' \
                      'enclosed in double quotation marks at {0}'
            matches.append(RuleMatch(
                path,
                (
                    message.format('/'.join(map(str, path)))
                ),
            ))

        return matches

    def check_recordset(self, path, recordset, cfn):
        """Check record configuration"""

        matches = []
        recordset_type = recordset.get('Type')

        # Skip Intrinsic functions
        if not isinstance(recordset_type, dict):
            if not recordset.get('AliasTarget'):
                # If no Alias is specified, ResourceRecords has to be specified
                if not recordset.get('ResourceRecords'):
                    return matches
                # Record type specific checks
                if recordset_type == 'A':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_a_record,
                        )
                    )
                elif recordset_type == 'AAAA':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_aaaa_record,
                        )
                    )
                elif recordset_type == 'CAA':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_caa_record,
                        )
                    )
                elif recordset_type == 'CNAME':
                    matches.extend(
                        self.count_c_names(
                            recordset.get('ResourceRecords'), path[:] + ['ResourceRecords'], cfn
                        )
                    )
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_cname_record,
                        )
                    )
                elif recordset_type == 'MX':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_mx_record,
                        )
                    )
                elif recordset_type == 'NS':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_ns_record,
                        )
                    )
                elif recordset_type == 'PTR':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_ptr_record,
                        )
                    )
                elif recordset_type == 'TXT':
                    matches.extend(
                        cfn.check_value(
                            recordset, 'ResourceRecords', path[:],
                            check_value=self.check_txt_record,
                        )
                    )
            else:
                if recordset.get('TTL'):
                    matches.append(RuleMatch(path + ['TTL'], 'TTL is not allowed for Alias records'))

        return matches

    def match(self, cfn):
        """Check RecordSets and RecordSetGroups Properties"""

        matches = []

        recordsets = cfn.get_resources(['AWS::Route53::RecordSet'])

        for name, recordset in recordsets.items():
            path = ['Resources', name, 'Properties']

            if isinstance(recordset, dict):
                props = recordset.get('Properties')
                if props:
                    matches.extend(self.check_recordset(path, props, cfn))

        recordsetgroups = cfn.get_resource_properties(
            ['AWS::Route53::RecordSetGroup', 'RecordSets'])

        for recordsetgroup in recordsetgroups:
            path = recordsetgroup['Path']
            value = recordsetgroup['Value']
            if isinstance(value, list):
                for index, recordset in enumerate(value):
                    tree = path[:] + [index]
                    matches.extend(self.check_recordset(tree, recordset, cfn))

        return matches
