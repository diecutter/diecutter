#########
Diecutter
#########

An API service that will give you back a configuration file from a template and variables.


*****
Usage
*****

The project is at a really early stage, but you can try it already.

Install diecutter from Github and run the server:

.. code-block:: sh

   git clone git@github.com:novagile/diecutter.git
   cd diecutter/
   make develop
   make serve &

Check it works::

    $ curl http://localhost:8106
    {"diecutter": "Hello", "version": "0.1dev"}

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
