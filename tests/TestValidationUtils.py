import re

def validate_non_empty_string(self, function_raising_error, exception_message):
    values = [None, False, True, {}, [], 123]
    error_regex = re.compile(exception_message)

    for value in values:
        with self.subTest(value=value):
            with self.assertRaises(ValueError) as cm:
                function_raising_error(value)

            self.assertTrue(error_regex.match(str(cm.exception)))
