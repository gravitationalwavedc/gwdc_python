from gwdc_python.objects.base import GWDCObjectBase
from gwdc_python.files.constants import GWDCObjectType


def test_object_base_equality(mocker):
    test_object = GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.NORMAL)
    assert test_object == GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.NORMAL)
    assert test_object != GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.UPLOADED)
    assert test_object != GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.EXTERNAL)
    assert test_object != GWDCObjectBase(mocker.Mock(), 2, GWDCObjectType.NORMAL)
    assert test_object != GWDCObjectBase(mocker.Mock(), 2, GWDCObjectType.UPLOADED)
    assert test_object != GWDCObjectBase(mocker.Mock(), 2, GWDCObjectType.EXTERNAL)


def test_object_base_type_methods(mocker):
    test_object = GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.NORMAL)
    assert test_object.is_normal()
    assert not test_object.is_uploaded()
    assert not test_object.is_external()

    test_object = GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.UPLOADED)
    assert not test_object.is_normal()
    assert test_object.is_uploaded()
    assert not test_object.is_external()

    test_object = GWDCObjectBase(mocker.Mock(), 1, GWDCObjectType.EXTERNAL)
    assert not test_object.is_normal()
    assert not test_object.is_uploaded()
    assert test_object.is_external()
