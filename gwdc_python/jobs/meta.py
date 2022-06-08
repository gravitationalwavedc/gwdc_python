class JobMeta(type):
    """Metaclass for GWDC jobs, which is used to dynamically add methods based on job list filters
    """
    def __new__(cls, classname, bases, attrs):
        new_class = super().__new__(cls, classname, bases, attrs)
        for name, func in attrs.get('FILE_LIST_FILTERS', {}).items():
            new_class.register_file_list_filter(name, func)
        return new_class

    def register_file_list_filter(self, name, file_list_filter_fn):
        """Register a function used to filter the file list.
        This will create three methods on the class using this filter function:

        - get_{name}_file_list
        - get_{name}_files
        - save_{name}_files

        where {name} is the input name string.

        Parameters
        ----------
        name : str
            String used to name the added methods
        file_list_filter_fn : function
            A function that takes in the full file list and returns only the desired entries from the list
        """
        spaced_name = name.replace('_', ' ')

        def _get_file_list_subset(self):
            full_list = self.get_full_file_list()
            return full_list.filter_list(file_list_filter_fn)

        file_list_fn_name = f'get_{name}_file_list'
        file_list_fn = _get_file_list_subset
        file_list_fn.__doc__ = f"""Get information for the {spaced_name} files associated with this job

            Returns
            -------
            ~gwdc_python.files._file_reference.FileReferenceList
                Contains FileReference instances holding information on the {spaced_name} files
        """

        setattr(self, file_list_fn_name, file_list_fn)

        def _get_files(self):
            file_list = _get_file_list_subset(self)
            return self.client.get_files_by_reference(file_list)

        files_fn_name = f'get_{name}_files'
        files_fn = _get_files
        files_fn.__doc__ = f"""Download the content of all the {spaced_name} files.

            **WARNING**:
            *As the file contents are stored in memory, we suggest being cautious about
            the size of files being downloaded. If the files are large or very numerous,
            it is suggested to save the files and read them as needed instead.*

            Returns
            -------
            list
                List containing tuples of the file path and associated file contents
        """

        setattr(self, files_fn_name, files_fn)

        def _save_files(self, root_path, preserve_directory_structure=True):
            file_list = _get_file_list_subset(self)
            return self.client.save_files_by_reference(file_list, root_path, preserve_directory_structure)

        save_fn_name = f'save_{name}_files'
        save_fn = _save_files
        save_fn.__doc__ = f"""Download and save the {spaced_name} files.

            Parameters
            ----------
            root_path : str or ~pathlib.Path
                The base directory into which the files will be saved
            preserve_directory_structure : bool, optional
                Save the files in the same structure that they were downloaded in, by default True
        """

        setattr(self, save_fn_name, save_fn)

        self.FILE_LIST_FILTERS[f'{name}'] = file_list_filter_fn
