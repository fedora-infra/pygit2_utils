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
