#########
diecutter
#########

`diecutter` is a web application around file generation:

* templates are the resources ;

* the most common operation is to **POST data to templates in order to retrieve
  generated files**.

`diecutter` can render single files and directories. Directories are rendered
as archives.


*******
Example
*******

``GET`` raw content of a template:

.. code-block:: text

   $ curl -X GET http://diecutter.io/api/greetings.txt
   {{ greetings|default('Hello') }} {{ name }}!

``POST`` data to the template and retrieve generated content:

.. code-block:: text

   $ curl -X POST -d name=world http://diecutter.io/api/greetings.txt
   Hello world!


**************
Project status
**************

Although under active development, `diecutter` already works, so `give it a
try! <http://diecutter.io>`_.

Check `milestones <https://github.com/diecutter/diecutter/issues/milestones>`_
and `vision <https://diecutter.readthedocs.io/en/latest/about/vision.html>`_
for details about the future.

Also notice that `diecutter` is part of an ecosystem:

* `piecutter`_ is the core Python API. It provides stuff like template engines
  or template loaders.

* `diecutter` implements a WSGI application and REST interface on top of
  `piecutter`.

* `diecutter-index <https://github.com/diecutter/diecutter-index>`_ is a
  proof-of-concept project for an online template registry.

* http://diecutter.io is the SAAS platform running `diecutter` ecosystem.

See also `alternatives and related projects`_ section in documentation.


*********
Resources
*********

* Online demo: http://diecutter.io
* Documentation: http://diecutter.readthedocs.io
* PyPI page: http://pypi.python.org/pypi/diecutter
* Bugtracker: https://github.com/diecutter/diecutter/issues
* Changelog: https://diecutter.readthedocs.io/en/latest/about/changelog.html
* Roadmap: https://github.com/diecutter/diecutter/issues/milestones
* Code repository: https://github.com/diecutter/diecutter
* Continuous integration: https://travis-ci.org/diecutter/diecutter
* IRC Channel: irc://irc.freenode.net/#diecutter

.. _`piecutter`: https://pypi.python.org/pypi/piecutter
.. _`alternatives and related projects`:
   https://diecutter.readthedocs.io/en/latest/about/alternatives.html
