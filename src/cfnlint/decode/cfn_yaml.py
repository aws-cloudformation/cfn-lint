"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fileinput
import logging
import sys
from yaml.composer import Composer
from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.resolver import Resolver
from yaml import ScalarNode
from yaml import SequenceNode
from yaml import MappingNode
from yaml.constructor import SafeConstructor
from yaml.constructor import ConstructorError
import cfnlint
from cfnlint.decode.node import str_node, dict_node, list_node, sub_node

try:
    from yaml._yaml import CParser as Parser  # pylint: disable=ungrouped-imports,
    cyaml = True
except ImportError:
    from yaml.parser import Parser  # type: ignore # pylint: disable=ungrouped-imports
    cyaml = False

UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'

LOGGER = logging.getLogger(__name__)


class CfnParseError(ConstructorError):
    """
    Error thrown when the template contains Cfn Error
    """

    def __init__(self, filename, errors):

        if isinstance(errors, cfnlint.rules.Match):
            errors = [errors]

        # Call the base class constructor with the parameters it needs
        super(CfnParseError, self).__init__(errors[0].message)

        # Now for your custom code...
        self.filename = filename
        self.matches = errors


def build_match(filename, message, line_number, column_number, key):
    return cfnlint.rules.Match(
        line_number + 1, column_number + 1, line_number + 1,
        column_number + 1 + len(key), filename, cfnlint.rules.ParseError(), message=message)


class NodeConstructor(SafeConstructor):
    """
    Node Constructors for loading different types in Yaml
    """

    def __init__(self, filename):
        # Call the base class constructor
        super(NodeConstructor, self).__init__()

        self.filename = filename

    # To support lazy loading, the original constructors first yield
    # an empty object, then fill them in when iterated. Due to
    # laziness we omit this behaviour (and will only do "deep
    # construction") by first exhausting iterators, then yielding
    # copies.
    def construct_yaml_map(self, node):

        # Check for duplicate keys on the current level, this is not desirable
        # because a dict does not support this. It overwrites it with the last
        # occurance, which can give unexpected results
        mapping = {}
        self.flatten_mapping(node)
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, False)
            value = self.construct_object(value_node, False)

            for key_dup in mapping:
                if key_dup == key:
                    raise CfnParseError(
                        self.filename,
                        [
                            build_match(
                                filename=self.filename,
                                message='Duplicate resource found "{}" (line {})'.format(
                                    key, key_dup.start_mark.line + 1),
                                line_number=key_dup.start_mark.line,
                                column_number=key_dup.start_mark.column,
                                key=key
                            ),
                            build_match(
                                filename=self.filename,
                                message='Duplicate resource found "{}" (line {})'.format(
                                    key, key_node.start_mark.line + 1),
                                line_number=key_node.start_mark.line,
                                column_number=key_node.start_mark.column,
                                key=key
                            ),
                        ]
                    )
            try:
                mapping[key] = value
            except:
                raise CfnParseError(
                    self.filename,
                    [
                        build_match(
                            filename=self.filename,
                            message=f'Unhashable type "{key}" (line {key.start_mark.line + 1})',
                            line_number=key.start_mark.line,
                            column_number=key.start_mark.column,
                            key=key
                        ),
                    ]
                )

        obj, = SafeConstructor.construct_yaml_map(self, node)

        if len(mapping) == 1:
            if 'Fn::Sub' in mapping:
                return sub_node(obj, node.start_mark, node.end_mark)

        return dict_node(obj, node.start_mark, node.end_mark)

    def construct_yaml_str(self, node):
        obj = SafeConstructor.construct_yaml_str(self, node)
        assert isinstance(obj, (str))
        return str_node(obj, node.start_mark, node.end_mark)

    def construct_yaml_seq(self, node):
        obj, = SafeConstructor.construct_yaml_seq(self, node)
        assert isinstance(obj, list)
        return list_node(obj, node.start_mark, node.end_mark)


NodeConstructor.add_constructor( # type: ignore
    'tag:yaml.org,2002:map',
    NodeConstructor.construct_yaml_map)

NodeConstructor.add_constructor( # type: ignore
    'tag:yaml.org,2002:str',
    NodeConstructor.construct_yaml_str)

NodeConstructor.add_constructor( # type: ignore
    'tag:yaml.org,2002:seq',
    NodeConstructor.construct_yaml_seq)


class MarkedLoader(Reader, Scanner, Parser, Composer, NodeConstructor, Resolver):
    """
    Class for marked loading YAML
    """
    # pylint: disable=non-parent-init-called,super-init-not-called

    def __init__(self, stream, filename):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        if cyaml:
            Parser.__init__(self, stream)
        else:
            Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)
        NodeConstructor.__init__(self, filename)


def multi_constructor(loader, tag_suffix, node):
    """
    Deal with !Ref style function format
    """

    if tag_suffix not in UNCONVERTED_SUFFIXES:
        tag_suffix = '{}{}'.format(FN_PREFIX, tag_suffix)

    constructor = None
    if tag_suffix == 'Fn::GetAtt':
        constructor = construct_getatt
    elif isinstance(node, ScalarNode):
        constructor = loader.construct_scalar
    elif isinstance(node, SequenceNode):
        constructor = loader.construct_sequence
    elif isinstance(node, MappingNode):
        constructor = loader.construct_mapping
    else:
        raise 'Bad tag: !{}'.format(tag_suffix)

    if tag_suffix == 'Fn::Sub':
        return sub_node({tag_suffix: constructor(node)}, node.start_mark, node.end_mark)

    return dict_node({tag_suffix: constructor(node)}, node.start_mark, node.end_mark)


def construct_getatt(node):
    """
    Reconstruct !GetAtt into a list
    """

    if isinstance(node.value, (str)):
        return list_node(node.value.split('.', 1), node.start_mark, node.end_mark)
    if isinstance(node.value, list):
        return list_node([s.value for s in node.value], node.start_mark, node.end_mark)

    raise ValueError('Unexpected node type: {}'.format(type(node.value)))


def loads(yaml_string, fname=None):
    """
    Load the given YAML string
    """
    loader = MarkedLoader(yaml_string, fname)
    loader.add_multi_constructor('!', multi_constructor)
    template = loader.get_single_data()
    # Convert an empty file to an empty dict
    if template is None:
        template = {}

    return template


def load(filename):
    """
    Load the given YAML file
    """

    content = ''

    if not sys.stdin.isatty():
        for line in fileinput.input(files=filename):
            content = content + line
    else:
        with open(filename, encoding='utf-8') as fp:
            content = fp.read()

    return loads(content, filename)
