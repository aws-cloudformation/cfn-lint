"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import logging
from copy import deepcopy

LOGGER = logging.getLogger(__name__)


class TemplateAttributeError(AttributeError):
    """ Custom error to capture Attribute Errors in the Template """


def create_str_node_class(cls):
    """
    Create string node class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark

        # pylint: disable=bad-classmethod-argument, unused-argument
        def __new__(self, x, start_mark, end_mark):
            return cls.__new__(self, x)

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

        def __deepcopy__(self, memo):
            result = str_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            return result

        def __copy__(self):
            return self

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


def create_dict_node_class(cls):
    """
    Create dynamic node class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark
            self.condition_functions = ['Fn::If']

        def __deepcopy__(self, memo):
            result = dict_node(self, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for k, v in self.items():
                result[deepcopy(k)] = deepcopy(v, memo)

            return result

        def __copy__(self):
            return self

        def is_function_returning_object(self, mappings=None):
            """
                Check if an object is using a function that could return an object
                Return True when
                    Fn::Select:
                    - 0  # or any number
                    - !FindInMap [mapname, key, value] # or any mapname, key, value
                Otherwise False
            """
            mappings = mappings or {}
            if len(self) == 1:
                for k, v in self.items():
                    if k in ['Fn::Select']:
                        if isinstance(v, list):
                            if len(v) == 2:
                                p_v = v[1]
                                if isinstance(p_v, dict):
                                    if len(p_v) == 1:
                                        for l_k in p_v.keys():
                                            if l_k == 'Fn::FindInMap':
                                                return True

            return False

        def get(self, key, default=None):
            """ Override the default get """
            if isinstance(default, dict):
                default = dict_node(default, self.start_mark, self.end_mark)
            return super(node_class, self).get(key, default)

        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []

            if default == {}:
                default = dict_node({}, self.start_mark, self.end_mark)
            value = self.get(key, default)
            if value is None and default is None:
                # if default is None and value is None return empty list
                return []

            # if the value is the default make sure that the default value is of type_t when specified
            if bool(type_t) and value == default and not isinstance(default, type_t):
                raise ValueError('"default" type should be of "type_t"')

            # when not a dict see if if the value is of the right type
            results = []
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]
            else:
                for sub_v, sub_path in value.items_safe(path + [key]):
                    if isinstance(sub_v, type_t) or not type_t:
                        results.append((sub_v, sub_path))

            return results

        def clean(self):
            """Clean object to remove any Ref AWS::NoValue"""
            result = dict_node({}, self.start_mark, self.end_mark)
            for k, v in self.items():
                if isinstance(v, dict) and len(v) == 1:
                    if v.get('Ref') == 'AWS::NoValue':
                        continue
                result[k] = v
            return result


        def items_safe(self, path=None, type_t=()):
            """Get items while handling IFs"""
            path = path or []
            if len(self) == 1:
                for k, v in self.items():
                    if k == 'Fn::If':
                        if isinstance(v, list):
                            if len(v) == 3:
                                for i, if_v in enumerate(v[1:]):
                                    if isinstance(if_v, dict):
                                        # yield from if_v.items_safe(path[:] + [k, i - 1])
                                        # Python 2.7 support
                                        for items, p in if_v.items_safe(path[:] + [k, i + 1]):
                                            if isinstance(items, type_t) or not type_t:
                                                yield items, p
                                    elif isinstance(if_v, list):
                                        if isinstance(if_v, type_t) or not type_t:
                                            yield if_v, path[:] + [k, i + 1]
                                    else:
                                        if isinstance(if_v, type_t) or not type_t:
                                            yield if_v, path[:] + [k, i + 1]
                    elif not (k == 'Ref' and v == 'AWS::NoValue'):
                        if isinstance(self, type_t) or not type_t:
                            yield self.clean(), path[:]
            else:
                if isinstance(self, type_t) or not type_t:
                    yield self.clean(), path[:]

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


def create_intrinsic_node_class(cls):
    """
    Create dynamic sub class
    """
    class intrinsic_class(cls):
        """Node class created based on the input class"""
        def is_valid(self):
            raise TemplateAttributeError('intrisnic class shouldn\'t be directly used')

    intrinsic_class.__name__ = '%s_intrinsic' % cls.__name__
    return intrinsic_class


def create_sub_node_class(cls):
    """
    Create dynamic sub class
    """
    class sub_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            cls.__init__(self, x, start_mark, end_mark)
            self.__cache_is_valid = False
            self.__cache_sub_string = ''
            self.__cache_sub_string_vars = set()
            self.__cache_sub_vars = {}
            self.__setup()

        def __setup_list_sub_string(self, s):
            self.__cache_sub_string = s
            regex = re.compile(r'\${[^!].*?}')
            string_params = regex.findall(s)

            for string_param in string_params:
                self.__cache_sub_string_vars.add(string_param[2:-1].strip())

        def __setup_list(self, v):
            if len(v) == 2:
                if not isinstance(v[0], str):
                    return
                self.__setup_list_sub_string(v[0])
                if not isinstance(v[1], dict):
                    return
                self.__cache_sub_vars = v[1]
                self.__cache_is_valid = True

        def __setup(self):
            if len(self) == 1:
                for k, v in self.items():
                    if k == 'Fn::Sub':
                        if isinstance(v, str):
                            self.__setup_list_sub_string(v)
                            self.__cache_is_valid = True
                        elif isinstance(v, list):
                            self.__setup_list(v)

        def get_defined_vars(self):
            # Returns that are in the second part of a list Fn::Sub
            # This function will not return implied variables from a String Ref and GetAtt
            if self.is_valid():
                return self.__cache_sub_vars

            return {}

        def get_string_vars(self):
            # Returns all variables in the Sub String
            if self.is_valid():
                return self.__cache_sub_string_vars

            return set()

        def get_string(self):
            # Returns the sub string as it was when it was decoded
            if self.is_valid():
                return self.__cache_sub_string

            return ''

        def is_valid(self):
            return self.__cache_is_valid


    sub_class.__name__ = '%s_sub' % cls.__name__
    return sub_class

def create_dict_list_class(cls):
    """
    Create dynamic list class
    """
    class node_class(cls):
        """Node class created based on the input class"""

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark
            self.condition_functions = ['Fn::If']

        def __deepcopy__(self, memo):
            result = list_node([], self.start_mark, self.end_mark)
            memo[id(self)] = result
            for _, v in enumerate(self):
                result.append(deepcopy(v, memo))

            return result

        def __copy__(self):
            return self

        def items_safe(self, path=None, type_t=()):
            """Get items while handling IFs"""
            path = path or []
            for i, v in enumerate(self):
                if isinstance(v, dict):
                    for items, p in v.items_safe(path[:] + [i]):
                        if isinstance(items, type_t) or not type_t:
                            yield items, p
                else:
                    if isinstance(v, type_t) or not type_t:
                        yield v, path[:] + [i]

        def __getattr__(self, name):
            raise TemplateAttributeError('%s.%s is invalid' % (self.__class__.__name__, name))

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


str_node = create_str_node_class(str)
dict_node = create_dict_node_class(dict)
list_node = create_dict_list_class(list)
intrinsic_node = create_intrinsic_node_class(dict_node)
sub_node = create_sub_node_class(intrinsic_node)
