"""
Helpers for loading resources, managing specs, constants, etc.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import datetime
import fnmatch
import gzip
import hashlib
import importlib
import importlib.resources as pkg_resources
import inspect
import json
import logging
import os
import sys
from io import BytesIO
from typing import List
from urllib.request import Request, urlopen, urlretrieve

import regex as re

LOGGER = logging.getLogger(__name__)

REGIONS = [
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    # "ap-south-2",  # no schemas yet
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    # "ap-southeast-4",  no schemas yet
    "ca-west-1",
    "ca-central-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-central-1",
    # "eu-central-2",  no schemas yet
    "eu-north-1",
    "eu-south-1",
    # "eu-south-2",  no schemas yet
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-south-1",
    # "me-central-1",  no schemas yet
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-gov-east-1",
    "us-gov-west-1",
    "us-west-1",
    "us-west-2",
]

TAG_MAP = "tag:yaml.org,2002:map"
UNCONVERTED_SUFFIXES = ["Ref", "Condition"]
FN_PREFIX = "Fn::"
CONDITION_FUNCTIONS = ["Fn::If"]

REGEX_ALPHANUMERIC = re.compile("^[a-zA-Z0-9]*$")
REGEX_CIDR = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$"
)
REGEX_IPV4 = re.compile(
    r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$"
)
REGEX_IPV6 = re.compile(
    r"^(((?=.*(::))(?!.*\3.+\3))\3?|[\dA-F]{1,4}:)([\dA-F]{1,4}(\3|:\b)|\2){5}(([\dA-F]{1,4}(\3|:\b|$)|\2){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})\Z",
    re.I | re.S,
)
REGEX_DYN_REF = re.compile(r"^.*{{resolve:.+}}.*$")
REGEX_DYN_REF_SSM = re.compile(r"^.*{{resolve:ssm:[a-zA-Z0-9_\.\-/]+(:\d+)?}}.*$")
REGEX_DYN_REF_SSM_SECURE = re.compile(
    r"^.*{{resolve:ssm-secure:[a-zA-Z0-9_\.\-/]+(:\d+)?}}.*$"
)

FUNCTIONS = [
    "Fn::Base64",
    "Fn::GetAtt",
    "Fn::GetAZs",
    "Fn::ImportValue",
    "Fn::Join",
    "Fn::Split",
    "Fn::FindInMap",
    "Fn::Select",
    "Ref",
    "Fn::If",
    "Fn::Contains",
    "Fn::Sub",
    "Fn::Cidr",
    "Fn::Length",
    "Fn::ToJsonString",
]

FUNCTIONS_MULTIPLE = ["Fn::GetAZs", "Fn::Split"]

# FindInMap can be singular or multiple.  This needs to be accounted for individually
FUNCTIONS_SINGLE = list(set(FUNCTIONS) - set(FUNCTIONS_MULTIPLE) - set("Fn::FindInMap"))

FUNCTION_IF = "Fn::If"
FUNCTION_AND = "Fn::And"
FUNCTION_OR = "Fn::Or"
FUNCTION_NOT = "Fn::Not"
FUNCTION_EQUALS = "Fn::Equals"
FUNCTION_FOR_EACH = re.compile(r"^Fn::ForEach::[a-zA-Z0-9]+$")

PSEUDOPARAMS_SINGLE = [
    "AWS::AccountId",
    "AWS::Partition",
    "AWS::Region",
    "AWS::StackId",
    "AWS::StackName",
    "AWS::URLSuffix",
]

PSEUDOPARAMS_MULTIPLE = [
    "AWS::NotificationARNs",
]

PSEUDOPARAMS = ["AWS::NoValue"] + PSEUDOPARAMS_SINGLE + PSEUDOPARAMS_MULTIPLE

LIMITS = {
    "Mappings": {"number": 200, "attributes": 200, "name": 255},  # in characters
    "Outputs": {
        "number": 200,
        "name": 255,  # in characters
        "description": 1024,  # in bytes
    },
    "Parameters": {
        "number": 200,
        "name": 255,  # in characters
        "value": 4096,  # in bytes
    },
    "Resources": {"number": 500, "name": 255},  # in characters
    "template": {"body": 1000000, "description": 1024},  # in bytes  # in bytes
    "threshold": 0.9,  # for rules about approaching the other limit values
}

valid_snapshot_types = [
    "AWS::EC2::Volume",
    "AWS::ElastiCache::CacheCluster",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::Neptune::DBCluster",
    "AWS::RDS::DBCluster",
    "AWS::RDS::DBInstance",
    "AWS::Redshift::Cluster",
]

VALID_PARAMETER_TYPES_SINGLE = [
    "AWS::EC2::AvailabilityZone::Name",
    "AWS::EC2::Image::Id",
    "AWS::EC2::Instance::Id",
    "AWS::EC2::KeyPair::KeyName",
    "AWS::EC2::SecurityGroup::GroupName",
    "AWS::EC2::SecurityGroup::Id",
    "AWS::EC2::Subnet::Id",
    "AWS::EC2::VPC::Id",
    "AWS::EC2::Volume::Id",
    "AWS::Route53::HostedZone::Id",
    "AWS::SSM::Parameter::Name",
    "Number",
    "String",
    "AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Instance::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::KeyPair::KeyName>",
    "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::GroupName>",
    "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Subnet::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>",
    "AWS::SSM::Parameter::Value<AWS::EC2::Volume::Id>",
    "AWS::SSM::Parameter::Value<AWS::Route53::HostedZone::Id>",
    "AWS::SSM::Parameter::Value<AWS::SSM::Parameter::Name>",
    "AWS::SSM::Parameter::Value<Number>",
    "AWS::SSM::Parameter::Value<String>",
]

VALID_PARAMETER_TYPES_LIST = [
    "CommaDelimitedList",
    "List<AWS::EC2::AvailabilityZone::Name>",
    "List<AWS::EC2::Image::Id>",
    "List<AWS::EC2::Instance::Id>",
    "List<AWS::EC2::SecurityGroup::GroupName>",
    "List<AWS::EC2::SecurityGroup::Id>",
    "List<AWS::EC2::Subnet::Id>",
    "List<AWS::EC2::VPC::Id>",
    "List<AWS::EC2::Volume::Id>",
    "List<AWS::Route53::HostedZone::Id>",
    "List<Number>",
    "List<String>",
    "AWS::SSM::Parameter::Value<CommaDelimitedList>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::AvailabilityZone::Name>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Image::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Instance::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::GroupName>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::VPC::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::EC2::Volume::Id>>",
    "AWS::SSM::Parameter::Value<List<AWS::Route53::HostedZone::Id>>",
    "AWS::SSM::Parameter::Value<List<Number>>",
    "AWS::SSM::Parameter::Value<List<String>>",
]

VALID_PARAMETER_TYPES = VALID_PARAMETER_TYPES_SINGLE + VALID_PARAMETER_TYPES_LIST


# pylint: disable=missing-class-docstring
class RegexDict(dict):
    def __getitem__(self, item):
        possible_items = {}
        for k, v in self.items():
            if re.fullmatch(k, item):
                possible_items[k] = v
        if not possible_items:
            raise KeyError
        longest_match = sorted(possible_items.keys(), key=len)[-1]
        return possible_items[longest_match]

    def __contains__(self, item):
        if isinstance(item, (dict, list)):
            return False
        for k, _ in self.items():
            if re.fullmatch(k, item):
                return True
        return False

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


def get_metadata_filename(url):
    """Returns the filename for a metadata file associated with a remote resource"""
    caching_dir = os.path.join(os.path.dirname(__file__), "data", "DownloadsMetadata")
    encoded_url = hashlib.sha256(url.encode()).hexdigest()
    metadata_filename = os.path.join(caching_dir, encoded_url + ".meta.json")

    return metadata_filename


def url_has_newer_version(url):
    """Checks to see if a newer version of the resource at the URL is available
    Always returns true if using Python2.7 due to lack of HEAD request support,
    or if we have no caching information for the local version of the resource
    """
    metadata_filename = get_metadata_filename(url)

    # Load in the cache
    metadata = load_metadata(metadata_filename)

    # Etag is a caching identifier used by S3 and Cloudfront
    if "etag" in metadata:
        cached_etag = metadata["etag"]
    else:
        # If we don't know the etag of the local version, we should force an update
        return True

    # Need to wrap this in a try, as URLLib2 in Python2 doesn't support HEAD requests
    try:
        # Make an initial HEAD request
        req = Request(url, method="HEAD")
        with urlopen(req) as res:
            # If we have an ETag value stored and it matches the returned one,
            # then we already have a copy of the most recent version of the
            # resource, so don't bother fetching it again
            if (
                cached_etag
                and res.info().get("ETag")
                and cached_etag == res.info().get("ETag")
            ):
                LOGGER.debug(
                    "We already have a cached version of url %s with ETag value of %s",
                    url,
                    cached_etag,
                )
                return False

    except NameError:
        # We should force an update
        return True

    # The ETag value of the remote resource does not match the local one, so a newer version is available
    return True


def get_url_content(url, caching=False):
    """Get the contents of a spec file"""

    with urlopen(url) as res:
        if caching and res.info().get("ETag"):
            metadata_filename = get_metadata_filename(url)
            # Load in all existing values
            metadata = load_metadata(metadata_filename)
            metadata["etag"] = res.info().get("ETag")
            metadata["url"] = url  # To make it obvious which url the Tag relates to
            save_metadata(metadata, metadata_filename)

        # Continue to handle the file download normally
        if res.info().get("Content-Encoding") == "gzip":
            buf = BytesIO(res.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read().decode("utf-8")
        else:
            content = res.read().decode("utf-8")

    return content


def get_url_retrieve(url: str, caching: bool = False) -> str:
    """Get the contents of a zip file and returns
    a string representing the file

    Args:
        url (str): The url to retrieve
        caching (bool): If we can cache the results (default: False)
    Returns:
        str: A string representing the file object that was retrieved
    """

    if caching:
        req = Request(url, method="HEAD")
        with urlopen(req) as res:
            if res.info().get("ETag"):
                metadata_filename = get_metadata_filename(url)
                # Load in all existing values
                metadata = load_metadata(metadata_filename)
                metadata["etag"] = res.info().get("ETag")
                metadata["url"] = url  # To make it obvious which url the Tag relates to
                save_metadata(metadata, metadata_filename)

    fileobject, _ = urlretrieve(url)

    return fileobject


def load_metadata(filename):
    """Get the contents of the download metadata file"""
    metadata = {}
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as metadata_file:
            metadata = json.load(metadata_file)
    return metadata


def save_metadata(metadata, filename):
    """Save the contents of the download metadata file"""
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    with open(filename, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file)


def load_resource(package, filename="us-east-1.json"):
    """Load CloudSpec resources
    :param filename: filename to load
    :return: Json output of the resource laoded
    """
    if sys.version_info >= (3, 9):
        return json.loads(
            pkg_resources.files(package)  # pylint: disable=no-member
            .joinpath(filename)
            .read_text(encoding="utf-8")
        )
    return json.loads(pkg_resources.read_text(package, filename, encoding="utf-8"))


REGISTRY_SCHEMAS: List[dict] = []


def is_custom_resource(resource_type):
    """Return True if resource_type is a custom resource"""
    return resource_type and (
        resource_type == "AWS::CloudFormation::CustomResource"
        or resource_type.startswith("Custom::")
    )


def bool_compare(first, second):
    """Compare strings to boolean values"""

    if isinstance(first, str):
        first = bool(first.lower() in ["true", "True"])

    if isinstance(second, str):
        second = bool(second.lower() in ["true", "True"])

    return first is second


def format_json_string(json_string):
    """Format the given JSON string"""

    def converter(o):  # pylint: disable=R1710
        """Help convert date/time into strings"""
        if isinstance(o, datetime.datetime):
            return o.__str__()  # pylint: disable=unnecessary-dunder-call

    return json.dumps(
        json_string, indent=1, sort_keys=True, separators=(",", ": "), default=converter
    )


def create_rules(mod):
    """Create and return an instance of each CloudFormationLintRule subclass
    from the given module."""
    result = []
    for _, clazz in inspect.getmembers(mod, inspect.isclass):
        if (
            clazz.__name__ == "CustomRule"
            and clazz.__module__ == "cfnlint.rules.custom"
        ):
            continue
        method_resolution = inspect.getmro(clazz)
        if [
            clz
            for clz in method_resolution[1:]
            if clz.__module__ in ("cfnlint", "cfnlint.rules")
            and clz.__name__ == "CloudFormationLintRule"
        ]:
            # create and instance of subclasses of CloudFormationLintRule
            obj = clazz()
            result.append(obj)
    return result


loader_details = (
    importlib.machinery.SourceFileLoader,  # pylint: disable=no-member
    importlib.machinery.SOURCE_SUFFIXES,  # pylint: disable=no-member
)


def import_filename(pluginname, root):
    """import_filename imports a module from a file"""
    mod_finder = importlib.machinery.FileFinder(  # pylint: disable=no-member
        root, loader_details
    )

    mod_spec = mod_finder.find_spec(pluginname)
    if mod_spec is not None:
        # for python 2.7 disabling pylint checks
        mod = importlib.util.module_from_spec(mod_spec)  # pylint: disable=no-member
        mod_spec.loader.exec_module(mod)
        return mod

    return None


def load_plugins(directory):
    """Load plugins"""
    result = []

    def onerror(os_error):
        """Raise an error"""
        raise os_error

    for root, _, filenames in os.walk(directory, onerror=onerror):
        for filename in fnmatch.filter(filenames, "[A-Za-z]*.py"):
            mod = import_filename(filename.replace(".py", ""), root)
            if mod is not None:
                result.extend(create_rules(mod))

    return result
