#########
Diecutter
#########

An API service that will give you back a configuration file from a template and variables.


*****
Usage
*****

The project is at a really early stage, but you can try it already.


Install
=======

Install diecutter from Github, configure it then run the server:

.. code-block:: sh

   # Download and install (in a virtualenv if you like).
   pip install -e git+git@github.com:novagile/diecutter.git#egg=diecutter
   # Configure: adapt "YOUR_TEMPLATE_DIR"!
   wget -O diecutter.ini --post-data "template_dir=YOUR_TEMPLATE_DIR" http://diecutter.alwaysdata.net/diecutter.ini
   # Run the server.
   pserve diecutter.ini --reload

Check it works::

    $ curl http://localhost:8106
    {"diecutter": "Hello", "version": "0.1dev"}


Files
=====

Put your template in the service templates directory or use the API::

    $ echo "Hello {{ who }}" | curl -X PUT http://localhost:8106/hello -F "file=@-"
    {"diecutter": "Ok"}

Then we can get the raw template we just created::

    $ curl http://localhost:8106/hello
    Hello {{ who }}

And we can render the template against some variables::

    $ curl -X POST http://localhost:8106/hello -d 'who=world'
    Hello world

Or the same with some JSON input::

    $ curl -X POST http://localhost:8106/hello -d '{"who": "world"}' -H "Content-Type: application/json"
    Hello world


Directories
===========

You can also get directories::
    
    $ echo "circus.ini" | curl -X PUT http://localhost:8106/circus/circus.ini -F "file=@-"
    {"diecutter": "Ok"}
    
    $ echo "circus_django.ini" | curl -X PUT http://localhost:8106/circus/circus_django.ini -F "file=@-"
    {"diecutter": "Ok"}

    $ curl http://localhost:8106/circus
    circus/circus.ini
    circus/circus_django.ini

    $ curl http://localhost:8106/circus/
    circus.ini
    circus_django.ini


If you want to render the directory against a global context::

    $ curl -X POST http://localhost:8106/circus
    /-- Get a ZIP archive with all the files listed below rendered against the context --/

    $ mkdir -p ~/sandbox/
    $ cd ~/sandbox/
    $ curl -X POST http://localhost:8106/circus > circus.zip
    $ unzip circus.zip
    $ tree .
    .
    ├── circus
    │   ├── circus_django.ini
    │   └── circus.ini
    └── circus.zip
    
    1 directory, 3 files


Render file names
=================

Sometimes you want to define names from the context.

You just add to put ``+context_name+`` it will match automatically::

     $ echo "[watcher:{{ watcher_name }}]" | curl -X PUT http://localhost:8106/circus/circus_+watcher_name+.ini -F "file=@-"
     {"diecutter": "Ok"}
 
     $ curl http://localhost:8106/circus
     circus/circus.ini
     circus/circus_django.ini
     circus/circus_+watcher_name+.ini
 
    $ curl http://localhost:8106/circus -d 'watcher_name=diecutter' > circus.zip
    $ unzip -l circus.zip
    Archive:  circus.zip
      Length      Date    Time    Name
    ---------  ---------- -----   ----
           10  2012-12-24 12:02   circus/circus.ini
           19  2012-12-24 12:02   circus/circus_diecutter.ini
           17  2012-12-24 12:02   circus/circus_django.ini
    ---------                     -------
           46                     3 files
    $ cat circus/circus_diecutter.ini
    [watcher:diecutter]

A full example : the diecutter django_admin.py startproject
===========================================================

As an example, we added a +django_project+ template that you can use like this::

    $ curl http://localhost:8106/+django_project+ -d 'django_project=diecutter_demo' > diecutter_demo.zip
    $ unzip -l diecutter_demo.zip
    Archive:  diecutter_demo.zip
      Length      Date    Time    Name
    ---------  ---------- -----   ----
          256  2012-12-24 12:08   diecutter_demo/manage.py
            0  2012-12-24 12:08   diecutter_demo/diecutter_demo/__init__.py
         5239  2012-12-24 12:08   diecutter_demo/diecutter_demo/settings.py
          579  2012-12-24 12:08   diecutter_demo/diecutter_demo/urls.py
         1149  2012-12-24 12:08   diecutter_demo/diecutter_demo/wsgi.py
    ---------                     -------
         7223                     5 files
