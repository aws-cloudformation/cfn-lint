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
import os
import logging
import six
import samtranslator
from samtranslator.parser import parser
from samtranslator.translator.translator import Translator
from samtranslator.public.exceptions import InvalidDocumentException

import cfnlint.helpers
LOGGER = logging.getLogger('cfnlint')

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
            if resource_type in ['AWS::Serverless::LayerVersion']:
                if resource_dict.get('ContentUri'):
                    Transform._update_to_s3_uri('ContentUri', resource_dict)
            if resource_type == 'AWS::Serverless::Application':
                if resource_dict.get('Location'):
                    resource_dict['Location'] = ''
                    Transform._update_to_s3_uri('Location', resource_dict)
            if resource_type == 'AWS::Serverless::Api':
                if 'DefinitionBody' not in resource_dict and 'Auth' not in resource_dict:
                    Transform._update_to_s3_uri('DefinitionUri', resource_dict)
                else:
                    resource_dict['DefinitionBody'] = ''

    def transform_template(self):
        """
        Transform the Template using the Serverless Application Model.
        """
        matches = []

        try:
            # Output the SAM Translator version in debug mode
            LOGGER.debug('SAM Translator: %s', samtranslator.__version__)

            sam_translator = Translator(managed_policy_map=self._managed_policy_map,
                                        sam_parser=self._sam_parser)

            self._replace_local_codeuri()

            # Tell SAM to use the region we're linting in, this has to be controlled using the default AWS mechanisms, see also:
            # https://github.com/awslabs/serverless-application-model/blob/master/samtranslator/translator/arn_generator.py
            LOGGER.debug('Setting AWS_DEFAULT_REGION to %s', self._region)
            os.environ['AWS_DEFAULT_REGION'] = self._region

            self._template = cfnlint.helpers.convert_dict(
                sam_translator.translate(sam_template=self._template, parameter_values={}))

            LOGGER.debug('Transformed template: %s', self._template)
        except InvalidDocumentException as e:
            message = 'Error transforming template: {0}'
            for cause in e.causes:
                matches.append(cfnlint.Match(
                    1, 1,
                    1, 1,
                    self._filename, cfnlint.TransformError(), message.format(cause.message)))
        except Exception as e:  # pylint: disable=W0703
            LOGGER.debug('Error transforming template: %s', str(e))
            LOGGER.debug('Stack trace: %s', e, exc_info=True)
            message = 'Error transforming template: {0}'
            matches.append(cfnlint.Match(
                1, 1,
                1, 1,
                self._filename, cfnlint.TransformError(), message.format(str(e))))

        return matches

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
