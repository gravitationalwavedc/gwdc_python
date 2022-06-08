import pytest
from pathlib import Path
from gwdc_python.utils import remove_path_anchor, rename_dict_keys


def test_remove_path_anchor():
    assert remove_path_anchor(Path('/a/test/absolute/path')) == Path('a/test/absolute/path')
    assert remove_path_anchor(Path('//another/test/absolute/path')) == Path('another/test/absolute/path')
    assert remove_path_anchor(Path('a/test/relative/path')) == Path('a/test/relative/path')
    assert remove_path_anchor(Path('./another/test/relative/path')) == Path('another/test/relative/path')


WORD_1 = 'arbitrary'
WORD_2 = 'test'
WORD_3 = 'words'
RENAMED_WORD = 'renamed'


single_dict = {
    WORD_1: 0,
    WORD_2: 1,
    WORD_3: 2,
}

renamed_single_dict = {
    RENAMED_WORD: 0,
    WORD_2: 1,
    WORD_3: 2,
}

nested_dict = {
    WORD_1: 0,
    WORD_2: 1,
    WORD_3: {
        WORD_1: 0,
        WORD_2: 1,
        WORD_3: 2,
    },
}

renamed_nested_dict = {
    RENAMED_WORD: 0,
    WORD_2: 1,
    WORD_3: {
        RENAMED_WORD: 0,
        WORD_2: 1,
        WORD_3: 2,
    },
}

listed_dict = {
    WORD_1: 0,
    WORD_2: 1,
    WORD_3: [
        WORD_1,
        WORD_2,
        WORD_3,
    ],
}

renamed_listed_dict = {
    RENAMED_WORD: 0,
    WORD_2: 1,
    WORD_3: [
        WORD_1,
        WORD_2,
        WORD_3,
    ],
}

nested_listed_dict = {
    WORD_1: 0,
    WORD_2: {
        WORD_1: 0,
        WORD_2: 1,
        WORD_3: 2,
    },
    WORD_3: [
        {
            WORD_1: 0,
            WORD_2: 1,
            WORD_3: 2,
        },
        WORD_2,
        WORD_3,
    ],
}

renamed_nested_listed_dict = {
    RENAMED_WORD: 0,
    WORD_2: {
        RENAMED_WORD: 0,
        WORD_2: 1,
        WORD_3: 2,
    },
    WORD_3: [
        {
            RENAMED_WORD: 0,
            WORD_2: 1,
            WORD_3: 2,
        },
        WORD_2,
        WORD_3,
    ],
}


@pytest.mark.parametrize(
    "test_dict, renamed_test_dict",
    [
        (single_dict, renamed_single_dict),
        (nested_dict, renamed_nested_dict),
        (listed_dict, renamed_listed_dict),
        (nested_listed_dict, renamed_nested_listed_dict),
    ]
)
def test_renamed_dict_keys(test_dict, renamed_test_dict):
    assert rename_dict_keys(test_dict, {WORD_1: RENAMED_WORD}) == renamed_test_dict
