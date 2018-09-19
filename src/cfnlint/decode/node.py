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
from copy import deepcopy
import six


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

        def get_safe(self, key, default=None, path=None, type_t=()):
            """
                Get values in format
            """
            path = path or []
            value = self.get(key, default)
            if not isinstance(value, (dict)):
                if isinstance(value, type_t) or not type_t:
                    return [(value, (path[:] + [key]))]

            results = []
            for sub_v, sub_path in value.items_safe(path):
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
                    elif k != 'Ref' and v != 'AWS::NoValue':
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


str_node = create_str_node_class(str)
dict_node = create_dict_node_class(dict)
list_node = create_dict_list_class(list)
