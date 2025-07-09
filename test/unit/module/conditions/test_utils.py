"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import hashlib
import json
import unittest

from cfnlint.conditions._utils import (
    ObjectEncoder,
    _cached_hash,
    _make_hashable,
    get_hash,
)


class AnObject:
    """Test object with _value attribute"""

    def __init__(self, value):
        self._value = value


class BadStringObject:
    """Test object that raises exception when stringified"""

    def __str__(self):
        raise ValueError("Cannot stringify")


class TestUtils(unittest.TestCase):
    """Test Utils"""

    def test_object_encoder(self):
        """Test ObjectEncoder class"""
        # Test with a regular object
        test_obj = AnObject("test_value")
        encoded = json.dumps(test_obj, cls=ObjectEncoder)
        self.assertEqual(encoded, '"test_value"')

        # Test with a nested object
        nested_obj = AnObject(AnObject("nested_value"))
        encoded = json.dumps(nested_obj, cls=ObjectEncoder)
        self.assertEqual(encoded, '"nested_value"')

        # Test with a regular value
        regular_value = {"key": "value"}
        encoded = json.dumps(regular_value, cls=ObjectEncoder)
        self.assertEqual(encoded, '{"key": "value"}')

        # Test the default method directly
        encoder = ObjectEncoder()
        obj = object()
        # The default method should return the object itself
        self.assertEqual(encoder.default(obj), obj)

    def test_make_hashable_simple_types(self):
        """Test _make_hashable with simple types"""
        # Test with simple hashable types
        self.assertEqual(_make_hashable("string"), "string")
        self.assertEqual(_make_hashable(123), 123)
        self.assertEqual(_make_hashable(123.45), 123.45)
        self.assertEqual(_make_hashable(True), True)
        self.assertEqual(_make_hashable(None), None)

    def test_make_hashable_dict(self):
        """Test _make_hashable with dictionaries"""
        # Test with dictionary
        test_dict = {"b": 2, "a": 1}
        hashable_dict = _make_hashable(test_dict)
        # Should be a tuple of tuples with sorted keys
        self.assertEqual(hashable_dict, (("a", 1), ("b", 2)))

        # Test with nested dictionary
        nested_dict = {"outer": {"inner": "value"}}
        hashable_nested = _make_hashable(nested_dict)
        self.assertEqual(hashable_nested, (("outer", (("inner", "value"),)),))

    def test_make_hashable_list(self):
        """Test _make_hashable with lists"""
        # Test with list
        test_list = [1, 2, 3]
        hashable_list = _make_hashable(test_list)
        self.assertEqual(hashable_list, (1, 2, 3))

        # Test with nested list
        nested_list = [1, [2, 3], 4]
        hashable_nested = _make_hashable(nested_list)
        self.assertEqual(hashable_nested, (1, (2, 3), 4))

    def test_make_hashable_complex(self):
        """Test _make_hashable with complex nested structures"""
        # Test with complex nested structure
        complex_obj = {
            "list": [1, {"key": "value"}],
            "dict": {"nested": [1, 2, 3]},
        }
        hashable_complex = _make_hashable(complex_obj)
        expected = (
            ("dict", (("nested", (1, 2, 3)),)),
            ("list", (1, (("key", "value"),))),
        )
        self.assertEqual(hashable_complex, expected)

    def test_make_hashable_with_object(self):
        """Test _make_hashable with custom objects"""
        # Test with object having _value
        test_obj = AnObject("test_value")
        hashable_obj = _make_hashable(test_obj)
        self.assertEqual(hashable_obj, "test_value")

        # Test with nested object
        nested_obj = AnObject({"key": "value"})
        hashable_nested = _make_hashable(nested_obj)
        self.assertEqual(hashable_nested, (("key", "value"),))

    def test_cached_hash_simple_types(self):
        """Test _cached_hash with simple types"""
        # Test with simple types
        string_hash = _cached_hash("test")
        expected_hash = hashlib.sha1("test".encode("utf-8")).hexdigest()
        self.assertEqual(string_hash, expected_hash)

        int_hash = _cached_hash(123)
        expected_hash = hashlib.sha1("123".encode("utf-8")).hexdigest()
        self.assertEqual(int_hash, expected_hash)

    def test_cached_hash_complex_types(self):
        """Test _cached_hash with complex types"""
        # Test with tuple (hashable)
        tuple_value = (1, 2, 3)
        tuple_hash = _cached_hash(tuple_value)
        expected_hash = hashlib.sha1(str(tuple_value).encode("utf-8")).hexdigest()
        self.assertEqual(tuple_hash, expected_hash)

    def test_cached_hash_exception_handling(self):
        """Test _cached_hash exception handling"""
        # Create a simple object that will trigger the exception path
        bad_obj = BadStringObject()

        # Mock the json.dumps to avoid circular reference issues
        original_dumps = json.dumps

        try:
            # Replace json.dumps with a mock that returns a fixed string
            def mock_dumps(*args, **kwargs):
                return '{"mocked": "value"}'

            json.dumps = mock_dumps

            # This should now use our mocked json.dumps in the exception handler
            hash_result = _cached_hash(bad_obj)

            # Verify we got a hash (the exact value doesn't matter)
            self.assertTrue(isinstance(hash_result, str))
            self.assertEqual(len(hash_result), 40)  # SHA-1 hash is 40 chars
        finally:
            # Restore the original json.dumps
            json.dumps = original_dumps

    def test_get_hash_simple_types(self):
        """Test get_hash with simple types"""
        # Test with simple types
        string_hash = get_hash("test")
        expected_hash = hashlib.sha1("test".encode("utf-8")).hexdigest()
        self.assertEqual(string_hash, expected_hash)

        int_hash = get_hash(123)
        expected_hash = hashlib.sha1("123".encode("utf-8")).hexdigest()
        self.assertEqual(int_hash, expected_hash)

    def test_get_hash_dict(self):
        """Test get_hash with dictionaries"""
        # Test with dictionary
        test_dict = {"b": 2, "a": 1}
        dict_hash = get_hash(test_dict)

        # Create the same dictionary in different order
        test_dict2 = {"a": 1, "b": 2}
        dict_hash2 = get_hash(test_dict2)

        # Hashes should be the same regardless of key order
        self.assertEqual(dict_hash, dict_hash2)

    def test_get_hash_list(self):
        """Test get_hash with lists"""
        # Test with list
        test_list = [1, 2, 3]
        list_hash = get_hash(test_list)

        # The same list should produce the same hash
        list_hash2 = get_hash([1, 2, 3])
        self.assertEqual(list_hash, list_hash2)

    def test_get_hash_complex(self):
        """Test get_hash with complex nested structures"""
        # Test with complex nested structure
        complex_obj = {
            "list": [1, {"key": "value"}],
            "dict": {"nested": [1, 2, 3]},
        }
        complex_hash = get_hash(complex_obj)

        # Different order but same content
        complex_obj2 = {
            "dict": {"nested": [1, 2, 3]},
            "list": [1, {"key": "value"}],
        }
        complex_hash2 = get_hash(complex_obj2)

        # Hashes should be the same
        self.assertEqual(complex_hash, complex_hash2)

    def test_get_hash_with_object(self):
        """Test get_hash with custom objects"""
        # Test with object having _value
        test_obj = AnObject("test_value")
        obj_hash = get_hash(test_obj)

        # Should be the same as hashing the _value directly
        direct_hash = get_hash("test_value")
        self.assertEqual(obj_hash, direct_hash)

    def test_get_hash_exception_handling(self):
        """Test get_hash exception handling"""
        # Create a simple object that will trigger the exception path
        bad_obj = BadStringObject()

        # Mock the json.dumps to avoid circular reference issues
        original_dumps = json.dumps

        try:
            # Replace json.dumps with a mock that returns a fixed string
            def mock_dumps(*args, **kwargs):
                return '{"mocked": "value"}'

            json.dumps = mock_dumps

            # This should now use our mocked json.dumps in the exception handler
            hash_result = get_hash(bad_obj)

            # Verify we got a hash (the exact value doesn't matter)
            self.assertTrue(isinstance(hash_result, str))
            self.assertEqual(len(hash_result), 40)  # SHA-1 hash is 40 chars
        finally:
            # Restore the original json.dumps
            json.dumps = original_dumps

    def test_get_hash_make_hashable_exception(self):
        """Test get_hash when _make_hashable raises an exception"""
        # Create a mock for _make_hashable that raises an exception
        original_make_hashable = _make_hashable

        try:
            # Replace _make_hashable with a function that raises an exception
            def mock_make_hashable(obj):
                raise Exception("Cannot make hashable")

            # Monkey patch the function
            import cfnlint.conditions._utils

            cfnlint.conditions._utils._make_hashable = mock_make_hashable

            # Mock json.dumps to avoid circular reference issues
            original_dumps = json.dumps
            json.dumps = lambda *args, **kwargs: '{"mocked": "value"}'

            # This should trigger the fallback path in get_hash
            obj = {"test": "value"}
            hash_result = get_hash(obj)

            # Verify we got a hash
            self.assertTrue(isinstance(hash_result, str))
            self.assertEqual(len(hash_result), 40)  # SHA-1 hash is 40 chars
        finally:
            # Restore the original functions
            cfnlint.conditions._utils._make_hashable = original_make_hashable
            json.dumps = original_dumps

    def test_hash_consistency(self):
        """Test hash consistency across multiple calls"""
        # Test that the same object produces the same hash on multiple calls
        test_obj = {"complex": [1, 2, {"nested": "value"}]}

        hash1 = get_hash(test_obj)
        hash2 = get_hash(test_obj)
        hash3 = get_hash(test_obj)

        self.assertEqual(hash1, hash2)
        self.assertEqual(hash2, hash3)

    def test_lru_cache_effectiveness(self):
        """Test that the LRU cache is effective"""
        # Call get_hash multiple times with the same object
        test_obj = {"test": "value"}

        # First call should compute the hash
        hash1 = get_hash(test_obj)

        # Subsequent calls should use the cached value
        hash2 = get_hash(test_obj)

        self.assertEqual(hash1, hash2)

        # We can't directly test the cache hit, but we can
        # verify the result is consistent


if __name__ == "__main__":
    unittest.main()
