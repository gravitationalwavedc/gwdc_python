GWDCObjectMeta class
====================

This metaclass is using to dynamically create three methods, based on the class attribute `FILE_LIST_FILTERS`.
`FILE_LIST_FILTERS` should be a dict with values being a function that can filter a FileReferenceList, and keys describing which files the filter finds.
More info is available in the :meth:`~gwdc_python.objects.meta.GWDCObjectMeta.register_file_list_filter` method.


.. autoclass:: gwdc_python.objects.meta.GWDCObjectMeta
    :members:
    :undoc-members:
    :show-inheritance:

GWDCObjectBase class
====================

The GWDCObjectBase class contains the GWDCObjectMeta metaclass, and adds a generic initilisation method, along with some other helpful methods.

.. autoclass:: gwdc_python.objects.base.GWDCObjectBase
    :members:
    :undoc-members:
    :show-inheritance:
