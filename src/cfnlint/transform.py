"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
import logging
import six
import samtranslator
import copy
import json
from samtranslator.parser import parser
from samtranslator.translator.translator import Translator
from samtranslator.public.exceptions import InvalidDocumentException

from cfnlint.helpers import load_resource, convert_dict, format_json_string
from cfnlint.data import Serverless
from cfnlint.rules import Match, TransformError
from cfnlint.decode import cfn_yaml
LOGGER = logging.getLogger('cfnlint')

samtranslator_logger = logging.getLogger('samtranslator')
samtranslator_logger.setLevel(logging.CRITICAL)

class Transform(object):
    """
    Application Serverless Module tranform Wrapper.
    Based on code from AWS SAM CLI:
    https://github.com/awslabs/aws-sam-cli/blob/develop/samcli/commands/validate/lib/sam_template_validator.py
    """

    def __init__(self, filename, template, region):
        """
        Initialize Transform class
        """
        self._filename = filename
        self._template = template
        self._region = region
        self._parameters = {}

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
        return load_resource(Serverless, 'ManagedPolicies.json')

    def _replace_local_codeuri(self):
        """
        Replaces the CodeUri in AWS::Serverless::Function and DefinitionUri in
        AWS::Serverless::Api to a fake S3 Uri. This is to support running the
        SAM Translator with valid values for these fields. If this is not done,
        the template is invalid in the eyes of SAM Translator (the translator
        does not support local paths)
        """

        all_resources = self._template.get('Resources', {})

        template_globals = self._template.get('Globals', {})
        auto_publish_alias = template_globals.get('Function', {}).get('AutoPublishAlias')
        if isinstance(auto_publish_alias, dict):
            if len(auto_publish_alias) == 1:
                for k, v in auto_publish_alias.items():
                    if k == 'Ref':
                        if v in self._template.get('Parameters'):
                            self._parameters[v] = 'Alias'


        for _, resource in all_resources.items():

            resource_type = resource.get('Type')
            resource_dict = resource.get('Properties')

            if resource_type == 'AWS::Serverless::Function':

                Transform._update_to_s3_uri('CodeUri', resource_dict)
                auto_publish_alias = resource_dict.get('AutoPublishAlias')
                if isinstance(auto_publish_alias, dict):
                    if len(auto_publish_alias) == 1:
                        for k, v in auto_publish_alias.items():
                            if k == 'Ref':
                                if v in self._template.get('Parameters'):
                                    self._parameters[v] = 'Alias'
            if resource_type in ['AWS::Serverless::LayerVersion']:
                if resource_dict.get('ContentUri'):
                    Transform._update_to_s3_uri('ContentUri', resource_dict)
            if resource_type == 'AWS::Serverless::Application':
                if resource_dict.get('Location'):
                    resource_dict['Location'] = ''
                    Transform._update_to_s3_uri('Location', resource_dict)
            if resource_type == 'AWS::Serverless::Api':
                if ('DefinitionBody' not in resource_dict and
                        'Auth' not in resource_dict and 'Cors' not in resource_dict):
                    Transform._update_to_s3_uri('DefinitionUri', resource_dict)
                else:
                    resource_dict['DefinitionBody'] = ''
            if resource_type == 'AWS::Serverless::StateMachine' and resource_dict.get('DefinitionUri'):
                Transform._update_to_s3_uri('DefinitionUri', resource_dict)

    def transform_template(self):
        """
        Transform the Template using the Serverless Application Model.
        """
        matches = []

        try:
            # Output the SAM Translator version in debug mode
            LOGGER.info('SAM Translator: %s', samtranslator.__version__)

            sam_translator = Translator(
                managed_policy_map=self._managed_policy_map,
                sam_parser=self._sam_parser)

            self._replace_local_codeuri()

            # Tell SAM to use the region we're linting in, this has to be
            # controlled using the default AWS mechanisms, see also:
            # https://github.com/awslabs/serverless-application-model/blob/master/samtranslator/translator/arn_generator.py
            LOGGER.info('Setting AWS_DEFAULT_REGION to %s', self._region)
            os.environ['AWS_DEFAULT_REGION'] = self._region
            _oldtemplate = copy.deepcopy(self._template)
            _single_line_template = convert_dict(
                sam_translator.translate(sam_template=self._template,
                                         parameter_values=self._parameters)
            )

            #Iterate over resources and copy metadata where it needs to be.
            for k,v in sam_translator.translated_resource_mapping.items():
                _metadata = _oldtemplate['Resources'][k].get('Metadata',{}).get('cfn-lint')
                if _metadata:
                    for r in v:
                        _single_line_template['Resources'][r].update({"Metadata":{"cfn-lint":_metadata}})

            # Pretty-print it, then run it through the loader again to update line numbers
            self._template = cfn_yaml.loads(json.dumps(_single_line_template, indent=4, default=str))


            LOGGER.info('Transformed template: \n%s',
                        format_json_string(self._template))


        except InvalidDocumentException as e:
            message = 'Error transforming template: {0}'
            for cause in e.causes:
                matches.append(Match(
                    1, 1,
                    1, 1,
                    self._filename,
                    TransformError(), message.format(cause.message)))
        except Exception as e:  # pylint: disable=W0703
            LOGGER.debug('Error transforming template: %s', str(e))
            LOGGER.debug('Stack trace: %s', e, exc_info=True)
            message = 'Error transforming template: {0}'
            matches.append(Match(
                1, 1,
                1, 1,
                self._filename,
                TransformError(), message.format(str(e))))

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
    def _update_to_s3_uri(
            property_key, resource_property_dict,
            s3_uri_value='s3://bucket/value'):
        """
        Updates the 'property_key' in the 'resource_property_dict' to the
        value of 's3_uri_value'
        Note: The function will mutate the resource_property_dict that is pass
        in Parameters
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
        if isinstance(uri_property, dict):
            if len(uri_property) == 1:
                for k in uri_property.keys():
                    if k == 'Ref':
                        resource_property_dict[property_key] = s3_uri_value
            return
        if Transform.is_s3_uri(uri_property):
            return

        resource_property_dict[property_key] = s3_uri_value
