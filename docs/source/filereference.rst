FileReference class
===================

FileReference objects are used to bundle together the file path, size and download token of a specific file.
They are typically automatically created and placed in a FileReferenceList by methods of classes inheriting from GWDCObjectBase.


.. autoclass:: gwdc_python.files.file_reference.FileReference
    :members:
    :undoc-members:
    :show-inheritance:

FileReferenceList class
=======================

FileReferenceList objects bundle together many FileReference objects, allowing simpler downloading and filtering of multiple files.
As with FileReference objects, FileReferenceList objects are normally created by other methods.

.. autoclass:: gwdc_python.files.file_reference.FileReferenceList
    :members:
    :undoc-members:
    :show-inheritance:
