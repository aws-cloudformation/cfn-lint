"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fnmatch
import gzip
import hashlib
import json
import multiprocessing
import os
import re
import sys
import logging
from io import BytesIO
import jsonpatch
import jsonpointer

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen

from cfnlint.data import CloudSpecs

LOGGER = logging.getLogger(__name__)

SPEC_REGIONS = {
    'af-south-1': 'https://cfn-resource-specifications-af-south-1-prod.s3.af-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-east-1': 'https://cfn-resource-specifications-ap-east-1-prod.s3.ap-east-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-1': 'https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-2': 'https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-3': 'https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-south-1': 'https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-southeast-1': 'https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-southeast-2': 'https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ca-central-1': 'https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'cn-north-1': 'https://cfn-resource-specifications-cn-north-1-prod.s3.cn-north-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json',
    'cn-northwest-1': 'https://cfn-resource-specifications-cn-northwest-1-prod.s3.cn-northwest-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-central-1': 'https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-north-1': 'https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-south-1': 'https://cfn-resource-specifications-eu-south-1-prod.s3.eu-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-1': 'https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-2': 'https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-3': 'https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'me-south-1': 'https://cfn-resource-specifications-me-south-1-prod.s3.me-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'sa-east-1': 'https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-east-1': 'https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-east-2': 'https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-gov-east-1': 'https://s3.us-gov-east-1.amazonaws.com/cfn-resource-specifications-us-gov-east-1-prod/latest/gzip/CloudFormationResourceSpecification.json',
    'us-gov-west-1': 'https://s3.us-gov-west-1.amazonaws.com/cfn-resource-specifications-us-gov-west-1-prod/latest/gzip/CloudFormationResourceSpecification.json',
    'us-west-1': 'https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-west-2': 'https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
}
REGIONS = list(SPEC_REGIONS.keys())
RESOURCE_SPECS = {}


def override_specs(override_spec_file):
    """Override specs file"""
    try:
        filename = override_spec_file
        with open(filename) as fp:
            custom_spec_data = json.load(fp)

        set_specs(custom_spec_data)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Override spec file not found: %s', filename)
            sys.exit(1)
        elif e.errno == 21:
            LOGGER.error('Override spec file references a directory, not a file: %s', filename)
            sys.exit(1)
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing override spec file: %s', filename)
            sys.exit(1)
    except (ValueError) as err:
        LOGGER.error('Override spec file %s is malformed: %s', filename, err)
        sys.exit(1)


def set_specs(override_spec_data):
    """ Set Resource Specs """

    excludes = []
    includes = []

    # Extract the exclude list from the override file
    if 'ExcludeResourceTypes' in override_spec_data:
        excludes = override_spec_data.pop('ExcludeResourceTypes')
    if 'IncludeResourceTypes' in override_spec_data:
        includes = override_spec_data.pop('IncludeResourceTypes')

    for region, spec in RESOURCE_SPECS.items():

        # Merge override spec file into the AWS Resource specification
        if override_spec_data:
            RESOURCE_SPECS[region] = merge_spec(override_spec_data, spec)

        # Grab a list of all resources
        all_resources = list(RESOURCE_SPECS[region]['ResourceTypes'].keys())[:]

        resources = []

        # Remove unsupported resource using includes
        if includes:
            for include in includes:
                regex = re.compile(include.replace('*', '(.*)') + '$')
                matches = [string for string in all_resources if re.match(regex, string)]

                resources.extend(matches)
        else:
            resources = all_resources[:]

        # Remove unsupported resources using the excludes
        if excludes:
            for exclude in excludes:
                regex = re.compile(exclude.replace('*', '(.*)') + '$')
                matches = [string for string in resources if re.match(regex, string)]

                for match in matches:
                    resources.remove(match)

        # Remove unsupported resources
        for resource in all_resources:
            if resource not in resources:
                del RESOURCE_SPECS[region]['ResourceTypes'][resource]


def merge_spec(source, destination):
    """ Recursive merge spec dict """

    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_spec(value, node)
        else:
            destination[key] = value

    return destination


def load_resource(package, filename='us-east-1.json'):
    """Load CloudSpec resources
        :param filename: filename to load
        :return: Json output of the resource laoded
    """
    return json.loads(pkg_resources.read_text(package, filename, encoding='utf-8'))


def save_metadata(metadata, filename):
    """Save the contents of the download metadata file"""
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    with open(filename, 'w') as metadata_file:
        json.dump(metadata, metadata_file)


def load_metadata(filename):
    """Get the contents of the download metadata file"""
    metadata = {}
    if os.path.exists(filename):
        with open(filename, 'r') as metadata_file:
            metadata = json.load(metadata_file)
    return metadata


def get_url_content(url, caching=False):
    """Get the contents of a spec file"""

    res = urlopen(url)

    if caching and res.info().get('ETag'):
        metadata_filename = get_metadata_filename(url)
        # Load in all existing values
        metadata = load_metadata(metadata_filename)
        metadata['etag'] = res.info().get('ETag')
        metadata['url'] = url # To make it obvious which url the Tag relates to
        save_metadata(metadata, metadata_filename)

    # Continue to handle the file download normally
    if res.info().get('Content-Encoding') == 'gzip':
        buf = BytesIO(res.read())
        f = gzip.GzipFile(fileobj=buf)
        content = f.read().decode('utf-8')
    else:
        content = res.read().decode('utf-8')

    return content


def url_has_newer_version(url):
    """Checks to see if a newer version of the resource at the URL is available
    Always returns true if using Python2.7 due to lack of HEAD request support,
    or if we have no caching information for the local version of the resource
    """
    metadata_filename = get_metadata_filename(url)

    # Load in the cache
    metadata = load_metadata(metadata_filename)

    # Etag is a caching identifier used by S3 and Cloudfront
    if 'etag' in metadata:
        cached_etag = metadata['etag']
    else:
        # If we don't know the etag of the local version, we should force an update
        return True

    # Need to wrap this in a try, as URLLib2 in Python2 doesn't support HEAD requests
    try:
        # Make an initial HEAD request
        req = Request(url, method='HEAD')
        res = urlopen(req)

    except NameError:
        # We should force an update
        return True

    # If we have an ETag value stored and it matches the returned one,
    # then we already have a copy of the most recent version of the
    # resource, so don't bother fetching it again
    if cached_etag and res.info().get('ETag') and cached_etag == res.info().get('ETag'):
        LOGGER.debug('We already have a cached version of url %s with ETag value of %s', url, cached_etag)
        return False

    # The ETag value of the remote resource does not match the local one, so a newer version is available
    return True


def get_metadata_filename(url):
    """Returns the filename for a metadata file associated with a remote resource"""
    caching_dir = os.path.join(os.path.dirname(__file__), 'data', 'DownloadsMetadata')
    encoded_url = hashlib.sha256(url.encode()).hexdigest()
    metadata_filename = os.path.join(caching_dir, encoded_url + '.meta.json')

    return metadata_filename

def initialize_specs():
    """ Initialize Resource Specs """
    for reg in REGIONS:
        RESOURCE_SPECS[reg] = load_resource(CloudSpecs, filename=('%s.json' % reg))

initialize_specs()


def update_resource_specs():
    """ Update Resource Specs """

    # Pool() uses cpu count if no number of processors is specified
    # Pool() only implements the Context Manager protocol from Python3.3 onwards,
    # so it will fail Python2.7 style linting, as well as throw AttributeError
    try:
        # pylint: disable=not-context-manager
        with multiprocessing.Pool() as pool:
            pool.starmap(update_resource_spec, SPEC_REGIONS.items())
    except AttributeError:

        # Do it the long, slow way
        for region, url in SPEC_REGIONS.items():
            update_resource_spec(region, url)


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
            all_patches = jsonpatch.JsonPatch(load_resource(
                'cfnlint.data.ExtendedSpecs.{}'.format(module), file_path))

            # Process the generic patches 1 by 1 so we can "ignore" failed ones
            for all_patch in all_patches:
                try:
                    jsonpatch.JsonPatch([all_patch]).apply(content, in_place=True)
                except jsonpatch.JsonPatchConflict:
                    LOGGER.debug('Patch (%s) not applied in region %s', all_patch, region)
                except jsonpointer.JsonPointerException:
                    # Debug as the parent element isn't supported in the region
                    LOGGER.debug('Parent element not found for patch (%s) in region %s',
                                 all_patch, region)

    return content


def update_resource_spec(region, url):
    """ Update a single resource spec """
    filename = os.path.join(os.path.dirname(__file__), 'data/CloudSpecs/%s.json' % region)

    multiprocessing_logger = multiprocessing.log_to_stderr()

    multiprocessing_logger.debug('Downloading template %s into %s', url, filename)

    # Check to see if we already have the latest version, and if so stop
    if not url_has_newer_version(url):
        return

    spec_content = get_url_content(url, caching=True)

    multiprocessing_logger.debug('A more recent version of %s was found, and will be downloaded to %s', url, filename)
    spec = json.loads(spec_content)

    # Patch the files
    spec = patch_spec(spec, 'all')
    spec = patch_spec(spec, region)

    with open(filename, 'w') as f:
        json.dump(spec, f, indent=2, sort_keys=True, separators=(',', ': '))
