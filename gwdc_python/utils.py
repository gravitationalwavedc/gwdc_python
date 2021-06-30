import io
import os


def split_variables_dict(variables):
    """Recursively travel through a dict, replacing any instances of a file-like object with None and moving the
    file-like objects to a separate dict

    Parameters
    ----------
    variables : dict
        Dictionary of variables for a graphql query

    Returns
    -------
    dict
        Variables dictionary with all file-like objects replaced with None
    dict
        Dictionary containing the file-like objects with keys based on the paths in the variables dict
    dict
        Dictionary with keys and values corresponding to the paths of the file-like objects in the variables dict.
    """    
    
    files = {}
    files_map = {}

    def extract_files(path, obj):
        nonlocal files, files_map
        if type(obj) is list:
            nulled_obj = []
            for key, value in enumerate(obj):
                value = extract_files(f"{path}.{key}", value)
                nulled_obj.append(value)
            return nulled_obj
        elif type(obj) is dict:
            nulled_obj = {}
            for key, value in obj.items():
                value = extract_files(f"{path}.{key}", value)
                nulled_obj[key] = value
            return nulled_obj
        elif isinstance(obj, io.IOBase):
            files[path] = (os.path.basename(obj.name), obj)
            files_map[path] = [path]
            return None
        else:
            return obj

    nulled_variables = extract_files("variables", variables)

    return nulled_variables, files, files_map