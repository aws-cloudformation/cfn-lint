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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from cfnlint.helpers import REGEX_IPV4, REGEX_IPV6, REGEX_ALPHANUMERIC


class RecordSet(CloudFormationLintRule):
    """Check Route53 Recordset Configuration"""
    id = 'E3020'
    shortdesc = 'Validate Route53 RecordSets'
    description = 'Check if all RecordSets are correctly configured'
    source_url = 'https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html'
    tags = ['resources', 'route53', 'record_set']

    REGEX_DOMAINNAME = re.compile(r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(.)$')
    REGEX_TXT = re.compile(r'^("[^"]{1,255}" *)*"[^"]{1,255}"$')
    REGEX_CNAME_VALIDATIONS = re.compile(r'^.*\.acm-validations\.aws\.?$')

    def check_a_record(self, path, recordset):
        """Check A record Configuration"""
        matches = []

        resource_records = recordset.get('ResourceRecords')
        for index, record in enumerate(resource_records):

            if not isinstance(record, dict):
                tree = path[:] + ['ResourceRecords', index]

                # Check if a valid IPv4 address is specified
                if not re.match(REGEX_IPV4, record):
                    message = 'A record ({}) is not a valid IPv4 address'
                    matches.append(RuleMatch(tree, message.format(record)))

        return matches

    def check_aaaa_record(self, path, recordset):
        """Check AAAA record Configuration"""
        matches = []

        resource_records = recordset.get('ResourceRecords')
        for index, record in enumerate(resource_records):

            if not isinstance(record, dict):
                tree = path[:] + ['ResourceRecords', index]

                # Check if a valid IPv4 address is specified
                if not re.match(REGEX_IPV6, record):
                    message = 'AAAA record ({}) is not a valid IPv6 address'
                    matches.append(RuleMatch(tree, message.format(record)))

        return matches

    def check_caa_record(self, path, recordset):
        """Check CAA record Configuration"""
        matches = []

        resource_records = recordset.get('ResourceRecords')

        for index, record in enumerate(resource_records):
            tree = path[:] + ['ResourceRecords', index]

            if not isinstance(record, dict):
                # Split the record up to the mandatory settings (flags tag "value")
                items = record.split(' ', 2)

                # Check if the 3 settings are given.
                if len(items) != 3:
                    message = 'CAA record must contain 3 settings (flags tag "value"), record contains {} settings.'
                    matches.append(RuleMatch(tree, message.format(len(items))))
                else:
                    # Check the flag value
                    if not items[0].isdigit():
                        message = 'CAA record flag setting ({}) should be of type Integer.'
                        matches.append(RuleMatch(tree, message.format(items[0])))
                    else:
                        if int(items[0]) not in [0, 128]:
                            message = 'Invalid CAA record flag setting ({}) given, must be 0 or 128.'
                            matches.append(RuleMatch(tree, message.format(items[0])))

                    # Check the tag value
                    if not re.match(REGEX_ALPHANUMERIC, items[1]):
                        message = 'Invalid CAA record tag setting {}. Value has to be alphanumeric.'
                        matches.append(RuleMatch(tree, message.format(items[0])))

                    # Check the value
                    if not items[2].startswith('"') or not items[2].endswith('"'):
                        message = 'CAA record value setting has to be enclosed in double quotation marks (").'
                        matches.append(RuleMatch(tree, message))

        return matches

    def check_cname_record(self, path, recordset):
        """Check CNAME record Configuration"""
        matches = []

        resource_records = recordset.get('ResourceRecords')
        if len(resource_records) > 1:
            message = 'A CNAME recordset can only contain 1 value'
            matches.append(RuleMatch(path + ['ResourceRecords'], message))
        else:
            for index, record in enumerate(resource_records):
                if not isinstance(record, dict):
                    tree = path[:] + ['ResourceRecords', index]
                    if (not re.match(self.REGEX_DOMAINNAME, record) and
                            not re.match(self.REGEX_CNAME_VALIDATIONS, record)):
                        # ACM Route 53 validation uses invalid CNAMEs starting with `_`,
                        # special-case them rather than complicate the regex.
                        message = 'CNAME record ({}) does not contain a valid domain name'
                        matches.append(RuleMatch(tree, message.format(record)))

        return matches

    def check_mx_record(self, path, recordset):
        """Check MX record Configuration"""
        matches = []

        resource_records = recordset.get('ResourceRecords')

        for index, record in enumerate(resource_records):
            tree = path[:] + ['ResourceRecords', index]

            if not isinstance(record, dict):
                # Split the record up to the mandatory settings (priority domainname)
                items = record.split(' ')

                # Check if the 3 settings are given.
                if len(items) != 2:
                    message = 'MX record must contain 2 settings (priority domainname), record contains {} settings.'
                    matches.append(RuleMatch(tree, message.format(len(items), record)))
                else:
                    # Check the priority value
                    if not items[0].isdigit():
                        message = 'MX record priority setting ({}) should be of type Integer.'
                        matches.append(RuleMatch(tree, message.format(items[0], record)))
                    else:
                        if not 0 <= int(items[0]) <= 65535:
                            message = 'Invalid MX record priority setting ({}) given, must be between 0 and 65535.'
                            matches.append(RuleMatch(tree, message.format(items[0], record)))

                    # Check the domainname value
                    if not re.match(self.REGEX_DOMAINNAME, items[1]):
                        matches.append(RuleMatch(tree, message.format(items[1])))

        return matches

    def check_txt_record(self, path, recordset):
        """Check TXT record Configuration"""
        matches = []

        # Check quotation of the records
        resource_records = recordset.get('ResourceRecords')

        for index, record in enumerate(resource_records):
            tree = path[:] + ['ResourceRecords', index]

            if not isinstance(record, dict) and not re.match(self.REGEX_TXT, record):
                message = 'TXT record is not structured as one or more items up to 255 characters ' \
                          'enclosed in double quotation marks at {0}'
                matches.append(RuleMatch(
                    tree,
                    (
                        message.format('/'.join(map(str, tree)))
                    ),
                ))

        return matches

    def check_recordset(self, path, recordset):
        """Check record configuration"""

        matches = []
        recordset_type = recordset.get('Type')

        # Skip Intrinsic functions
        if not isinstance(recordset_type, dict):
            if not recordset.get('AliasTarget'):
                # If no Alias is specified, ResourceRecords has to be specified
                if not recordset.get('ResourceRecords'):
                    message = 'Property ResourceRecords missing at {}'
                    matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))
                # Record type specific checks
                elif recordset_type == 'A':
                    matches.extend(self.check_a_record(path, recordset))
                elif recordset_type == 'AAAA':
                    matches.extend(self.check_aaaa_record(path, recordset))
                elif recordset_type == 'CAA':
                    matches.extend(self.check_caa_record(path, recordset))
                elif recordset_type == 'CNAME':
                    matches.extend(self.check_cname_record(path, recordset))
                elif recordset_type == 'MX':
                    matches.extend(self.check_mx_record(path, recordset))
                elif recordset_type == 'TXT':
                    matches.extend(self.check_txt_record(path, recordset))

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
                    matches.extend(self.check_recordset(path, props))

        recordsetgroups = cfn.get_resource_properties(['AWS::Route53::RecordSetGroup', 'RecordSets'])

        for recordsetgroup in recordsetgroups:
            path = recordsetgroup['Path']
            value = recordsetgroup['Value']
            if isinstance(value, list):
                for index, recordset in enumerate(value):
                    tree = path[:] + [index]
                    matches.extend(self.check_recordset(tree, recordset))

        return matches
