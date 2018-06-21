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

class RecordSet(CloudFormationLintRule):
    """Check Route53 Recordset Configuration"""
    id = 'E3020'
    shortdesc = 'Validate Route53 RecordSets'
    description = 'Check if all RecordSets are correctly configured'
    tags = ['base', 'resources', 'route53', 'record_set']

    # https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/ResourceRecordTypes.html
    VALID_RECORD_TYPES = [
        'A',
        'AAAA',
        'CAA',
        'CNAME',
        'MX',
        'NAPTR',
        'NS',
        'PTR',
        'SOA'
        'SPF',
        'SRV',
        'TXT'
    ]

    ipv4_regex = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$'

    def check_a_record(self, path, recordset):
        """Check A record Configuration"""
        matches = list()

        if not recordset.get('AliasTarget'):
            resource_records = recordset.get('ResourceRecords')
            for index, record in enumerate(resource_records):

                if isinstance(record, six.string_types):
                    tree = path[:] + ['ResourceRecords', index]
                    full_path = ('/'.join(str(x) for x in tree))

                    # Check if a valid IPv4 address is specified
                    regex = re.compile(self.ipv4_regex)
                    if not regex.match(record):
                        message = 'A record is not a valid IPv4 address at {0}'
                        matches.append(RuleMatch(tree, message.format(full_path)))

        return matches

    def check_txt_record(self, path, recordset):
        """Check TXT record Configuration"""
        matches = list()

        # Check quotation of the records
        resource_records = recordset.get('ResourceRecords')

        for index, record in enumerate(resource_records):
            tree = path[:] + ['ResourceRecords', index]
            full_path = ('/'.join(str(x) for x in tree))

            if not record.startswith('"') or not record.endswith('"'):
                message = 'TXT record has to be enclosed in double quotation marks (") at {0}'
                matches.append(RuleMatch(tree, message.format(full_path)))
            elif len(record) > 255:
                message = 'The length of the TXT record ({0}) exceeds the limit (255) as {1}'
                matches.append(RuleMatch(tree, message.format(len(record), full_path)))

        return matches

    def check_recordset(self, path, recordset):
        """Check record configuration"""

        matches = list()
        recordset_type = recordset.get('Type')

        if recordset_type not in self.VALID_RECORD_TYPES:
            message = 'Invalid record type "{0}" specified at {1}'
            full_path = ('/'.join(str(x) for x in path))
            matches.append(RuleMatch(path, message.format(recordset_type, full_path)))
        elif recordset_type == 'A':
            matches.extend(self.check_a_record(path, recordset))
        elif recordset_type == 'TXT':
            matches.extend(self.check_txt_record(path, recordset))

        return matches


    def match(self, cfn):
        """Check RecordSets and RecordSetGroups Properties"""

        matches = list()

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
