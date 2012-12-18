#########
Diecutter
#########

An API service that will give you back a configuration file from a template and variables.


USAGE
=====

Put your template in the service templates directory or use the API::

    $ curl -X PUT http://diecutter.local/template_name.ini -F "file=@local/path/to/template_file.ini" -F "token=CONFIGURED_TOKEN"

Then to see the template, ask for it::

    $ curl http://diecutter.local/template_name.ini
    Received "{{ variable }}"

To render a template with some variables::

    curl -X POST http://diecutter.local/template_name.ini -d '{"variable": "toto"}' -H "Content-Type: application/json"
    Received "toto"

    curl -X POST http://diecutter.local/template_name.ini -d 'variable=toto'
    Received "toto"
