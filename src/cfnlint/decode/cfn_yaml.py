"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

# Code is taken from jsonschema package and adapted CloudFormation use
# https://github.com/yaml/pyyaml/blob/a2d19c0234866dc9d4d55abf3009699c258bb72f/lib/yaml/scanner.py#L46
"""

from __future__ import annotations

import fileinput
import logging
import sys

from yaml import MappingNode, SafeLoader, ScalarNode, SequenceNode

try:
    from yaml import CSafeLoader

    FastLoader = CSafeLoader  # type: ignore
except ImportError:
    FastLoader = SafeLoader  # type: ignore

from yaml.constructor import ConstructorError, SafeConstructor
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from cfnlint.decode.mark import Mark
from cfnlint.decode.node import dict_node, list_node, str_node
from cfnlint.rules import Match
from cfnlint.rules.errors import ParseError

UNCONVERTED_SUFFIXES = ["Ref", "Condition"]
FN_PREFIX = "Fn::"

LOGGER = logging.getLogger(__name__)


class CfnParseError(ConstructorError):
    """
    Error thrown when the template contains Cfn Error
    """

    def __init__(self, filename, errors):
        if isinstance(errors, Match):
            errors = [errors]

        # Call the base class constructor with the parameters it needs
        super().__init__(errors[0].message)

        # Now for your custom code...
        self.filename = filename
        self.matches = errors


def build_match(filename, message, line_number, column_number, key):
    return Match.create(
        message=message,
        filename=filename,
        rule=ParseError(),
        linenumber=line_number + 1,
        columnnumber=column_number + 1,
        linenumberend=line_number + 1,
        columnnumberend=column_number + 1 + len(key),
    )


class NodeConstructor(SafeConstructor):
    """
    Node Constructors for loading different types in Yaml
    """

    def __init__(self, filename):
        # Call the base class constructor
        super().__init__()
        self.filename = filename

    def flatten_mapping(self, node):
        # Rewrote to handle merging and overwriting keys
        if any(key_node.tag == "tag:yaml.org,2002:merge" for key_node, _ in node.value):
            super().flatten_mapping(node)
            setattr(node, "using_merge", True)
        super().flatten_mapping(node)

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
        matches = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, False)
            value = self.construct_object(value_node, False)

            if key is None:
                raise CfnParseError(
                    self.filename,
                    [
                        build_match(
                            filename=self.filename,
                            message=(
                                f"Null key {key_node.value!r} not supported "
                                f"(line {key_node.start_mark.line + 1})"
                            ),
                            line_number=key_node.start_mark.line,
                            column_number=key_node.start_mark.column,
                            key=key_node.value,
                        ),
                    ],
                )
            if not getattr(node, "using_merge", False):
                for key_dup in mapping:
                    if key_dup == key:
                        if matches:
                            matches.append(
                                build_match(
                                    filename=self.filename,
                                    message=(
                                        f"Duplicate found {key!r} (line"
                                        f" {key_node.start_mark.line + 1})"
                                    ),
                                    line_number=key_node.start_mark.line,
                                    column_number=key_node.start_mark.column,
                                    key=key,
                                )
                            )
                        else:
                            matches.extend(
                                [
                                    build_match(
                                        filename=self.filename,
                                        message=(
                                            f"Duplicate found {key!r} (line"
                                            f" {key_dup.start_mark.line + 1})"
                                        ),
                                        line_number=key_dup.start_mark.line,
                                        column_number=key_dup.start_mark.column,
                                        key=key,
                                    ),
                                    build_match(
                                        filename=self.filename,
                                        message=(
                                            f"Duplicate found {key!r} (line"
                                            f" {key_node.start_mark.line + 1})"
                                        ),
                                        line_number=key_node.start_mark.line,
                                        column_number=key_node.start_mark.column,
                                        key=key,
                                    ),
                                ],
                            )
            try:
                mapping[key] = value
            except Exception as exc:
                raise CfnParseError(
                    self.filename,
                    [
                        build_match(
                            filename=self.filename,
                            message=(
                                f'Unhashable type "{key}" (line'
                                f" {key.start_mark.line + 1})"
                            ),
                            line_number=key.start_mark.line,
                            column_number=key.start_mark.column,
                            key=key,
                        ),
                    ],
                ) from exc

        if matches:
            raise CfnParseError(
                self.filename,
                matches,
            )

        (obj,) = SafeConstructor.construct_yaml_map(self, node)

        using_merge = False if not hasattr(node, "using_merge") else node.using_merge
        return dict_node(obj, node.start_mark, node.end_mark, using_merge)

    def construct_yaml_str(self, node):
        obj = SafeConstructor.construct_yaml_str(self, node)
        assert isinstance(obj, (str))
        return str_node(obj, node.start_mark, node.end_mark)

    def construct_yaml_seq(self, node):
        (obj,) = SafeConstructor.construct_yaml_seq(self, node)
        assert isinstance(obj, list)
        return list_node(obj, node.start_mark, node.end_mark)

    def construct_getatt(self, node):
        """
        Reconstruct !GetAtt into a list
        """
        if isinstance(node.value, (str)):
            return list_node(node.value.split(".", 1), node.start_mark, node.end_mark)
        if isinstance(node.value, list):
            if any(isinstance(value, tuple) for value in node.value):
                return dict_node(
                    self.construct_object(
                        MappingNode(
                            tag="tag:yaml.org,2002:map",
                            value=node.value,
                            start_mark=node.start_mark,
                            end_mark=node.end_mark,
                        ),
                        deep=True,
                    )
                )
            else:
                return list_node(
                    [self.construct_object(child, deep=True) for child in node.value],
                    node.start_mark,
                    node.end_mark,
                )
        raise ValueError(f"Unexpected GetAtt format: {type(node.value)}")


NodeConstructor.add_constructor(  # type: ignore
    "tag:yaml.org,2002:map", NodeConstructor.construct_yaml_map
)

NodeConstructor.add_constructor(  # type: ignore
    "tag:yaml.org,2002:str", NodeConstructor.construct_yaml_str
)

NodeConstructor.add_constructor(  # type: ignore
    "tag:yaml.org,2002:seq", NodeConstructor.construct_yaml_seq
)


class CfnFullLoader(FastLoader, NodeConstructor):
    """
    Custom FullLoader that integrates NodeConstructor functionality
    """

    def __init__(self, stream, filename):
        FastLoader.__init__(self, stream)
        NodeConstructor.__init__(self, filename)


# Register NodeConstructor methods with CfnFullLoader
CfnFullLoader.add_constructor(  # type: ignore[type-var]
    "tag:yaml.org,2002:map", NodeConstructor.construct_yaml_map
)
CfnFullLoader.add_constructor(  # type: ignore[type-var]
    "tag:yaml.org,2002:str", NodeConstructor.construct_yaml_str
)
CfnFullLoader.add_constructor(  # type: ignore[type-var]
    "tag:yaml.org,2002:seq", NodeConstructor.construct_yaml_seq
)


def multi_constructor(loader: CfnFullLoader, tag_suffix, node):
    """
    Deal with !Ref style function format
    """

    if tag_suffix not in UNCONVERTED_SUFFIXES:
        tag_suffix = f"{FN_PREFIX}{tag_suffix}"

    if tag_suffix == "Fn::GetAtt":
        return dict_node(
            {tag_suffix: loader.construct_getatt(node)}, node.start_mark, node.end_mark
        )
    elif isinstance(node, ScalarNode):
        return dict_node(
            {tag_suffix: loader.construct_scalar(node)}, node.start_mark, node.end_mark
        )
    elif isinstance(node, SequenceNode):
        return dict_node(
            {tag_suffix: loader.construct_sequence(node, True)},
            node.start_mark,
            node.end_mark,
        )
    elif isinstance(node, MappingNode):
        return dict_node(
            {tag_suffix: loader.construct_mapping(node, True)},
            node.start_mark,
            node.end_mark,
        )

    raise Exception(f"Bad tag: !{tag_suffix}")


def loads(yaml_string, fname=None):
    """
    Load the given YAML string
    """
    try:
        loader = CfnFullLoader(yaml_string, fname)
        loader.add_multi_constructor("!", multi_constructor)

        template = loader.get_single_data()
        # Convert an empty file to an empty dict
        if template is None:
            template = dict_node({}, Mark(0, 0), Mark(0, 0))
        return template
    except CfnParseError:
        raise
    except (ScannerError, ParserError):
        # Let YAML parsing errors bubble up so decode.py can handle JSON fallback
        raise
    except Exception as exc:
        raise CfnParseError(
            fname,
            [
                build_match(
                    filename=fname,
                    message=f"Template could not be parsed: {str(exc)}",
                    line_number=0,
                    column_number=0,
                    key="",
                )
            ],
        ) from exc


def load(filename):
    """
    Load the given YAML file
    """

    content = ""

    if (filename is None) and (not sys.stdin.isatty()):
        filename = "-"  # no filename provided, it's stdin
        fileinput_args = {"files": filename}
        if sys.version_info.major <= 3 and sys.version_info.minor >= 10:
            fileinput_args["encoding"] = "utf-8"
        with fileinput.input(**fileinput_args) as f:
            for line in f:
                content = content + line
    else:
        with open(filename, encoding="utf-8") as fp:
            content = fp.read()

    return loads(content, filename)
