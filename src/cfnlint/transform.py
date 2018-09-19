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
import os
import six

from samtranslator.parser import parser
from samtranslator.translator.translator import Translator
from samtranslator.public.exceptions import InvalidDocumentException

import cfnlint.helpers
from cfnlint.decode.node import dict_node, list_node


class Transform(object):
    """
    Application Serverless Module tranform Wrappor. Based on code from AWS SAM CLI:
    https://github.com/awslabs/aws-sam-cli/blob/develop/samcli/commands/validate/lib/sam_template_validator.py
    """

    def __init__(self, filename, template, region):
        """
        Initialize Transform class
        """
        self._filename = filename
        self._template = template
        self._region = region

        self._managed_policy_map = self.load_managed_policies()
        self._sam_parser = parser.Parser()

    def template(self):
        """Get the template"""
        return self._template

    def load_managed_policies(self):
        """
        Load the ManagedPolicies locally, based on the AWS-CLI:
        https://github.com/awslabs/aws-sam-cli/blob/develop/samcli/lib/samlib/default_managed_policies.json
        """
        return cfnlint.helpers.load_resources('data/Serverless/ManagedPolicies.json')

    def _replace_local_codeuri(self):
        """
        Replaces the CodeUri in AWS::Serverless::Function and DefinitionUri in AWS::Serverless::Api to a fake
        S3 Uri. This is to support running the SAM Translator with valid values for these fields. If this in not done,
        the template is invalid in the eyes of SAM Translator (the translator does not support local paths)
        """

        all_resources = self._template.get('Resources', {})

        for _, resource in all_resources.items():

            resource_type = resource.get('Type')
            resource_dict = resource.get('Properties')

            if resource_type == 'AWS::Serverless::Function':

                Transform._update_to_s3_uri('CodeUri', resource_dict)

            if resource_type == 'AWS::Serverless::Api':
                if 'DefinitionBody' not in resource_dict:
                    Transform._update_to_s3_uri('DefinitionUri', resource_dict)

    def transform_template(self):
        """
        Transform the Template using the Serverless Application Model.
        """
        matches = []

        try:
            sam_translator = Translator(managed_policy_map=self._managed_policy_map,
                                        sam_parser=self._sam_parser)

            self._replace_local_codeuri()

            # Tell SAM to use the region we're linting in, this has to be controlled using the default AWS mechanisms, see also:
            # https://github.com/awslabs/serverless-application-model/blob/master/samtranslator/translator/arn_generator.py
            os.environ['AWS_DEFAULT_REGION'] = self._region

            # In the Paser class, within the SAM Translator, they log a warning for when the template
            # does not match the schema. The logger they use is the root logger instead of one scoped to
            # their module. Currently this does not cause templates to fail, so we will suppress this
            # by patching the logging.warning method that is used in that class.
            class WarningSuppressLogger(object):
                """ Patch the Logger in SAM """

                def __init__(self, obj_to_patch):
                    self.obj_to_patch = obj_to_patch

                def __enter__(self):
                    self.obj_to_patch.warning = self.warning

                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.obj_to_patch.warning = self.obj_to_patch.warning

                def warning(self, message):
                    """ Ignore warnings from SAM """
                    pass

            with WarningSuppressLogger(parser.logging):
                self._template = sam_translator.translate(sam_template=self._template, parameter_values={})
                self._correct_objects()
        except InvalidDocumentException as e:
            for cause in e.causes:
                matches.append(cfnlint.Match(
                    1, 1,
                    1, 1,
                    self._filename, cfnlint.TransformError(), cause.message))

        return matches

    def _correct_objects_loop(self, template):
        """
            Looping for dynamic depths and types
        """
        if isinstance(template, dict):
            if not isinstance(template, dict_node):
                template = dict_node(template, (0, 0), (0, 0))
            for k, v in template.items():
                template[k] = self._correct_objects_loop(v)
        elif isinstance(template, list):
            if not isinstance(template, list_node):
                template = list_node(template, (0, 0), (0, 0))
            for i, v in enumerate(template):
                template[i] = self._correct_objects_loop(v)

        return template

    def _correct_objects(self):
        """
            Corrects the template to have the correct types of objects, list, strings
        """
        self._template = self._correct_objects_loop(self._template)

    @staticmethod
    def is_s3_uri(uri):
        """
        Checks the uri and determines if it is a valid S3 Uri
        Parameters
        ----------
        uri str, required
            Uri to check
        Returns
        -------
        bool
            Returns True if the uri given is an S3 uri, otherwise False
        """
        return isinstance(uri, six.string_types) and uri.startswith('s3://')

    @staticmethod
    def _update_to_s3_uri(property_key, resource_property_dict, s3_uri_value='s3://bucket/value'):
        """
        Updates the 'property_key' in the 'resource_property_dict' to the value of 's3_uri_value'
        Note: The function will mutate the resource_property_dict that is pass in
        Parameters
        ----------
        property_key str, required
            Key in the resource_property_dict
        resource_property_dict dict, required
            Property dictionary of a Resource in the template to replace
        s3_uri_value str, optional
            Value to update the value of the property_key to
        """
        uri_property = resource_property_dict.get(property_key, '.')

        # ignore if dict or already an S3 Uri
        if isinstance(uri_property, dict) or Transform.is_s3_uri(uri_property):
            return

        resource_property_dict[property_key] = s3_uri_value
