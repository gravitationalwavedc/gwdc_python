import pytest
from pathlib import Path
from collections import OrderedDict

from gwdc_python.objects.base import GWDCObjectBase
from gwdc_python.files.constants import GWDCObjectType
from gwdc_python.files.file_reference import FileReference, FileReferenceList
from gwdc_python.utils import remove_path_anchor


@pytest.fixture
def setup_dicts():
    return [
        {
            'path': 'data/dir/test1.png',
            'file_size': '1',
            'download_token': 'test_token_1',
            'parent': GWDCObjectBase(None, 'id1', GWDCObjectType.NORMAL)
        },
        {
            'path': 'data/dir/test2.png',
            'file_size': '1',
            'download_token': 'test_token_2',
            'parent': GWDCObjectBase(None, 'id1', GWDCObjectType.NORMAL)
        },
        {
            'path': 'result/dir/test1.txt',
            'file_size': '1',
            'download_token': 'test_token_3',
            'parent': GWDCObjectBase(None, 'id2', GWDCObjectType.UPLOADED)
        },
        {
            'path': 'result/dir/test2.txt',
            'file_size': '1',
            'download_token': 'test_token_4',
            'parent': GWDCObjectBase(None, 'id2', GWDCObjectType.UPLOADED)
        },
        {
            'path': 'test1.json',
            'file_size': '1',
            'download_token': 'test_token_5',
            'parent': GWDCObjectBase(None, 'id3', GWDCObjectType.NORMAL)
        },
        {
            'path': 'test2.json',
            'file_size': '1',
            'download_token': 'test_token_6',
            'parent': GWDCObjectBase(None, 'id3', GWDCObjectType.NORMAL)
        },
        {
            'path': 'https://myurl.com/test/file1.h5',
            'file_size': None,
            'download_token': None,
            'parent': GWDCObjectBase(None, 'id4', GWDCObjectType.EXTERNAL)
        },
    ]


def test_file_reference(setup_dicts):
    for file_dict in setup_dicts:
        ref = FileReference(**file_dict)
        if ref.parent.is_external():
            assert ref.path == file_dict['path']
            assert ref.file_size is None
        else:
            assert ref.path == remove_path_anchor(Path(file_dict['path']))
            assert ref.file_size == int(file_dict['file_size'])
        assert ref.download_token == file_dict['download_token']
        assert ref.parent == file_dict['parent']


def test_file_reference_list(setup_dicts):
    file_references = [FileReference(**file_dict) for file_dict in setup_dicts]
    file_reference_list = FileReferenceList(file_references)

    for i, ref in enumerate(file_reference_list):
        assert ref.path == file_references[i].path
        assert ref.file_size == file_references[i].file_size
        assert ref.download_token == file_references[i].download_token
        assert ref.parent == file_references[i].parent

    assert (file_reference_list.get_total_bytes() ==
            sum([ref.file_size for ref in file_references if ref.file_size is not None]))
    assert file_reference_list.get_tokens() == [ref.download_token for ref in file_references]
    assert file_reference_list.get_paths() == [ref.path for ref in file_references]
    assert file_reference_list.get_parent_type() == [ref.parent.type for ref in file_references]


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


def test_batch_file_reference_list(setup_dicts):
    file_reference_list = FileReferenceList([FileReference(**file_dict) for file_dict in setup_dicts])

    batched = OrderedDict(
        id1=file_reference_list[0:2],
        id2=file_reference_list[2:4],
        id3=file_reference_list[4:6],
        id4=file_reference_list[6:8],
    )

    assert file_reference_list.batched == batched
