def validate_non_empty_string(parameter, parameter_name):
    if (not parameter or not isinstance(parameter, str)):
        raise ValueError("InvalidArgument: {} must be a non-empty string"
                         .format(parameter_name))

def validate_dict_keys(parameter, parameter_name, keys):
    if not parameter:
        raise ValueError("InvalidArgument: {} must be provided"
                         .format(parameter_name))

    if not isinstance(parameter, dict):
        raise ValueError("InvalidArgument: {} must be a dictionary"
                         .format(parameter_name))

    for key in keys:
        if not key in parameter:
            raise ValueError("InvalidArgument: {} dictionary must have {} key"
                                .format(parameter_name, key))
