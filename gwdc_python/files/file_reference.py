from dataclasses import dataclass, field
from pathlib import Path
from . import filters
from .constants import JobType
from ..utils import remove_path_anchor, TypedList


@dataclass
class FileReference:
    """Object used to facilitate simpler downloading of files.
    """

    path: str
    file_size: int = field(repr=False)
    download_token: str = field(repr=False)
    job_id: int = field(repr=False)
    job_type: int = field(repr=False, default=JobType.NORMAL_JOB)

    def __post_init__(self):
        if self.job_type != JobType.EXTERNAL_JOB:
            self.path = remove_path_anchor(Path(self.path))
            self.file_size = int(self.file_size)


class FileReferenceList(TypedList):
    def __init__(self, data=[]):
        super().__init__(item_type=FileReference, data=data)

    @property
    def batched(self):
        _batched = {}
        for ref in self.data:
            refs = _batched.get(ref.job_id, FileReferenceList())
            refs.append(ref)
            _batched[ref.job_id] = refs
        return _batched

    def filter_list(self, file_filter_fn, *args, **kwargs):
        """Create a subset of this list by filtering the contents with a function.

        Parameters
        ----------
        file_filter_fn : function
            Must take a list of FileReference objects and return only those that are desired

        Returns
        -------
        FileReferenceList
            Filtered list
        """
        return FileReferenceList(file_filter_fn(self.data, *args, **kwargs))

    def filter_list_by_path(self, directory=None, name=None, extension=None):
        """Create a subset of this list by filtering the contents based on their path attributes

        Parameters
        ----------
        directory : str, optional
            Matches any of the directories in the file path, by default None
        name : str, optional
            Matches the name of the file, by default None
        extension : str, optional
            Matches the file extension, by default None

        Returns
        -------
        FileReferenceList
            Filtered list
        """
        return self.filter_list(filters.custom_path_filter, directory, name, extension)

    def get_total_bytes(self):
        """Sum the total size of each file represented in the list

        Returns
        -------
        int
            Total size of all files
        """
        total_bytes = 0
        for ref in self.data:
            if ref.file_size is not None:
                total_bytes += ref.file_size

        return total_bytes

    def get_tokens(self):
        """Get all the download tokens in a list

        Returns
        -------
        list
            List of download tokens
        """
        return [ref.download_token for ref in self.data]

    def get_paths(self):
        """Get all the file paths in a list

        Returns
        -------
        list
            List of file paths
        """
        return [ref.path for ref in self.data]

    def get_job_type(self):
        """Get the job type for each job in a list

        Returns
        -------
        list
            List of JobType for jobs
        """
        return [ref.job_type for ref in self.data]

    def get_output_paths(self, root_path, preserve_directory_structure=True):
        """Get all the file paths modified to give them a base directory.
        Can also optionally remove any existing directory structure

        Parameters
        ----------
        root_path : str or ~pathlib.Path
            Directory to add to the beginning of the file paths
        preserve_directory_structure : bool, optional
            Retain existing directory structure in the file paths, by default True

        Returns
        -------
        list
            List of output file paths
        """
        paths = []
        for ref in self.data:
            if ref.job_type == JobType.EXTERNAL_JOB:
                # Ignored for external jobs
                continue
            else:
                path = ref.path

            if preserve_directory_structure:
                paths.append(root_path / path)
            else:
                paths.append(root_path / Path(path.name))

        return paths
