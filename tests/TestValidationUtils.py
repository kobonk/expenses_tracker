import re

class TestStub(object):
    pass

def validate_non_empty_string(sut, function_raising_error, exception_message):
    values = [None, False, True, {}, [], 123]
    error_regex = re.compile(exception_message)

    for value in values:
        with sut.subTest(value=value):
            with sut.assertRaises(ValueError) as cm:
                function_raising_error(value)

            sut.assertTrue(error_regex.match(str(cm.exception)))

def validate_provided(callback):
    callback(None)

def validate_object_with_methods(sut, method_names, callback):
    for method_name in method_names:
        with sut.subTest(method_name=method_name):
            selected_methods = [name for name in method_names if name != method_name]

            stub_object = TestStub()
            for name in selected_methods:
                setattr(stub_object, name, lambda: None)

            callback(stub_object, method_name)

def validate_dict_keys(sut, function_raising_error, exception_message, keys):
    value = dict.fromkeys(keys, "xyz")
    error_regex = re.compile(exception_message)

    for key in keys:
        value_without_key = {k: value[k] for k in value if k is not key}

        with sut.subTest(value=value_without_key):
            with sut.assertRaises(ValueError) as cm:
                function_raising_error(value_without_key)

            sut.assertTrue(error_regex.match(str(cm.exception)))

def validate_dict(sut, function_raising_error, value, validator_map):
    for key, (validate, exception_message) in validator_map.items():
        def callback(property_value):
            updated_value = value.copy()
            updated_value[key] = property_value

            function_raising_error(updated_value)

        validate(sut, callback, exception_message)
