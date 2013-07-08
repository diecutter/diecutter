"""Manage templates located on Github."""
import os
import tarfile

from pyramid.exceptions import NotFound
import requests

from diecutter.resources import FileResource, DirResource
from diecutter.utils import temporary_directory, execute
from diecutter.views import LocalService


class GithubLoader(object):
    """Loads resources from Github."""
    def __init__(self, checkout_dir):
        self.checkout_dir = checkout_dir

    def get_resource(self, engine, filename_engine, user, project, commit,
                     path):
        """Return resource (either a file or directory)."""
        local_root = self.github_targz(user, project, commit)
        local_path = os.path.join(local_root,
                                  '{project}-{commit}'.format(project=project,
                                                              commit=commit),
                                  path)
        if os.path.isdir(local_path):
            resource = DirResource(path=local_path, engine=engine,
                                   filename_engine=filename_engine)
        else:
            resource = FileResource(path=local_path, engine=engine,
                                    filename_engine=filename_engine)
        return resource

    def github_checkout(self, user, project, commit):
        """Return path to local checkout of remote repository."""
        try:
            return self._checkout
        except AttributeError:
            self.github_clone(user, project, self.checkout_dir)
            command = ['git', 'checkout', commit]
            previous_dir = os.getcwd()
            os.chdir(self.checkout_dir)
            try:
                code, stdout, stderr = execute(command)
            finally:
                os.chdir(previous_dir)
            self._checkout = self.checkout_dir
            return self._checkout

    def github_clone(self, user, project):
        """Clone repository locally over ssh in ``self.checkout_dir``."""
        command = ['git', 'clone', '--no-checkout',
                   self.github_clone_url(user, project),
                   self.checkout_dir]
        code, stdout, stderr = execute(command)

    def github_clone_url(self, user, project):
        """Return URL to clone from github.

        >>> from diecutter.github import GithubLoader
        >>> from diecutter.utils import temporary_directory
        >>> with temporary_directory() as temp_dir:
        ...     loader = GithubLoader(temp_dir)
        ...     loader.github_clone_url('user', 'project')
        'git@github.com:user/project.git'

        """
        return 'git@github.com:{user}/{project}.git'.format(user=user,
                                                            project=project)

    def github_targz(self, user, project, commit):
        """Download archive from Github and return path to local extract."""
        try:
            return self._checkout
        except AttributeError:
            url = self.github_targz_url(user, project, commit)
            try:
                response = requests.get(url, stream=True)
            except requests.exceptions.RequestException as e:
                raise e
            if response.status_code == 404:
                raise NotFound()
            archive = tarfile.open(fileobj=response.raw, mode='r|gz')
            archive.extractall(self.checkout_dir)
            self._checkout = self.checkout_dir
            return self._checkout

    def github_targz_url(self, user, project, commit):
        """Return URL of Github archive.

        >>> from diecutter.github import GithubLoader
        >>> from diecutter.utils import temporary_directory
        >>> with temporary_directory() as temp_dir:
        ...     loader = GithubLoader(temp_dir)
        ...     loader.github_targz_url('user', 'project', 'master')
        'https://github.com/user/project/archive/master.tar.gz'

        """
        return 'https://github.com/{user}/{project}/archive/{commit}.tar.gz' \
               .format(user=user, project=project, commit=commit)


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

    def split_path(self, path):
        """Return parts of path of the form /{user}/{project}/{commit}/{path}.

        >>> from diecutter.github import GithubService
        >>> service = GithubService()
        >>> service.split_path('/user/project/commit/path')
        ['user', 'project', 'commit', 'path']
        >>> service.split_path('/user/project/commit/nested/path')
        ['user', 'project', 'commit', 'nested/path']

        """
        return path.lstrip('/').split('/', 3)

    def get_resource_loader(self, request):
        """Return :py:class:`GithubLoader` instance."""
        return GithubLoader(self.checkout_dir)

    def get_resource(self, request):
        """Return the resource matching request.

        Return value is a :py:class:`GithubFileResource` or
        :py:class`GithubDirResource`.

        """
        path = self.get_resource_path(request)
        user, project, commit, relative_path = self.split_path(path)
        engine = self.get_engine(request)
        filename_engine = self.get_filename_engine(request)
        resource_loader = self.get_resource_loader(request)
        resource = resource_loader.get_resource(
            engine, filename_engine, user, project, commit, relative_path)
        return resource

    def get_resource_path(self, request):
        """Return validated (absolute) resource path from request."""
        return request.matchdict['template_path']
