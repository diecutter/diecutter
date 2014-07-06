.. note::

   In the examples below, let's communicate with a `diecutter` server using
   Python `requests <http://docs.python-requests.org>`_.

   This `diecutter` serves `diecutter's demo templates
   <https://github.com/diecutter/diecutter/tree/master/demo/templates>`_.

   The ``diecutter_url`` variable holds root URL of `diecutter` service, i.e.
   something like http://diecutter.io/api/.

.. testsetup::

   import os
   import shutil
   import tempfile

   import requests

   import testserver  # See ``doctest_path`` in :file:`docs/conf.py`.


   # Copy demo template in a temporary directory.
   diecutter_template_dir = tempfile.mkdtemp()
   shutil.rmtree(diecutter_template_dir)  # Required for shutil.copytree.
   shutil.copytree(testserver.demo_template_dir(), diecutter_template_dir)

   # Start a local server.
   diecutter_server = testserver.demo_server(diecutter_template_dir)
   diecutter_url = diecutter_server.application_url

.. testcleanup::

   diecutter_server.shutdown()
   shutil.rmtree(diecutter_template_dir)
