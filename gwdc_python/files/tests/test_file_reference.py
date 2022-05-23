import pytest
from pathlib import Path
from collections import OrderedDict
from gwdc_python.files.file_reference import FileReference, FileReferenceList
from gwdc_python.utils import remove_path_anchor


@pytest.fixture
def setup_dicts():
    return [
        {
            'path': 'data/dir/test1.png',
            'file_size': '1',
            'download_token': 'test_token_1',
            'job_id': 'id1',
            'uploaded': False
        },
        {
            'path': 'data/dir/test2.png',
            'file_size': '1',
            'download_token': 'test_token_2',
            'job_id': 'id1',
            'uploaded': False
        },
        {
            'path': 'result/dir/test1.txt',
            'file_size': '1',
            'download_token': 'test_token_3',
            'job_id': 'id2',
            'uploaded': True
        },
        {
            'path': 'result/dir/test2.txt',
            'file_size': '1',
            'download_token': 'test_token_4',
            'job_id': 'id2',
            'uploaded': True
        },
        {
            'path': 'test1.json',
            'file_size': '1',
            'download_token': 'test_token_5',
            'job_id': 'id3',
            'uploaded': False
        },
        {
            'path': 'test2.json',
            'file_size': '1',
            'download_token': 'test_token_6',
            'job_id': 'id3',
            'uploaded': False
        },
    ]


def test_file_reference(setup_dicts):
    for file_dict in setup_dicts:
        ref = FileReference(**file_dict)
        assert ref.path == remove_path_anchor(Path(file_dict['path']))
        assert ref.file_size == int(file_dict['file_size'])
        assert ref.download_token == file_dict['download_token']
        assert ref.job_id == file_dict['job_id']
        assert ref.uploaded == file_dict['uploaded']


def test_file_reference_list(setup_dicts):
    file_references = [FileReference(**file_dict) for file_dict in setup_dicts]
    file_reference_list = FileReferenceList(file_references)

    for i, ref in enumerate(file_reference_list):
        assert ref.path == file_references[i].path
        assert ref.file_size == file_references[i].file_size
        assert ref.download_token == file_references[i].download_token
        assert ref.job_id == file_references[i].job_id
        assert ref.uploaded == file_references[i].uploaded

    assert file_reference_list.get_total_bytes() == sum([ref.file_size for ref in file_references])
    assert file_reference_list.get_tokens() == [ref.download_token for ref in file_references]
    assert file_reference_list.get_paths() == [ref.path for ref in file_references]
    assert file_reference_list.get_uploaded() == [ref.uploaded for ref in file_references]


def test_file_reference_list_types(setup_dicts):
    # FileReferenceList can be created from list of FileReference objects
    file_references = [FileReference(**file_dict) for file_dict in setup_dicts]
    file_reference_list = FileReferenceList(file_references)

    # FileReferenceList can be created by appending FileReferenceObjects
    file_reference_list_appended = FileReferenceList()
    for ref in file_references:
        file_reference_list_appended.append(ref)

    assert file_reference_list == file_reference_list_appended

    # Check that other types can't be appended or included in initial data
    with pytest.raises(TypeError):
        FileReferenceList().append(1)

    with pytest.raises(TypeError):
        FileReferenceList().append('string')

    with pytest.raises(TypeError):
        FileReferenceList([1])

    with pytest.raises(TypeError):
        FileReferenceList(['string'])


def test_file_reference_list_output_paths(setup_dicts):
    file_reference_list = FileReferenceList([FileReference(**file_dict) for file_dict in setup_dicts])

    root_path = Path('test_dir')
    output_paths = [
        root_path / 'data/dir/test1.png',
        root_path / 'data/dir/test2.png',
        root_path / 'result/dir/test1.txt',
        root_path / 'result/dir/test2.txt',
        root_path / 'test1.json',
        root_path / 'test2.json'
    ]
    output_paths_flat = [
        root_path / 'test1.png',
        root_path / 'test2.png',
        root_path / 'test1.txt',
        root_path / 'test2.txt',
        root_path / 'test1.json',
        root_path / 'test2.json'
    ]
    assert output_paths == file_reference_list.get_output_paths(root_path)
    assert output_paths_flat == file_reference_list.get_output_paths(root_path, preserve_directory_structure=False)


def test_batch_file_reference_list(setup_dicts):
    file_reference_list = FileReferenceList([FileReference(**file_dict) for file_dict in setup_dicts])

    batched = OrderedDict(
        id1=file_reference_list[0:2],
        id2=file_reference_list[2:4],
        id3=file_reference_list[4:6],
    )

    assert file_reference_list.batched == batched
