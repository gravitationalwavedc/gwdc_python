JobMeta class
=============

This metaclass is using to dynamically create three methods, based on the class attribute `FILE_LIST_FILTERS`.
`FILE_LIST_FILTERS` should be a dict with values being a function that can filter a FileReferenceList, and keys describing which files the filter finds.
More info is available in the :meth:`~gwdc_python.jobs.meta.JobMeta.register_file_list_filter` method.


.. autoclass:: gwdc_python.jobs.meta.JobMeta
    :members:
    :undoc-members:
    :show-inheritance:

JobBase class
=============

The JobBase class contains the JobMeta metaclass, and adds a generic initilisation method, along with some other helpful methods.

.. autoclass:: gwdc_python.jobs.base.JobBase
    :members:
    :undoc-members:
    :show-inheritance:
