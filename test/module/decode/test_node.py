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
import cfnlint.decode.node  # pylint: disable=E0401
from testlib.testcase import BaseTestCase


class TestNode(BaseTestCase):
    """Test Node Objects """

    def test_success_init(self):
        """Test Dict Object"""
        template = cfnlint.decode.node.dict_node({
            "test": "string"
        }, (0, 1), (2, 3))

        self.assertEqual(template, {"test": "string"})
        self.assertEqual(template.start_mark[0], 0)
        self.assertEqual(template.start_mark[1], 1)
        self.assertEqual(template.end_mark[0], 2)
        self.assertEqual(template.end_mark[1], 3)

    def test_success_dict_get_safe(self):
        """Test List Object"""
        filename = 'fixtures/templates/good/decode/conditions.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)

        bucket_properties = template.get('Resources').get('myS3Bucket').get('Properties')
        results = [
            (True, ['Fn::If', 1, 'BucketName', 'Fn::If', 1]),
            (True, ['Fn::If', 1, 'BucketName', 'Fn::If', 2, 'Fn::If', 1]),
            (False, ['Fn::If', 1, 'BucketName', 'Fn::If', 2, 'Fn::If', 2]),
            (True, ['Fn::If', 2, 'Fn::If', 1, 'BucketName'])
        ]

        self.assertEqual(bucket_properties.get_safe('BucketName'), results)

    def test_success_dict_items_safe(self):
        """Test List Object"""
        filename = 'fixtures/templates/good/decode/conditions.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)

        bucket_properties = template.get('Resources').get('myS3Bucket').get('Properties')
        correct_results = [
            ({'BucketName': {'Fn::If': ['isProd', True, {'Fn::If': ['isDev', True, False]}]}}, ['Fn::If', 1]),
            ({'MetricsConfigurations': False, 'BucketName': True}, ['Fn::If', 2, 'Fn::If', 1])
        ]

        results = []
        for items, p in bucket_properties.items_safe():
            results.append((items, p))

        self.assertEqual(results, correct_results)

    def test_success_dict_get_keys_safe(self):
        """ Test success of Get Keys Safe on Dict """
        filename = 'fixtures/templates/good/decode/conditions.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)

        #
        # Test singular condition
        #
        dbcluster_properties = template.get('Resources').get('DBCluster').get('Properties')
        correct_results = [
            ['DBSnapshotIdentifier', 'DBInstanceClass', 'Engine'].sort(),
            ['DBInstanceClass', 'Engine', 'MasterUserPassword', 'MasterUsername'].sort()]

        results = []
        for result in dbcluster_properties.keys_safe():
            results.append(result.sort())

        self.assertEqual(results, correct_results)

    def test_success_dict_get_keys_safe_multiple_conditions(self):
        """ Test success of Get Keys Safe on Dict """
        filename = 'fixtures/templates/good/decode/conditions.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)

        dbcluster_properties = template.get('Resources').get('DBCluster2').get('Properties')
        correct_results = [
            ['MasterUsername', 'MasterUserPassword', 'DBSnapshotIdentifier', 'Engine', 'DBInstanceClass'].sort(),
            ['MasterUsername', 'MasterUserPassword', 'Engine', 'DBInstanceClass'].sort(),
            ['DBSnapshotIdentifier', 'Engine', 'DBInstanceClass'].sort(),
            ['Engine', 'DBInstanceClass'].sort()]

        results = []
        for result in dbcluster_properties.keys_safe():
            results.append(result.sort())

        self.assertEqual(results, correct_results)

    def test_success_dict_check_value(self):
        """Test List Object"""
        filename = 'fixtures/templates/good/decode/conditions.yaml'
        template = cfnlint.decode.cfn_yaml.load(filename)

        def check_value(value, path):
            """ Return the value """
            if path == ['Fn::If', 1, 'BucketName', 'Fn::If', 1] and value is True:
                return [1]
            elif path == ['Fn::If', 1, 'BucketName', 'Fn::If', 2, 'Fn::If', 1] and value is True:
                return [2]
            elif path == ['Fn::If', 1, 'BucketName', 'Fn::If', 2, 'Fn::If', 2] and value is False:
                return [3]
            elif path == ['Fn::If', 2, 'Fn::If', 1, 'BucketName'] and value is True:
                return [4]

            return [False]

        results = []
        bucket_properties = template.get('Resources').get('myS3Bucket').get('Properties')
        results = bucket_properties.check_value(key='BucketName', path=[], check_value=check_value)

        self.assertEqual(results[0], 1)
        self.assertEqual(results[1], 2)
        self.assertEqual(results[2], 3)
        self.assertEqual(results[3], 4)

    def test_success_fnif_list(self):
        """Test List Object"""
        template = cfnlint.decode.node.dict_node({
            "Fn::If": [
                "string",
                ["1", "2", "3"],
                ["a", "b", "c"]]
        }, (0, 1), (2, 3))

        results = []
        for items, p in template.items_safe():
            results.append((items, p))

        self.assertEqual(results, [
            (['1', '2', '3'], ['Fn::If', 1]),
            (['a', 'b', 'c'], ['Fn::If', 2])
        ])

    def test_success_fnif_list_strings(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1', '2', '3'
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('3', [2])])

    def test_success_fnif_list_conditions(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1',
            '2',
            cfnlint.decode.node.dict_node({
                'Fn::If': [
                    'string',
                    '4',
                    '5']
            }, (0, 1), (2, 3)),
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('4', [2, 'Fn::If', 1]), ('5', [2, 'Fn::If', 2])])

    def test_success_fnif_list_conditions_no_value(self):
        """Test List Object"""
        template = cfnlint.decode.node.list_node([
            '1',
            '2',
            cfnlint.decode.node.dict_node({
                'Fn::If': [
                    'string',
                    '4',
                    cfnlint.decode.node.dict_node({
                        "Ref": "AWS::NoValue"
                    }, (0, 1), (2, 3))
                ]
            }, (0, 1), (2, 3)),
        ], (0, 1), (2, 3))

        results = []
        for v, p in template.items_safe():
            results.append((v, p))

        self.assertEqual(results, [('1', [0]), ('2', [1]), ('4', [2, 'Fn::If', 1])])
