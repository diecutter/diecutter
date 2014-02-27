#########
diecutter
#########

Templates as a service.

``diecutter`` exposes an API where you manage templates as resources.
The most common operation is to **POST data to templates in order to retrieve
generated files**.

Files and directories are supported. Directories are rendered as archives.

.. note::

   Diecutter is under active development: some (killer) features have not been
   implemented yet, or they are not mature.
   Check `milestones <https://github.com/diecutter/diecutter/issues/milestones>`_
   and `vision <https://diecutter.readthedocs.org/en/latest/about/vision.html>`_
   for details.

   That said, features documented below actually work, so **give it a try!**

.. image:: https://secure.travis-ci.org/diecutter/diecutter.png?branch=master
   :alt: Build Status
   :target: https://secure.travis-ci.org/diecutter/diecutter
.. image:: https://pypip.in/v/diecutter/badge.png
   :target: https://python.org/pypi/diecutter/
.. image:: https://pypip.in/d/diecutter/badge.png
   :target: https://python.org/pypi/diecutter/

*******
Example
*******

GET raw content of a template:

.. code-block:: text

   $ curl -X GET http://diecutter.io/api/greetings.txt
   {{ greetings|default('Hello') }} {{ name }}!

POST data to the template and retrieve generated content:

.. code-block:: text

   $ curl -X POST -d name=world http://diecutter.io/api/greetings.txt
   Hello world!


**********
Ressources
**********

* Online demo: http://diecutter.io
* Documentation: http://diecutter.readthedocs.org
* PyPI page: http://pypi.python.org/pypi/diecutter
* Bugtracker: https://github.com/diecutter/diecutter/issues
* Changelog: https://diecutter.readthedocs.org/en/latest/about/changelog.html
* Roadmap: https://github.com/diecutter/diecutter/issues/milestones
* Code repository: https://github.com/diecutter/diecutter
* Continuous integration: https://travis-ci.org/diecutter/diecutter
