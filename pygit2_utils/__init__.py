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

import os
import errno

import pygit2


class GitRepo(object):

    def __init__(self, name=None, path=None):
        """ Constructor of the GitRepo class.

        :kwarg name: the name of the git repo. If not provided will be
            computed automatically.
        :kward path: the path of the git repo on the filesystem. If not
            provided.

        """
        self._name = name
        self.path = path

    def clone_repo(self, url, dest_path=None):
        """ Clone a git repo from the provided url at the specified dest_path.

        :arg url: the url of the git.
        :type url: str
        :kwarg dest_path: the path where to clone the git repo.
        :type dest_path: str
        :return: None
        :raises OSError: raised when the directory where is cloned the repo
            exists and is not empty
        :raises pygit2.GitError: raised then the url provided is invalid

        """
        path = dest_path or self.path

        if os.path.exists(path):
            raise OSError(
                errno.EEXIST, '%s exists and is not empty' % path)

        pygit2.clone_repository(url, path, bare=False)
