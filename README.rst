GWLandscape Python API
==================

`GWLandscape <https://gwlandscape.org.au/>`_ is a service used to handle both the submission of COMPAS jobs (todo)

Check out the `documentation <https://gwlandscape-python.readthedocs.io/en/latest/>`_ for more information.

Installation
------------

The gwlandscape-python package can be installed with

::

    pip install gwlandscape-python


Example
-------

::

    >>> from gwlandscape_python import GWLandscape
    >>> gwc = GWLandscape(token='<user_api_token_here>')
    >>> job = gwc.get_preferred_job_list()[0]
    >>> job.save_corner_plot_files()

    100%|██████████████████████████████████████| 3.76M/3.76M [00:00<00:00, 5.20MB/s]
    All 2 files saved!
