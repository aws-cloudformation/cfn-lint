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
import logging
import json
from json.decoder import WHITESPACE, WHITESPACE_STR, BACKSLASH, STRINGCHUNK
from json.scanner import NUMBER_RE
from cfnlint.parser import DuplicateError, NullError


LOGGER = logging.getLogger(__name__)


def check_duplicates(ordered_pairs):
    """
        Check for duplicate keys on the current level, this is not desirable
        because a dict does not support this. It overwrites it with the last
        occurance, which can give unexpected results
    """
    mapping = {}
    for key, value in ordered_pairs:
        if value is None:
            raise NullError('"{}"'.format(key))
        if key in mapping:
            raise DuplicateError('"{}"'.format(key))
        else:
            mapping[key] = value
    return mapping


class JSONDecodeError(ValueError):
    """Subclass of ValueError with the following additional properties:
    msg: The unformatted error message
    doc: The JSON document being parsed
    pos: The start index of doc where parsing failed
    lineno: The line corresponding to pos
    colno: The column corresponding to pos
    """
    # Note that this exception is used from _json
    def __init__(self, msg, doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)


class Mark(object):
    """Mark of line and column"""
    line = 1
    column = 1

    def __init__(self, line, column):
        self.line = line
        self.column = column


def create_node_class(cls):
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

        # pylint: disable=bad-classmethod-argument, unused-argument
        def __new__(self, x, start_mark, end_mark):
            return cls.__new__(self, x)
    node_class.__name__ = '%s_node' % cls.__name__
    return node_class


str_node = create_node_class(str)


# pylint: disable=W0102
# Exception based on builtin Python Function
def py_scanstring(s, end, strict=True,
                  _b=BACKSLASH, _m=STRINGCHUNK.match):
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.
    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    chunks = []
    _append = chunks.append
    begin = end - 1
    while 1:
        chunk = _m(s, end)
        if chunk is None:
            raise JSONDecodeError('Unterminated string starting at', s, begin)
        end = chunk.end()
        content, terminator = chunk.groups()
        # Content is contains zero or more unescaped string characters
        if content:
            _append(content)
        # Terminator is the end of string, a literal control character,
        # or a backslash denoting that an escape sequence follows
        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = 'Invalid control character {0!r} at'.format(terminator)
                raise JSONDecodeError(msg, s, end)
            else:
                _append(terminator)
                continue
        try:
            esc = s[end]
        except IndexError:
            raise JSONDecodeError('Unterminated string starting at', s, begin)
        # If not a unicode escape sequence, must be in the lookup table
        if esc != 'u':
            try:
                char = _b[esc]
            except KeyError:
                msg = 'Invalid \\escape: {0!r}'.format(esc)
                raise JSONDecodeError(msg, s, end)
            end += 1
        else:
            uni = _decode_uXXXX(s, end)
            end += 5
            if 0xd800 <= uni <= 0xdbff and s[end:end + 2] == '\\u':
                uni2 = _decode_uXXXX(s, end + 1)
                if 0xdc00 <= uni2 <= 0xdfff:
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    end += 6
            char = chr(uni)
        _append(char)
    return ''.join(chunks), end


def _decode_uXXXX(s, pos):
    esc = s[pos + 1:pos + 5]
    if len(esc) == 4 and esc[1] not in 'xX':
        try:
            return int(esc, 16)
        except ValueError:
            pass
    msg = 'Invalid \\uXXXX escape'
    raise JSONDecodeError(msg, s, pos)


def CfnJSONObject(s_and_end, strict, scan_once, object_hook, object_pairs_hook,
                  memo=None, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    """ Custom Cfn JSON Object to store keys with start and end times """
    s, end = s_and_end
    pairs = []
    pairs_append = pairs.append
    # Backwards compatibility
    if memo is None:
        memo = {}
    memo_get = memo.setdefault
    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end:end + 1]
    # Normally we expect nextchar == '"'
    if nextchar != '"':
        if nextchar in _ws:
            end = _w(s, end).end()
            nextchar = s[end:end + 1]
        # Trivial empty object
        if nextchar == '}':
            if object_pairs_hook is not None:
                try:
                    result = object_pairs_hook(pairs)
                    return result, end + 1
                except DuplicateError as err:
                    raise JSONDecodeError('Duplicate found {}'.format(err), s, end)
                except NullError as err:
                    raise JSONDecodeError('Null Error {}'.format(err), s, end)
            pairs = {}
            if object_hook is not None:
                pairs = object_hook(pairs, s)
            return pairs, end + 1
        elif nextchar != '"':
            raise JSONDecodeError('Expecting property name enclosed in double quotes', s, end)
    end += 1
    while True:
        begin = end - 1
        key, end = py_scanstring(s, end, strict)
        # print(lineno, colno, obj)
        # print(key, lineno, colno)
        key = memo_get(key, key)
        # To skip some function call overhead we optimize the fast paths where
        # the JSON key separator is ": " or just ":".
        if s[end:end + 1] != ':':
            end = _w(s, end).end()
            if s[end:end + 1] != ':':
                raise JSONDecodeError('Expecting \':\' delimiter', s, end)
        end += 1

        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass

        beg_lineno = s.count('\n', 0, begin)
        beg_colno = begin - s.rfind('\n', 0, begin)
        beg_mark = Mark(beg_lineno, beg_colno)
        end_key_pos = begin + len(key)
        end_lineno = s.count('\n', 0, end_key_pos)
        end_colno = end_key_pos - s.rfind('\n', 0, end_key_pos)
        end_mark = Mark(end_lineno, end_colno)
        try:
            value, end = scan_once(s, end)
        except StopIteration as err:
            raise JSONDecodeError('Expecting value', s, str(err))
        key_str = str_node(key, beg_mark, end_mark)
        pairs_append((key_str, value))
        try:
            nextchar = s[end]
            if nextchar in _ws:
                end = _w(s, end + 1).end()
                nextchar = s[end]
        except IndexError:
            nextchar = ''
        end += 1

        if nextchar == '}':
            break
        elif nextchar != ',':
            raise JSONDecodeError('Expecting \',\' delimiter', s, end - 1)
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar != '"':
            raise JSONDecodeError(
                'Expecting property name enclosed in double quotes', s, end - 1)
    if object_pairs_hook is not None:
        try:
            result = object_pairs_hook(pairs)
        except DuplicateError as err:
            raise JSONDecodeError('Duplicate found {}'.format(err), s, end)
        except NullError as err:
            raise JSONDecodeError('Null Error {}'.format(err), s, end)
        return result, end
    pairs = dict(pairs)
    if object_hook is not None:
        pairs = object_hook(pairs, s, begin)
    return pairs, end


def py_make_scanner(context):
    """
        Make python based scanner
        For this use case we will not use the C based scanner
    """
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    # pylint: disable=R0911
    # Based on Python standard function
    def _scan_once(string, idx):
        """ Scan once internal function """
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx)

        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        elif nextchar == '{':
            return parse_object(
                (string, idx + 1), strict,
                scan_once, object_hook, object_pairs_hook, memo)
        elif nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == 'n' and string[idx:idx + 4] == 'null':
            return None, idx + 4
        elif nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        elif nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5

        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return res, m.end()
        elif nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            return parse_constant('NaN'), idx + 3
        elif nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            return parse_constant('Infinity'), idx + 8
        elif nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            return parse_constant('-Infinity'), idx + 9
        else:
            raise StopIteration(idx)

    def scan_once(string, idx):
        """ Scan Once"""
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return _scan_once


class CfnJSONDecoder(json.JSONDecoder):
    """
    Converts a json string, where datetime and timedelta objects were converted
    into strings using the DateTimeAwareJSONEncoder, into a python object.
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, *args, **kwargs)
        self.parse_object = CfnJSONObject
        self.parse_string = py_scanstring
        self.memo = {}
        self.object_pairs_hook = check_duplicates
        self.scan_once = py_make_scanner(self)
