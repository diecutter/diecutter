import base64
import json

from pyramid.exceptions import NotFound
import requests

from diecutter.resources import FileResource, DirResource


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

    def github_response(self, url):
        """Retrieve and return response from Github API.

        >>> from diecutter.github import GithubResource
        >>> res = GithubResource()
        >>> url = res.github_content_url(user='novagile',
        ...                              project='diecutter',
        ...                              commit='master',
        ...                              path='/demo/templates')
        >>> response = res.github_response(url)
        >>> response.status_code
        200

        """
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise e
        if response.status_code == 404:
            raise NotFound(url)
        return response

    def github_content_url(self, user, project, commit, path):
        """Return URL of content on Github API.

        >>> from diecutter.github import GithubResource
        >>> res = GithubResource()
        >>> res.github_content_url('novagile', 'diecutter', 'master', '/demo')
        u'https://api.github.com/repos/novagile/diecutter/contents/demo?ref=master'

        """
        return u'https://api.github.com/repos/{user}/{project}/contents/' \
               u'{path}?ref={commit}'.format(user=user,
                                             project=project,
                                             path=path.lstrip('/'),
                                             commit=commit)

    def github_tree_url(self, user, project, commit):
        """Return URL of tree on Github API.

        >>> from diecutter.github import GithubResource
        >>> res = GithubResource()
        >>> res.github_tree_url('novagile', 'diecutter', 'master')
        u'https://api.github.com/repos/novagile/diecutter/git/trees/master?recursive=1'

        """
        return u'https://api.github.com/repos/{user}/{project}/git/trees/' \
               u'{commit}?recursive=1'.format(user=user,
                                              project=project,
                                              commit=commit)

    def is_file(self, path):
        """Return True if resource is a file.

        >>> from diecutter.github import GithubResource
        >>> res = GithubResource()
        >>> res.is_file('/novagile/diecutter/master/demo/templates')
        False
        >>> res.is_file('/novagile/diecutter/master/README')
        True

        """
        user, project, commit, path = self.split_path(path)
        url = self.github_content_url(user, project, commit, path)
        response = self.github_response(url)
        data = json.loads(response.text)
        return 'content' in data


class GithubFileResource(GithubResource, FileResource):
    """A file resource that lives on Github."""
    @property
    def is_file(self):
        return super(GithubResource, self).is_file

    def read(self):
        """Return file contents.

        >>> from diecutter.github import GithubFileResource
        >>> res = GithubFileResource('/novagile/diecutter/master/demo/'
        ...                          'templates/greetings.txt')
        >>> print res.read()
        {{ greetings|default('Hello') }} {{ name }}!
        <BLANKLINE>

        """
        user, project, commit, path = self.split_path(self.path)
        url = self.github_content_url(user, project, commit, path)
        response = self.github_response(url)
        data = json.loads(response.text)
        try:
            content = data['content']
        except KeyError:
            raise Exception('Not a file')
        if data['encoding'] == 'base64':
            content = unicode(base64.b64decode(content))
        else:
            raise Exception('Unsupported encoding %s' % data['encoding'])
        return content


class GithubDirResource(GithubResource, DirResource):
    """A directory resource that lives on Github."""
    @property
    def exists(self):
        """Return True if resource exists.

        >>> from diecutter.github import GithubDirResource
        >>> res = GithubDirResource('/novagile/diecutter/master/demo/templates')
        >>> res.exists
        True
        >>> res = GithubDirResource('/novagile/diecutter/master/fake')
        >>> res.exists
        False

        """
        user, project, commit, path = self.split_path(self.path)
        url = self.github_content_url(user, project, commit, path)
        try:
            self.github_response(url)
        except NotFound:
            return False
        return True

    @property
    def content_type(self):
        return 'application/zip'

    def relative_filename(self, filename):
        """Return filename relative to :py:attr:`path`."""
        if filename.startswith(self.path):
            return filename[len(self.path):].lstrip('/')
        return filename

    def read_tree(self):
        """Generate list of paths to contained resources.

        >>> from diecutter.github import GithubDirResource
        >>> res = GithubDirResource('/novagile/diecutter/master/demo/templates/'
        ...                         'dynamic-tree')
        >>> list(res.read_tree())
        [u'/novagile/diecutter/master/demo/templates/dynamic-tree/.diecutter-tree', u'/novagile/diecutter/master/demo/templates/dynamic-tree/greeter.txt']

        """
        user, project, commit, path = self.split_path(self.path)
        url = self.github_tree_url(user, project, commit)
        response = self.github_response(url)
        data = json.loads(response.text)
        for item in data['tree']:
            if item['type'] == u'blob':
                if item['path'].startswith(path):
                    yield u'/'.join([u'', user, project, commit, item['path']])

    def get_file_resource(self, path):
        """Factory for internal FileResources."""
        file_path = u'/'.join(self.path.rstrip(u'/'), path.lstrip(u'/'))
        return GithubFileResource(file_path, self.engine)
