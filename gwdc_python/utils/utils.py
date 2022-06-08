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


def remove_path_anchor(path):
    """Removes the path anchor, making it a relative path

    Parameters
    ----------
    path : ~pathlib.Path
        Path from which to strip anchor

    Returns
    -------
    Path
        Relative path
    """
    if path.is_absolute():
        return path.relative_to(path.anchor)
    else:
        return path


def rename_dict_keys(input_obj, key_map):
    """Renames the keys in a dictionary

    Parameters
    ----------
    input_obj : dict or list
        Object within which to recursively substitute dictionary keys
    key_map : dict
        Dictionary which specifies old keys to be swapped with new keys in the input_obj, e.g `{'old_key': 'new_key'}`

    Returns
    -------
    dict or list
        Copy of `input_obj` with old keys subbed for new keys
    """
    if isinstance(input_obj, dict):  # if dict, apply to each key
        return {key_map.get(k, k): rename_dict_keys(v, key_map) for k, v in input_obj.items()}
    elif isinstance(input_obj, list):  # if list, apply to each element
        return [rename_dict_keys(elem, key_map) for elem in input_obj]
    else:
        return input_obj
