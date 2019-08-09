import re

class TestStub(object):
    pass

def validate_non_empty_string(self, function_raising_error, exception_message):
    values = [None, False, True, {}, [], 123]
    error_regex = re.compile(exception_message)

    for value in values:
        with self.subTest(value=value):
            with self.assertRaises(ValueError) as cm:
                function_raising_error(value)

            self.assertTrue(error_regex.match(str(cm.exception)))

def validate_provided(callback):
    callback(None)

def validate_object_with_methods(self, method_names, callback):
    for method_name in method_names:
        with self.subTest(method_name=method_name):
            selected_methods = [name for name in method_names if name != method_name]

            stub_object = TestStub()
            for name in selected_methods:
                setattr(stub_object, name, lambda: None)

            callback(stub_object, method_name)

def validate_dict_keys(self, function_raising_error, exception_message, keys):
    value = dict.fromkeys(keys, "xyz")
    error_regex = re.compile(exception_message)

    for key in keys:
        value_without_key = {k: value[k] for k in value if k is not key}

        with self.subTest(value=value_without_key):
            with self.assertRaises(ValueError) as cm:
                function_raising_error(value_without_key)

            self.assertTrue(error_regex.match(str(cm.exception)))
