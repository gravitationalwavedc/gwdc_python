import pytest
from pathlib import Path
from functools import partial
from gwdc_python.files.identifiers import (
    match_file_suffix,
    match_file_base_dir,
    match_file_dir,
    match_file_stem,
    match_file_name,
    match_file_end
)


@pytest.fixture
def setup_paths():
    return {
        'txt': Path('test.txt'),
        'dir_txt': Path('this/is/a/test.txt'),
        'txt_dir': Path('is/this/not/a/txt'),

        'just_txt': Path('txt'),
        'just_test': Path('test'),
        'just_this': Path('this'),

        'test_base_dir': Path('test/dir.png'),
        'test_dir': Path('this/test/is/okay.png'),

        'test_stem': Path('this/is/a/stem.test'),
        'test_stem_again': Path('this/is/a/stem_test'),

        'long_name': Path('a_complicated_and_long_name.test'),
        'dir_long_name': Path('test/a_complicated_and_long_name.test'),
        'dir_long_name_multi': Path('test/a_complicated_and_long_name.test.multi'),
    }


@pytest.mark.parametrize(
    'identifier, true_path_keys',
    [
        (
            partial(match_file_suffix, suffix='txt'),
            ['txt', 'dir_txt']
        ),
        (
            partial(match_file_suffix, suffix='test'),
            ['test_stem', 'long_name', 'dir_long_name']
        ),
        (
            partial(match_file_base_dir, directory='test'),
            ['test_base_dir', 'dir_long_name', 'dir_long_name_multi']
        ),
        (
            partial(match_file_base_dir, directory='this'),
            ['dir_txt', 'test_dir', 'test_stem', 'test_stem_again']
        ),
        (
            partial(match_file_dir, directory='test'),
            ['test_dir', 'test_base_dir', 'dir_long_name', 'dir_long_name_multi']
        ),
        (
            partial(match_file_dir, directory='this'),
            ['txt_dir', 'dir_txt', 'test_dir', 'test_stem', 'test_stem_again']
        ),
        (
            partial(match_file_stem, stem='test'),
            ['txt', 'dir_txt', 'just_test', 'test_stem_again', 'dir_long_name_multi']
        ),
        (
            partial(match_file_stem, stem='stem'),
            ['test_stem', 'test_stem_again']
        ),
        (
            partial(match_file_name, name='test'),
            [
                'txt',
                'dir_txt',
                'just_test',
                'test_stem',
                'test_stem_again',
                'long_name',
                'dir_long_name',
                'dir_long_name_multi'
            ]
        ),
        (
            partial(match_file_name, name='txt'),
            ['txt', 'dir_txt', 'txt_dir', 'just_txt']
        ),
        (
            partial(match_file_end, end='test'),
            ['just_test', 'test_stem', 'test_stem_again', 'long_name', 'dir_long_name']
        ),
        (
            partial(match_file_end, end='_and_long_name.test'),
            ['long_name', 'dir_long_name']
        ),
    ]
)
def test_identifiers(identifier, true_path_keys, setup_paths):
    true_paths = [value for key, value in setup_paths.items() if key in true_path_keys]
    false_paths = [value for key, value in setup_paths.items() if key not in true_path_keys]

    for path in true_paths:
        assert identifier(path) is True

    for path in false_paths:
        assert identifier(path) is False
