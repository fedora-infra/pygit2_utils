# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import errno

import pygit2


class GitConfig(object):
    """ Generic class to access the git configuration. """

    def __init__(self, config=None, repopath=None):
        """ Constructor of the GitConfig class.

        :kwarg config: path to a git configuration file.
        :type config: str
        :kwarg repopath: path to a local git

        """
        if config is None:
            if os.path.join('~', '.gitconfig'):
                config = os.path.expanduser(
                    os.path.join('~', '.gitconfig'))
            else:
                config = os.path.expanduser(
                    os.path.join('~', '.config', 'git', 'config'))

        configs = []
        if config:
            configs.append(config)
        if repopath is not None:
            configs.append(os.path.join(repopath, '.git', 'config'))

        self.config = configparser.ConfigParser()
        self.config.read(configs)

    def get(self, section, option):
        """ Returned a specfic option in a specified section.

        ini file have the basic structure:
            [section]
            option = value
        for example:
            [user]
            name = foo
            email = foo@bar.com

        With the present method you can do obj.get('user', 'name') to
        retrieve `foo`.

        :arg section: the name of the section to query
        :type section: str
        :arg option: the name of the option to retrieve in the specified
            section
        :type section: str
        :return: the value of the option in the specified section
        :rtype: str or int
        :raises configparser.NoSectionError: if the section asked could not
            be found
        :raises configparser.NoOptionError: if the option asked could not
            be found in the specified section

        """
        return self.config.get(section, option)

    def get_user(self):
        """ Utility method to retrieve the user as desired for a commit in
        git.
        For example will return: foo <foo@bar.com>

        :return: the string of the user and his/her email as desired for a
            commit in git
        :rtype: str

        """
        tmpl = '%(name)s <%(email)s>'
        return tmpl % dict(
            name=self.get('user', 'name'),
            email=self.get('user', 'email')
        )


class GitRepo(object):

    def __init__(self, path):
        """ Constructor of the GitRepo class.

        :arg path: the path of the git repo on the filesystem. If not
            provided.

        """
        self.path = path

    @classmethod
    def clone_repo(cls, url, dest_path):
        """ Clone a git repo from the provided url at the specified dest_path.

        :arg url: the url of the git.
        :type url: str
        :arg dest_path: the path where to clone the git repo (including the
            name of the git repo itself, ie: if you clone foo in /home/bb/bar
            the dest_path will be /home/bb/bar/foo).
        :type dest_path: str
        :return: a `GitRepo` object instanciated at the provided path
        :rtype: GitRepo
        :raises OSError: raised when the directory where is cloned the repo
            exists and is not empty
        :raises pygit2.GitError: raised then the url provided is invalid

        """

        if os.path.exists(dest_path):
            raise OSError(
                errno.EEXIST, '%s exists and is not empty' % dest_path)

        pygit2.clone_repository(url, dest_path, bare=False)

        return cls(path=dest_path)
