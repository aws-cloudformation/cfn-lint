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
import sys
import logging
import re
from copy import deepcopy
import six
import cfnlint.helpers

LOGGER = logging.getLogger(__name__)


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
            if sys.version_info >= (3, 0):
                return cls.__new__(self, x)

            if isinstance(x, six.string_types):
                return cls.__new__(self, x.encode('ascii', 'ignore'))

            return cls.__new__(self, x)

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
        start_mark = (0, 0)
        end_mark = (0, 0)

        def __init__(self, x, start_mark, end_mark):
            try:
                cls.__init__(self, x)
            except TypeError:
                cls.__init__(self)
            self.start_mark = start_mark
            self.end_mark = end_mark
            self.condition_functions = ['Fn::If']

        def __deepcopy__(self, memo):
            cls = self.__class__
            result = cls.__new__(cls, self.start_mark, self.end_mark)
            memo[id(self)] = result
            for k, v in self.items():
                result[deepcopy(k)] = deepcopy(v, memo)

            return result

        def __copy__(self):
            return self

        def get(self, key, default=None):
            """ Override get """
            if default == {}:
                cls = self.__class__
                default = cls.__new__(cls, self.start_mark, self.end_mark)

            return super(dict_node, self).get(key, default)

        # pylint: disable=W0613
        def _check_value(self, value, path, check_value=None, check_ref=None,
                         check_find_in_map=None, check_split=None, check_join=None,
                         check_import_value=None, check_sub=None, **kwargs):
            """ Helper for checking values """
            matches = []
            if len(value) == 1:
                for dict_name, _ in value.items():
                    # If this is a function we shouldn't fall back to a check_value check
                    if dict_name in cfnlint.helpers.FUNCTIONS:
                        # convert the function name from camel case to underscore
                        # Example: Fn::FindInMap becomes check_find_in_map
                        function_name = 'check_%s' % camel_to_snake(dict_name.replace('Fn::', ''))
                        if function_name == 'check_ref':
                            if check_ref:
                                matches.extend(
                                    check_ref(
                                        value=value.get('Ref'), path=path[:] + ['Ref'], **kwargs))
                        else:
                            if locals().get(function_name):
                                matches.extend(
                                    locals()[function_name](
                                        value=value.get(dict_name),
                                        path=path[:] + [dict_name],
                                        **kwargs))
                    else:
                        if check_value:
                            matches.extend(
                                check_value(
                                    value=value, path=path[:], **kwargs))
            else:
                if check_value:
                    matches.extend(
                        check_value(
                            value=value, path=path[:], **kwargs))

            return matches

        # pylint: disable=W0613
        def check_value(self, key, path,
                        check_value=None, check_ref=None,
                        check_find_in_map=None, check_split=None, check_join=None,
                        check_import_value=None, check_sub=None,
                        **kwargs):
            """
                Check a value
            """
            matches = []
            values = self.get_safe(key=key, path=path)
            if not values:
                return matches
            for i_s, p_s in values:
                if i_s is None:
                    continue
                elif isinstance(i_s, dict):
                    matches.extend(
                        self._check_value(
                            value=i_s, path=p_s[:], check_value=check_value, check_ref=check_ref,
                            check_find_in_map=check_find_in_map, check_split=check_split,
                            check_join=check_join, check_import_value=check_import_value,
                            check_sub=check_sub, **kwargs
                        )
                    )
                elif isinstance(i_s, list):
                    for a_s, a_p in i_s.items_safe(p_s):
                        if isinstance(a_s, dict):
                            matches.extend(
                                self._check_value(
                                    value=a_s, path=a_p[:], check_value=check_value, check_ref=check_ref,
                                    check_find_in_map=check_find_in_map, check_split=check_split,
                                    check_join=check_join, check_import_value=check_import_value,
                                    check_sub=check_sub, **kwargs
                                )
                            )
                        else:
                            if check_value:
                                matches.extend(
                                    check_value(
                                        value=a_s, path=a_p[:], **kwargs))
                else:
                    if check_value:
                        matches.extend(
                            check_value(
                                value=i_s, path=p_s[:], **kwargs))

            return matches

        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []
            results = []
            # Handle Fn::If in the root so we are looking for sub dict nodes
            if len(self) == 1:
                for k, _ in self.items():
                    if k == 'Fn::If':
                        for sub_v, sub_p in self.items_safe(path):
                            if isinstance(sub_v, dict):
                                results.extend(sub_v.get_safe(key, default, sub_p))

                        return results

            # Get the values of the keys and build return results
            value = self.get(key, default)
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]

            for sub_v, sub_path in value.items_safe(path[:] + [key]):
                if isinstance(sub_v, type_t) or not type_t:
                    results.append((sub_v, sub_path))

            return results

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
                            yield self, path[:]
            else:
                if isinstance(self, type_t) or not type_t:
                    yield self, path[:]

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


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
            cls = self.__class__
            result = cls.__new__(cls, self.start_mark, self.end_mark)
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

    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


def camel_to_snake(s):
    """
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    _underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
    _underscorer2 = re.compile('([a-z0-9])([A-Z])')
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


str_node = create_str_node_class(str)
dict_node = create_dict_node_class(dict)
list_node = create_dict_list_class(list)
