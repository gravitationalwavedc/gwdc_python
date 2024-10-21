from humps import decamelize

from .meta import GWDCObjectMeta
from ..files.constants import GWDCObjectType


class GWDCObjectBase(metaclass=GWDCObjectMeta):
    """Base class from which GWDC objects will inherit. Provides a basic initialisation method,
    an equality check, a neat string representation and a method with which to get the full file list.
    """

    def __init__(self, client, _id, _type=None):
        self.client = client
        self.id = _id
        self.type = _type

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id and self.type == other.type

    def get_full_file_list(self):
        f"""Get information for all files associated with this {self.__class__.__name__}

        Returns
        -------
        ~gwdc_python.files.file_reference.FileReferenceList
            Contains FileReference instances for each of the files associated with this {self.__class__.__name__}
        """
        return getattr(
            self.client, f"_get_files_by_{decamelize(self.__class__.__name__)}"
        )(self)

    def is_normal(self):
        f"""Is this a normal {self.__class__.__name__}

        Returns
        -------
        bool
            True if this {self.__class__.__name__} was created normally, otherwise False
        """
        return self.type == GWDCObjectType.NORMAL

    def is_uploaded(self):
        f"""Is this an uploaded {self.__class__.__name__}

        Returns
        -------
        bool
            True if this {self.__class__.__name__} was uploaded, otherwise False
        """
        return self.type == GWDCObjectType.UPLOADED

    def is_external(self):
        f"""Is this an external {self.__class__.__name__}

        Returns
        -------
        bool
            True if this is an external {self.__class__.__name__}, otherwise False
        """
        return self.type == GWDCObjectType.EXTERNAL
