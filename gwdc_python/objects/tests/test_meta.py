import pytest
from gwdc_python.files import FileReference, FileReferenceList
from gwdc_python.objects.meta import GWDCObjectMeta


@pytest.fixture
def mock_parent(mocker):
    return mocker.Mock(**{"is_external.return_value": False})


@pytest.fixture
def html(mock_parent):
    return FileReferenceList(
        [
            FileReference(
                path="test/dir/test1.html",
                file_size="1",
                download_token="test_token_1",
                parent=mock_parent,
            ),
            FileReference(
                path="test2.html",
                file_size="1",
                download_token="test_token_2",
                parent=mock_parent,
            ),
        ]
    )


@pytest.fixture
def extra(mock_parent):
    return FileReferenceList(
        [
            FileReference(
                path="html.png",
                file_size="1",
                download_token="test_token_3",
                parent=mock_parent,
            ),
            FileReference(
                path="html",
                file_size="1",
                download_token="test_token_4",
                parent=mock_parent,
            ),
            FileReference(
                path="html/dir/test.txt",
                file_size="1",
                download_token="test_token_5",
                parent=mock_parent,
            ),
        ]
    )


class TrivialClass(metaclass=GWDCObjectMeta):
    pass


def test_filter():
    pass


class ObjectClass(metaclass=GWDCObjectMeta):
    FILE_LIST_FILTERS = {"test": test_filter}


def test_object_meta_methods():
    assert not hasattr(TrivialClass, "get_test_file_list")
    assert not hasattr(TrivialClass, "get_test_files")
    assert not hasattr(TrivialClass, "save_test_files")

    assert hasattr(ObjectClass, "get_test_file_list")
    assert hasattr(ObjectClass, "get_test_files")
    assert hasattr(ObjectClass, "save_test_files")


def test_get_file_list(mocker):
    mock_object = ObjectClass()
    mock_object.get_full_file_list = mocker.Mock()
    mock_object.get_test_file_list()
    assert mock_object.get_full_file_list.call_count == 1
    assert mock_object.get_full_file_list.return_value.filter_list.call_count == 1


def test_register_file_list_filter(mocker, html, extra):
    mock_object = TrivialClass()
    mock_object.get_full_file_list = mocker.Mock(return_value=html + extra)

    def get_html_file(file_list):
        return [f for f in file_list if f.path.suffix == ".html"]

    assert getattr(mock_object, "get_html_file_list", None) is None
    assert getattr(mock_object, "get_html_files", None) is None
    assert getattr(mock_object, "save_html_files", None) is None

    TrivialClass.register_file_list_filter("html", get_html_file)

    assert getattr(mock_object, "get_html_file_list", None) is not None
    assert getattr(mock_object, "get_html_files", None) is not None
    assert getattr(mock_object, "save_html_files", None) is not None

    assert mock_object.get_html_file_list() == html
