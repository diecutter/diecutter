#########
Diecutter
#########

An API service that will give you back a configuration file from a template and variables.

The project is at a really early stage, but you can try it already.


*******
Install
*******

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


*****
Files
*****

Put your template in the service templates directory or use the API::

    $ echo "Hello {{ who }}" | curl -X PUT http://localhost:8106/hello -F "file=@-"
    {"diecutter": "Ok"}

Then we can get the raw template we just created::

    $ curl http://localhost:8106/hello
    Hello {{ who }}

And we can render the template against some variables::

    $ curl -X POST http://localhost:8106/hello -d 'who=world'
    Hello world


***********
Directories
***********

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


******************
Posting input data
******************

When you perform POST requests on resources, you provide a context, i.e.
variables and values.

Diecutter has builtin support for the following input content-types:

* "application/x-www-form-urlencoded": the default when you perform POST
  requests with ``wget`` or ``curl``.
  See http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.1

* "application/json": JSON encoded data. See http://json.org/.

* "text/plain": INI-style plain text files. See
  https://en.wikipedia.org/wiki/INI_file and
  http://docs.python.org/2.7/library/configparser.html.

Diecutter expects data to be provided as the body of the request.
"multipart/form-data" requests aren't supported currently.

Here are "flat" examples using ``curl``.

.. code-block:: sh

   # All examples below return the same result.

   # Default (implicit application/x-www-form-urlencoded content type).
   curl -X POST -d 'who=world' http://localhost:8106/hello

   # Explicit "application/x-www-form-urlencoded" content-type.
   curl -X POST -d 'who=world' -H "Content-Type: application/x-www-form-urlencoded" http://localhost:8106/hello

   # JSON.
   curl -X POST -d '{"who": "world"}' -H "Content-Type: application/json" http://localhost:8106/hello

   # INI.
   curl -X POST -d 'who=world' -H "Content-Type: text/plain" http://localhost:8106/hello

.. note:: Pass content of a file using ``@`` in curl's ``-d`` option.

INI content-type allows you to provide 2 levels of data:

.. code-block:: sh

   cat > input.ini <<EOF
   hello = world
   [foo]
   bar = baz
   EOF
   curl -X POST --data-binary '@input.ini' -H "Content-Type: text/plain" http://localhost:8106/hello
   # Templates can use variables like {{ hello }} and {{ foo.bar }}.

JSON allows you to provide multiple levels of data.


*****************
Render file names
*****************

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


***********************************************************
A full example : the diecutter django_admin.py startproject
***********************************************************

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
