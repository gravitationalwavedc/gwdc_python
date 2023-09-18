from humps import decamelize

from .meta import GWDCObjectMeta
from ..helpers import JobStatus


class GWDCObjectBase(metaclass=GWDCObjectMeta):
    """Base class from which GWDC jobs will inherit. Provides a basic initialisation method,
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
        return self.id == other.id

    def get_full_file_list(self):
        f"""Get information for all files associated with this {self.__class__.__name__}

        Returns
        -------
        ~gwdc_python.files.file_reference.FileReferenceList
            Contains FileReference instances for each of the files associated with this {self.__class__.__name__}
        """
        return getattr(self.client, f'_get_files_by_{decamelize(self.__class__.__name__)}')(self)
        # result, self.job_type = self.client._get_files_by_job_id(self)
        # return result
