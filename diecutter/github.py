import os
import tempfile

from diecutter.resources import FileResource, DirResource


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
