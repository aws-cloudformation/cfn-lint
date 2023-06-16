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
from urllib.request import Request, urlopen, urlretrieve

import regex as re

LOGGER = logging.getLogger(__name__)

AVAILABILITY_ZONES = {
    "af-south-1": ["af-south-1a", "af-south-1b", "af-south-1c"],
    "ap-east-1": ["ap-east-1a", "ap-east-1b", "ap-east-1c"],
    "ap-northeast-1": [
        "ap-northeast-1a",
        "ap-northeast-1b",
        "ap-northeast-1c",
        "ap-northeast-1d",
    ],
    "ap-northeast-2": [
        "ap-northeast-2a",
        "ap-northeast-2b",
        "ap-northeast-2c",
        "ap-northeast-2d",
    ],
    "ap-northeast-3": ["ap-northeast-3a", "ap-northeast-3b", "ap-northeast-3c"],
    "ap-south-1": ["ap-south-1a", "ap-south-1b", "ap-south-1c"],
    # "ap-south-2",  # no schemas yet
    "ap-southeast-1": ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"],
    "ap-southeast-2": ["ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"],
    "ap-southeast-3": ["ap-southeast-3a", "ap-southeast-3b", "ap-southeast-3c"],
    # "ap-southeast-4",  no schemas yet
    "ca-central-1": [
        "ca-central-1a",
        "ca-central-1b",
        "ca-central-1c",
        "ca-central-1d",
    ],
    "cn-north-1": ["cn-north-1a", "cn-north-1b", "cn-north-1c"],
    "cn-northwest-1": ["cn-northwest-1a", "cn-northwest-1b", "cn-northwest-1c"],
    "eu-central-1": ["eu-central-1a", "eu-central-1b", "eu-central-1c"],
    # "eu-central-2",  no schemas yet
    "eu-north-1": ["eu-north-1a", "eu-north-1b", "eu-north-1c"],
    "eu-south-1": ["eu-south-1a", "eu-south-1b", "eu-south-1c"],
    # "eu-south-2",  no schemas yet
    "eu-west-1": ["eu-west-1a", "eu-west-1b", "eu-west-1c"],
    "eu-west-2": ["eu-west-2a", "eu-west-2b", "eu-west-2c"],
    "eu-west-3": ["eu-west-3a", "eu-west-3b", "eu-west-3c"],
    "me-south-1": ["me-south-1a", "me-south-1b", "me-south-1c"],
    # "me-central-1",  no schemas yet
    "sa-east-1": ["sa-east-1a", "sa-east-1b", "sa-east-1c"],
    "us-east-1": [
        "us-east-1a",
        "us-east-1b",
        "us-east-1c",
        "us-east-1d",
        "us-east-1e",
        "us-east-1f",
    ],
    "us-east-2": ["us-east-2a", "us-east-2b", "us-east-2c"],
    "us-gov-east-1": ["us-gov-east-1a", "us-gov-east-1b", "us-gov-east-1c"],
    "us-gov-west-1": ["us-gov-west-1a", "us-gov-west-1b", "us-gov-west-1c"],
    "us-west-1": ["us-west-1a", "us-west-1c"],
    "us-west-2": ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"],
}

REGIONS = list(AVAILABILITY_ZONES.keys())
REGION_PRIMARY = "us-east-1"
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
REGEX_DYN_REF_SSM = re.compile(r"^.*{{resolve:ssm:[a-zA-Z0-9_\.\-/]+:\d+}}.*$")
REGEX_DYN_REF_SSM_SECURE = re.compile(
    r"^.*{{resolve:ssm-secure:[a-zA-Z0-9_\.\-/]+:\d+}}.*$"
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

FUNCTIONS_LIST = frozenset(
    [
        "Fn::GetAZs",
        "Fn::Split",
        "Fn::Cidr",
        "Fn::GetAtt",
        "Fn::FindInMap",
        "Fn::Select",
        "Ref",
    ]
)
FUNCTIONS_OBJECT = frozenset(["Fn::Select", "Fn::GetAtt"])
# FindInMap can be singular or multiple.  This needs to be accounted for individually
# GetAtt can refere to a list, object, or a singular value
FUNCTIONS_SINGLE = frozenset(
    set(FUNCTIONS)
    - (set(FUNCTIONS_LIST) - set(["Fn::FindInMap", "Fn::GetAtt", "Fn::Select", "Ref"]))
)

FUNCTION_IF = "Fn::If"
FUNCTION_AND = "Fn::And"
FUNCTION_OR = "Fn::Or"
FUNCTION_NOT = "Fn::Not"
FUNCTION_EQUALS = "Fn::Equals"

FUNCTION_CONDITIONS = [FUNCTION_AND, FUNCTION_OR, FUNCTION_NOT, FUNCTION_EQUALS]

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

    # The ETag value of the remote resource does not
    # match the local one, so a newer version is available
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
        metadata_file.write("\n")


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


def create_rules(
    mod, name="CloudFormationLintRule", modules=("cfnlint", "cfnlint.rules")
):
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
            if clz.__module__ in modules and clz.__name__ == name
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


def load_plugins(
    directory, name="CloudFormationLintRule", modules=("cfnlint", "cfnlint.rules")
):
    """Load plugins"""
    result = []

    def onerror(os_error):
        """Raise an error"""
        raise os_error

    for root, _, filenames in os.walk(directory, onerror=onerror):
        for filename in fnmatch.filter(filenames, "[A-Za-z]*.py"):
            mod = import_filename(filename.replace(".py", ""), root)
            if mod is not None:
                result.extend(create_rules(mod, name, modules))

    return result


class ToPy:
    """
    Conversion of a string into Python friendly naming
    """

    def __init__(self, name: str):
        self.name = name
        self.py = name.replace("::", "_").replace("-", "_").lower()
        self.py_class = name.replace("::", "")
        # provider zips has filenames with -
        self.provider = name.replace("::", "-").lower()
