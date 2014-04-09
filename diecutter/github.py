# -*- coding: utf-8 -*-
"""Manage templates located on Github."""
from piecutter.loaders.github import GithubLoader

from piecutter.utils import temporary_directory
from diecutter.local import LocalService


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
        try:
            user, project, commit, relative_path = self.split_path(path)
        except:
            # favicon.ico request.
            return
        engine = self.get_engine(request)
        filename_engine = self.get_filename_engine(request)
        resource_loader = self.get_resource_loader(request)
        resource = resource_loader.get_resource(
            engine, filename_engine, user, project, commit, relative_path)
        return resource

    def get_resource_path(self, request):
        """Return validated (absolute) resource path from request."""
        return request.matchdict['template_path']
