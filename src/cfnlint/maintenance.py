"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fnmatch
import json
import logging
import multiprocessing
import os
import subprocess
import zipfile
import re
from io import BytesIO
import warnings
from urllib.request import urlopen, Request
import jsonpatch
import cfnlint
from cfnlint.helpers import get_url_content, url_has_newer_version
from cfnlint.helpers import SPEC_REGIONS
import cfnlint.data.AdditionalSpecs


LOGGER = logging.getLogger(__name__)

REGISTRY_SCHEMA_ZIP = 'https://schema.cloudformation.us-east-1.amazonaws.com/CloudformationSchema.zip'


def update_resource_specs(force: bool=False):
    # Pool() uses cpu count if no number of processors is specified
    # Pool() only implements the Context Manager protocol from Python3.3 onwards,
    # so it will fail Python2.7 style linting, as well as throw AttributeError
    schema_cache = get_schema_value_types()
    try:
        # pylint: disable=not-context-manager
        with multiprocessing.Pool() as pool:
            # Patch from registry schema
            pool_tuple = [(k, v, schema_cache, force) for k, v in SPEC_REGIONS.items()]
            pool.starmap(update_resource_spec, pool_tuple)
    except AttributeError:

        # Do it the long, slow way
        for region, url in SPEC_REGIONS.items():
            update_resource_spec(region, url, schema_cache, force)


def update_resource_spec(region, url, schema_cache, force: bool=False):
    """ Update a single resource spec """
    filename = os.path.join(os.path.dirname(cfnlint.__file__), f'data/CloudSpecs/{region}.json')

    multiprocessing_logger = multiprocessing.log_to_stderr()

    multiprocessing_logger.debug('Downloading template %s into %s', url, filename)

    # Check to see if we already have the latest version, and if so stop
    if not (url_has_newer_version(url) or force):
        return

    spec_content = get_url_content(url, caching=True)

    multiprocessing_logger.debug(
        'A more recent version of %s was found, and will be downloaded to %s', url, filename)
    spec = json.loads(spec_content)

    # Patch the files
    spec = patch_spec(spec, 'all')
    spec = patch_spec(spec, region)

    # do each patch individually so we can ignore errors
    for patch in schema_cache:
        try:
            # since there could be patched in values to ValueTypes
            # Ref/GetAtt as an example.  So we want to add new
            # ValueTypes that don't exist
            for i_patch in patch:
                path_details = i_patch.get('path').split('/')
                if path_details[1] == 'ValueTypes':
                    if not spec.get('ValueTypes').get(path_details[2]):
                        spec['ValueTypes'][path_details[2]] = {}
            # do the patch
            jsonpatch.JsonPatch(patch).apply(spec, in_place=True)
        except jsonpatch.JsonPatchConflict:
            for i_patch in patch:
                path_details = i_patch.get('path').split('/')
                if path_details[1] == 'ValueTypes':
                    if not spec.get('ValueTypes').get(path_details[2]):
                        try:
                            del spec['ValueTypes'][path_details[2]]
                        except:  # pylint: disable=bare-except
                            pass
            LOGGER.debug('Patch (%s) not applied in region %s', patch, region)
        except jsonpatch.JsonPointerException:
            for i_patch in patch:
                path_details = i_patch.get('path').split('/')
                if path_details[1] == 'ValueTypes':
                    if not spec.get('ValueTypes').get(path_details[2]):
                        try:
                            del spec['ValueTypes'][path_details[2]]
                        except:  # pylint: disable=bare-except
                            pass
            # Debug as the parent element isn't supported in the region
            LOGGER.debug('Parent element not found for patch (%s) in region %s',
                         patch, region)

    botocore_cache = {}

    def search_and_replace_botocore_types(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for key, value in obj.items():
                if key == 'botocore':
                    service_and_type = value.split('/')
                    service = '/'.join(service_and_type[:-1])
                    botocore_type = service_and_type[-1]
                    if service not in botocore_cache:
                        botocore_cache[service] = json.loads(get_url_content(
                            'https://raw.githubusercontent.com/boto/botocore/master/botocore/data/' + service + '/service-2.json'))
                    new_obj['AllowedValues'] = sorted(
                        botocore_cache[service]['shapes'][botocore_type]['enum'])
                else:
                    new_obj[key] = search_and_replace_botocore_types(value)
            return new_obj

        if isinstance(obj, list):
            new_list = []
            for item in obj:
                new_list.append(search_and_replace_botocore_types(item))
            return new_list

        return obj

    spec = search_and_replace_botocore_types(spec)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, sort_keys=True, separators=(',', ': '))


def update_documentation(rules):
    # Update the overview of all rules in the linter
    filename = 'docs/rules.md'

    # Sort rules by the Rule ID
    sorted_rules = sorted(rules, key=lambda obj: obj.id)

    data = []

    # Read current file up to the Rules part, everything up to that point is
    # static documentation.
    with open(filename, 'r', encoding='utf-8') as original_file:

        line = original_file.readline()
        while line:
            data.append(line)

            if line == '## Rules\n':
                break

            line = original_file.readline()

    # Rebuild the file content
    with open(filename, 'w', encoding='utf-8') as new_file:

        # Rewrite the static documentation
        for line in data:
            new_file.write(line)

        # Add the rules
        new_file.write(
            '(_This documentation is generated by running `cfn-lint --update-documentation`, do not alter this manually_)\n\n')
        new_file.write(
            'The following **{}** rules are applied by this linter:\n\n'.format(len(sorted_rules) + 3))
        new_file.write(
            '| Rule ID  | Title | Description | Config<br />(Name:Type:Default) | Source | Tags |\n')
        new_file.write('| -------- | ----- | ----------- | ---------- | ------ | ---- |\n')

        rule_output = '| [{0}<a name="{0}"></a>]({6}) | {1} | {2} | {3} | [Source]({4}) | {5} |\n'

        for rule in [cfnlint.rules.ParseError(), cfnlint.rules.TransformError(), cfnlint.rules.RuleError()] + sorted_rules:
            # pylint: disable=invalid-string-quote
            rule_source_code_file = '../' + subprocess.check_output(['git', 'grep', '-l', "id = '" + rule.id + "'", 'src/cfnlint/rules/']).decode(
                'ascii').strip()
            rule_id = rule.id + '*' if rule.experimental else rule.id
            tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
            config = '<br />'.join('{0}:{1}:{2}'.format(key, values.get('type'), values.get('default'))
                                   for key, values in rule.config_definition.items())
            new_file.write(rule_output.format(rule_id, rule.shortdesc,
                                              rule.description, config, rule.source_url, tags, rule_source_code_file))
        new_file.write('\n\\* experimental rules\n')


def patch_spec(content, region):
    """Patch the spec file"""
    LOGGER.info('Patching spec file for region "%s"', region)

    append_dir = os.path.join(os.path.dirname(__file__), 'data', 'ExtendedSpecs', region)
    for dirpath, _, filenames in os.walk(append_dir):
        filenames.sort()
        for filename in fnmatch.filter(filenames, '*.json'):
            file_path = os.path.basename(filename)
            module = dirpath.replace('%s' % append_dir, '%s' % region).replace(os.path.sep, '.')
            LOGGER.info('Processing %s/%s', module, file_path)
            all_patches = jsonpatch.JsonPatch(cfnlint.helpers.load_resource(
                'cfnlint.data.ExtendedSpecs.{}'.format(module), file_path))

            # Process the generic patches 1 by 1 so we can "ignore" failed ones
            for all_patch in all_patches:
                try:
                    jsonpatch.JsonPatch([all_patch]).apply(content, in_place=True)
                except jsonpatch.JsonPatchConflict:
                    LOGGER.debug('Patch (%s) not applied in region %s', all_patch, region)
                except jsonpatch.JsonPointerException:
                    # Debug as the parent element isn't supported in the region
                    LOGGER.debug('Parent element not found for patch (%s) in region %s',
                                 all_patch, region)

    return content


def update_iam_policies():
    """update iam policies file"""

    url = 'https://awspolicygen.s3.amazonaws.com/js/policies.js'

    filename = os.path.join(
        os.path.dirname(cfnlint.data.AdditionalSpecs.__file__),
        'Policies.json')
    LOGGER.debug('Downloading policies %s into %s', url, filename)

    content = get_url_content(url)

    content = content.split('app.PolicyEditorConfig=')[1]
    content = json.loads(content)

    actions = {
        'Manage Amazon API Gateway': ['HEAD', 'OPTIONS'],
        'Amazon API Gateway Management': ['HEAD', 'OPTIONS'],
        'Amazon API Gateway Management V2': ['HEAD', 'OPTIONS'],
        'Amazon Kinesis Video Streams': ['StartStreamEncryption'],
    }
    for k, v in actions.items():
        if content.get('serviceMap').get(k):
            content['serviceMap'][k]['Actions'].extend(v)
        else:
            LOGGER.debug('"%s" was not found in the policies file', k)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, sort_keys=True, separators=(',', ': '))


def get_schema_value_types():

    def resolve_refs(properties, schema):
        results = {}
        name = None

        if properties.get('$ref'):
            name = properties.get('$ref').split('/')[-1]
            subname, results = resolve_refs(schema.get('definitions').get(name), schema)
            if subname:
                name = subname
            properties = schema.get('definitions').get(name)

        if properties.get('type') == 'array':
            results = properties.get('items')

        if results:
            properties = results

        if results and results.get('$ref'):
            name, results = resolve_refs(results, schema)

        if not results:
            return name, properties

        return name, results

    def get_object_details(names, properties, schema):
        results = {}
        warnings.filterwarnings('error')
        for propname, propdetails in properties.items():
            subname, propdetails = resolve_refs(propdetails, schema)
            t = propdetails.get('type')
            if not t:
                continue
            if t in ['object']:
                if subname is None:
                    subname = propname
                if propdetails.get('properties'):
                    if subname not in names:
                        results.update(get_object_details(
                            names + [subname], propdetails.get('properties'), schema))
                elif propdetails.get('oneOf') or propdetails.get('anyOf') or propdetails.get('allOf'):
                    LOGGER.info(
                        'Type %s object for %s has only oneOf,anyOf, or allOf properties', names[0], propname)
                    continue
            elif t not in ['string', 'integer', 'number', 'boolean']:
                if propdetails.get('$ref'):
                    results.update(get_object_details(
                        names + [propname], schema.get('definitions').get(t.get('$ref').split('/')[-1]), schema))
                elif isinstance(t, list):
                    LOGGER.info('Type for %s object and %s property is a list', names[0], propname)
                else:
                    LOGGER.info('Unable to handle %s object for %s property', names[0], propname)
            elif t == 'string':
                if not results.get('.'.join(names + [propname])):
                    if propdetails.get('pattern') or (propdetails.get('minLength') and propdetails.get('maxLength')) or propdetails.get('enum'):
                        results['.'.join(names + [propname])] = {}
                if propdetails.get('pattern'):
                    p = propdetails.get('pattern')
                    if '.'.join(names + [propname]) == 'AWS::OpsWorksCM::Server.CustomPrivateKey':
                        # one off exception to handle a weird parsing issue in python 2.7
                        continue
                    # python 3 has the ability to test isascii
                    # python 3.7 introduces is ascii so switching to encode
                    try:
                        p.encode('ascii')
                    except UnicodeEncodeError:
                        continue
                    try:
                        if '\\p{' in p:
                            continue
                        re.compile(p, re.UNICODE)
                        results['.'.join(names + [propname])].update({
                            'AllowedPatternRegex': p
                        })
                    except:  #pylint: disable=bare-except
                        LOGGER.info(
                            'Unable to handle regex for type %s and property %s with regex %s', names[0], propname, p)
                if propdetails.get('minLength') and propdetails.get('maxLength'):
                    results['.'.join(names + [propname])].update({
                        'StringMin': propdetails.get('minLength'),
                        'StringMax': propdetails.get('maxLength'),
                    })
                if propdetails.get('enum'):
                    results['.'.join(names + [propname])].update({
                        'AllowedValues': propdetails.get('enum')
                    })
            elif t in ['number', 'integer']:
                if not results.get('.'.join(names + [propname])):
                    if propdetails.get('minimum') and propdetails.get('maximum'):
                        results['.'.join(names + [propname])] = {}
                if propdetails.get('minimum') and propdetails.get('maximum'):
                    results['.'.join(names + [propname])].update({
                        'NumberMin': propdetails.get('minimum'),
                        'NumberMax': propdetails.get('maximum'),
                    })

        return results

    def process_schema(schema):
        details = get_object_details([schema.get('typeName')], schema.get('properties'), schema)

        # Remove duplicates
        vtypes = {}
        for n, v in details.items():
            if n.count('.') > 1:
                s = n.split('.')
                vtypes[s[0] + '.' + '.'.join(s[-2:])] = v
            else:
                vtypes[n] = v

        patches = []
        for n, v in vtypes.items():
            patch = []
            if v:
                if n.count('.') == 2:
                    r_type = 'PropertyTypes'
                else:
                    r_type = 'ResourceTypes'
                element = {
                    'op': 'add',
                    'path': '/%s/%s/Properties/%s/Value' % (r_type, '.'.join(n.split('.')[0:-1]), n.split('.')[-1]),
                    'value': {
                        'ValueType': n,
                    },
                }
                patch.append(element)
                for s, vs in v.items():
                    element = {
                        'op': 'add',
                        'path': '/ValueTypes/%s/%s' % (n, s),
                        'value': vs,
                    }
                    patch.append(element)
            if patch:
                patches.append(patch)

        return patches

    req = Request(REGISTRY_SCHEMA_ZIP)
    res = urlopen(req)

    results = []

    with zipfile.ZipFile(BytesIO(res.read())) as z:
        for f in z.namelist():
            with z.open(f) as d:
                if not isinstance(d, str):
                    data = d.read()
                else:
                    data = d
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                schema = json.loads(data)
                patches = process_schema(schema)
                results.extend(patches)

    return results
