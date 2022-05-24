import pytest
from functools import partial
from gwdc_python.files.filters import filter_file_list, match_all, custom_path_filter
from gwdc_python.files.file_reference import FileReference, FileReferenceList


@pytest.fixture
def refs():
    test_dir = FileReference(
        path='test/name.ext',
        file_size='1',
        download_token='test_token_1',
        job_id='id'
    )
    test_name = FileReference(
        path='dir/test.ext',
        file_size='1',
        download_token='test_token_1',
        job_id='id'
    )
    test_ext = FileReference(
        path='dir/name.test',
        file_size='1',
        download_token='test_token_1',
        job_id='id'
    )

    return {
        'dir': FileReferenceList([test_name, test_ext]),
        'test_dir': FileReferenceList([test_dir]),
        'name': FileReferenceList([test_dir, test_ext]),
        'test_name': FileReferenceList([test_name]),
        'ext': FileReferenceList([test_dir, test_name]),
        'test_ext': FileReferenceList([test_ext]),
        'all': FileReferenceList([test_dir, test_name, test_ext]),
        'none': FileReferenceList([])
    }


def test_filter_file_list(mocker, refs):
    mock_identifier = mocker.Mock(side_effect=lambda path: path != refs['all'][0].path)
    filtered, other = filter_file_list(mock_identifier, refs['all'])
    assert filtered == refs['dir']
    assert other == refs['test_dir']
    mock_identifier.assert_has_calls([
        mocker.call(ref.path) for ref in refs['all']
    ])


def test_match_all(mocker, refs):
    mock_identifier1 = mocker.Mock(side_effect=lambda path: path != refs['all'][0].path)
    mock_identifier2 = mocker.Mock(side_effect=lambda path: path != refs['all'][1].path)
    filtered = match_all([mock_identifier1, mock_identifier2], refs['all'])
    assert filtered == refs['test_ext']
    mock_identifier1.assert_has_calls([
        mocker.call(ref.path) for ref in refs['all']
    ])
    mock_identifier2.assert_has_calls([
        mocker.call(ref.path) for ref in refs['dir']
    ])


def test_custom_path_file_filter(refs):
    custom_filter = partial(custom_path_filter, file_list=refs['all'])

    # No arguments
    assert custom_filter() == refs['all']

    # Single argument
    assert custom_filter(directory='dir') == refs['dir']
    assert custom_filter(directory='test') == refs['test_dir']
    assert custom_filter(directory='name') == refs['none']

    assert custom_filter(name='name') == refs['name']
    assert custom_filter(name='test') == refs['test_name']
    assert custom_filter(name='ext') == refs['none']

    assert custom_filter(extension='ext') == refs['ext']
    assert custom_filter(extension='test') == refs['test_ext']
    assert custom_filter(extension='dir') == refs['none']

    # Two arguments
    assert custom_filter(directory='dir', name='name') == refs['test_ext']
    assert custom_filter(directory='dir', name='test') == refs['test_name']
    assert custom_filter(directory='test', name='name') == refs['test_dir']
    assert custom_filter(directory='test', name='test') == refs['none']

    assert custom_filter(name='name', extension='ext') == refs['test_dir']
    assert custom_filter(name='name', extension='test') == refs['test_ext']
    assert custom_filter(name='test', extension='ext') == refs['test_name']
    assert custom_filter(name='test', extension='test') == refs['none']

    assert custom_filter(directory='dir', extension='ext') == refs['test_name']
    assert custom_filter(directory='dir', extension='test') == refs['test_ext']
    assert custom_filter(directory='test', extension='ext') == refs['test_dir']
    assert custom_filter(directory='test', extension='test') == refs['none']

    # Three arguments
    assert custom_filter(directory='dir', name='name', extension='ext') == refs['none']
    assert custom_filter(directory='dir', name='name', extension='test') == refs['test_ext']
    assert custom_filter(directory='dir', name='test', extension='ext') == refs['test_name']
    assert custom_filter(directory='dir', name='test', extension='test') == refs['none']

    assert custom_filter(directory='test', name='name', extension='ext') == refs['test_dir']
    assert custom_filter(directory='test', name='name', extension='test') == refs['none']
    assert custom_filter(directory='test', name='test', extension='ext') == refs['none']
    assert custom_filter(directory='test', name='test', extension='test') == refs['none']
