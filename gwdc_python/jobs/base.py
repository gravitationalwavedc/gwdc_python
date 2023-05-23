from .meta import JobMeta
from ..helpers import JobStatus


class JobBase(metaclass=JobMeta):
    """Base class from which GWDC jobs will inherit. Provides a basic initialisation method,
    an equality check, a neat string representation and a method with which to get the full file list.
    """

    def __init__(self, client, job_id, name, description, user, job_status):
        self.client = client
        self.job_id = job_id
        self.name = name
        self.description = description
        self.user = user
        self.status = JobStatus(status=job_status['name'], date=job_status['date'])
        self.job_type = None

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, job_id={self.job_id})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.job_id == other.job_id and
                self.name == other.name and
                self.user == other.user
            )
        return False

    def get_full_file_list(self):
        """Get information for all files associated with this job

        Returns
        -------
        ~gwdc_python.files.file_reference.FileReferenceList
            Contains FileReference instances for each of the files associated with this job
        """
        result, self.job_type = self.client._get_files_by_job_id(self.job_id)
        return result
