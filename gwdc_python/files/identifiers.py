from pathlib import Path


def match_file_suffix(file_path, suffix):
    return file_path.suffix == f'.{suffix}'


def match_file_base_dir(file_path, directory):
    parents = Path(file_path.parent).parts
    if parents:
        return parents[0] == directory
    return False


def match_file_dir(file_path, directory):
    parents = Path(file_path.parent).parts
    if parents:
        return directory in parents
    return False


def match_file_stem(file_path, stem):
    return stem in file_path.stem


def match_file_name(file_path, name):
    return name in file_path.name


def match_file_end(file_path, end):
    return file_path.name.endswith(end)
