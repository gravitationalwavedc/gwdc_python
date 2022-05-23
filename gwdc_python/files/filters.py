from functools import partial, reduce
from .identifiers import match_file_dir, match_file_stem, match_file_suffix


def filter_file_list(identifier, file_list):
    """Takes an identifier and used it to filter an input FileReferenceList

    Parameters
    ----------
    identifier : function
        Function that takes a Path and returns True if it matches the desired pattern
    file_list : FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    FileReferenceList
        List of FileReference objects filtered by the identifier
    """
    matches = []
    others = []
    for f in file_list:
        if identifier(f.path):
            matches.append(f)
        else:
            others.append(f)
    return matches, others


def match_all(identifiers, file_list):
    """Takes a list of identifier functions and uses it to filter an input FileReferenceList

    Parameters
    ----------
    identifier : list
        List of identifier functions
    file_list : FileReferenceList
        A list of FileReference objects which will be filtered

    Returns
    -------
    FileReferenceList
        List of FileReference objects which match all of the identifier functions
    """
    return reduce(lambda res, f: filter_file_list(f, res)[0], identifiers, file_list)


def custom_path_filter(file_list, directory=None, name=None, extension=None):
    """Takes an input file list and returns a subset of that file list containing:

    - Any file that has any enclosing directory matching the `directory` argument
    - Any file that has any part of its filename matching the `name` argument
    - Any file that has an extension matching the `extension` argument

    Parameters
    ----------
    file_list : .FileReferenceList
        A list of FileReference objects which will be filtered
    directory : str, optional
        Directory to match, by default None
    name : str, optional
        Part of filename to match, by default None
    extension : str, optional
        File extension to match, by default None

    Returns
    -------
    .FileReferenceList
        Subset of the input FileReferenceList containing only the paths that match the above corner plot file criteria
    """
    identifiers = []
    if directory:
        identifiers.append(partial(match_file_dir, directory=str(directory)))
    if name:
        identifiers.append(partial(match_file_stem, stem=str(name)))
    if extension:
        identifiers.append(partial(match_file_suffix, suffix=str(extension)))

    return match_all(identifiers, file_list)
