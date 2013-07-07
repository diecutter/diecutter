import os
import tempfile

from diecutter.resources import FileResource, DirResource
from diecutter.tests import temporary_directory
from diecutter.views import LocalService


def execute(command):
    import subprocess
    process = subprocess.Popen(command,
                               stdin=None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=False)
    return (process.wait(), process.stdout.read(), process.stderr.read())


class GithubResource(object):
    """Base class for Github resources."""
    def split_path(self, path):
        """Return parts of path of the form /{user}/{project}/{commit}/{path}.

        >>> from diecutter.github import GithubResource
        >>> res = GithubResource()
        >>> res.split_path('/user/project/commit/path')
        ['user', 'project', 'commit', 'path']
        >>> res.split_path('/user/project/commit/nested/path')
        ['user', 'project', 'commit', 'nested/path']

        """
        return path.lstrip('/').split('/', 3)

    def github_checkout(self, user, project, commit, output_dir=None):
        """Return path to local checkout of remote repository."""
        try:
            return self._checkout
        except AttributeError:
            if output_dir is None:
                output_dir = tempfile.mkdtemp()
            self.github_clone(user, project, output_dir)
            command = ['git', 'checkout', commit]
            previous_dir = os.getcwd()
            os.chdir(output_dir)
            try:
                code, stdout, stderr = execute(command)
            finally:
                os.chdir(previous_dir)
            self._checkout = output_dir
            return self._checkout

    def github_clone(self, user, project, output_dir):
        """Clone repository locally over ssh in ``output_dir``."""
        command = ['git', 'clone', '--no-checkout',
                   self.github_clone_url(user, project),
                   output_dir]
        code, stdout, stderr = execute(command)

    def github_clone_url(self, user, project):
        """Return URL to clone from github."""
#        return '/home/benoit/web/diecutter/'
        return 'git@github.com:{user}/{project}.git'.format(user=user,
                                                            project=project)


class GithubFileResource(GithubResource, FileResource):
    """A file resource that lives on Github.

    >>> from diecutter.github import GithubFileResource
    >>> from diecutter.tests import temporary_directory
    >>> with temporary_directory() as working_dir:
    ...     res = GithubFileResource(
    ...         '/novagile/diecutter/967556784a99d593120718c222051d8b4766e176/demo/templates/greetings.txt',
    ...         local_dir=working_dir)
    ...     res.exists
    ...     res.is_file
    ...     print res.read()
    True
    True
    {{ greetings|default('Hello') }} {{ name }}!
    <BLANKLINE>

    """
    def __init__(self, path='', engine=None, filename_engine=None,
                 local_dir=None):
        self.remote_path = path
        user, project, commit, relative_path = self.split_path(path)
        local_dir = GithubResource.github_checkout(
            self, user, project, commit, local_dir)
        local_path = os.path.join(local_dir, relative_path)
        FileResource.__init__(self, local_path, engine, filename_engine)


class GithubDirResource(GithubResource, DirResource):
    """A directory resource that lives on Github.

    >>> from diecutter.github import GithubDirResource
    >>> from diecutter.tests import temporary_directory
    >>> with temporary_directory() as working_dir:
    ...     res = GithubDirResource('/novagile/diecutter/967556784a99d593120718c222051d8b4766e176/demo/templates/dynamic-tree/',
    ...         local_dir=working_dir)
    ...     res.exists
    ...     res.is_dir
    ...     print res.read()
    True
    True
    .diecutter-tree
    greeter.txt

    """
    def __init__(self, path='', engine=None, filename_engine=None,
                 local_dir=None):
        self.remote_path = path
        user, project, commit, relative_path = self.split_path(path)
        local_dir = GithubResource.github_checkout(
            self, user, project, commit, local_dir)
        local_path = os.path.join(local_dir, relative_path)
        DirResource.__init__(self, local_path, engine, filename_engine)


class GithubService(LocalService):
    """A diecutter service that uses Github as template storage."""
    def get(self, request):
        with temporary_directory() as checkout_dir:
            self.checkout_dir = checkout_dir
            return super(GithubService, self).get(request)

    def post(self, request):
        with temporary_directory() as checkout_dir:
            self.checkout_dir = checkout_dir
            return super(GithubService, self).post(request)

    def put(self, request):
        raise NotImplementedError()

    def get_resource(self, request):
        """Return the resource matching request.

        Return value is a :py:class:`GithubFileResource` or
        :py:class`GithubDirResource`.

        """
        path = self.get_resource_path(request)
        engine = self.get_engine(request)
        filename_engine = self.get_filename_engine(request)
        res = GithubResource()
        user, project, commit, relative_path = res.split_path(path)
        res.github_checkout(user, project, commit, output_dir=self.checkout_dir)
        local_path = os.path.join(self.checkout_dir, relative_path)
        if os.path.isdir(local_path):
            resource = GithubDirResource(path=path, engine=engine,
                                         filename_engine=filename_engine)
        else:
            resource = GithubFileResource(path=path, engine=engine,
                                          filename_engine=filename_engine)
        resource._checkout = self.checkout_dir
        return resource

    def get_resource_path(self, request):
        """Return validated (absolute) resource path from request."""
        return request.matchdict['template_path']
