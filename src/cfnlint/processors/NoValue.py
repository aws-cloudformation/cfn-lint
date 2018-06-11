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
import logging
import cfnlint.processors

LOGGER = logging.getLogger(__name__)


class NoValue(cfnlint.processors.CloudFormationProcessor):
    """CloudFormation Transform Support"""
    type = 'NoValue'

    def run(self, cfn):
        """
            Main engine to run conditions processor
            Input: cfn (Template class)
            Output: Array of Template class objects with modified templates
        """
        self.check_obj(cfn.template)
        return cfn

    def check_obj(self, obj):
        """
            Check and iterate an object removing elements that are 'Ref: AWS::NoValue'
        """

        if not isinstance(obj, dict):
            return
        for key, value in obj.copy().items():
            if isinstance(value, dict):
                if len(value) == 1:
                    for sub_key, sub_value in value.items():
                        if sub_key == 'Ref' and sub_value == 'AWS::NoValue':
                            del obj[key]
                        else:
                            self.check_obj(sub_value)
                else:
                    self.check_obj(value)
            elif isinstance(value, list):
                for index, list_item in enumerate(value):
                    if isinstance(list_item, dict):
                        if len(list_item) == 1:
                            for sub_key, sub_value in list_item.items():
                                if sub_key == 'Ref' and sub_value == 'AWS::NoValue':
                                    del obj[key][index]
                                else:
                                    self.check_obj(sub_value)
                        else:
                            self.check_obj(list_item)
