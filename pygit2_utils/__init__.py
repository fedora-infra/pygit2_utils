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


class GitRepo(object):

    def __init__(self, path):
        """ Constructor of the GitRepo class.

        :arg path: the path of the git repo on the filesystem. If not
            provided.

        """
        self.path = path
        self.repository = pygit2.Repository(self.path)
        self.config = self.repository.config

        # If there is a local config, use it
        potential_config = os.path.join(self.path, '.git', 'config')
        if os.path.isfile(potential_config):
            self.config.add_file(potential_config)

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

    @property
    def current_branch(self):
        """ Return the name of the current branch checked-out.

        """
        head = self.repository.head

        return head.name.replace('refs/heads/', '')

    @property
    def remote_current_branch(self):
        """ Return the name of the remove of the current branch checked-out.

        """
        branch = self.repository.lookup_branch(
            self.repository.head.name.replace('refs/heads/', ''))
        if branch.upstream:
            return branch.upstream_name.replace('refs/remotes/', '')

    @property
    def files_changed(self):
        """ Return the list of files that are tracked in git and changed
        locally.

        """
        status = self.repository.status()
        files = []
        for filepath, flag in status.items():
            if (flag & pygit2.GIT_STATUS_WT_MODIFIED) \
                    or (flag & pygit2.GIT_STATUS_WT_DELETED):
                files.append(filepath)
        return files

    @property
    def files_untracked(self):
        """ Return the list of files that are not tracked in git but present
        locally.

        """
        status = self.repository.status()
        files = []
        for filepath, flag in status.items():
            if flag & pygit2.GIT_STATUS_WT_NEW:
                files.append(filepath)
        return files

    def commit(self, message, files):
        """ Commmit the specified list of files with the provided commit
        message.

        :arg message: the message to use in the git commit
        :type message: str
        :arg files: the list of files to include in the commit
        :type files: list(str)
        :return: a `pygit2.Oid` object corresponding to the commit made
        :rtype: pygit2.Oid

        """
        # Let's be careful about what we get
        if not isinstance(files, list):
            files = [files]

        for filename in files:
            self.repository.index.add(filename)
        self.repository.index.write()
        tree = self.repository.index.write_tree()

        # Set variables needed for the commit
        author = pygit2.Signature(
            self.config.get_multivar('user.name')[0],
            self.config.get_multivar('user.email')[0],
        )
        parent = self.repository.revparse_single('HEAD').oid.hex

        # Do the commit
        commit = self.repository.create_commit(
            # the name of the reference to update
            self.repository.head.name,
            author,
            author,
            message,
            # binary string representing the tree object ID
            tree,
            # list of binary strings representing parents of the new commit
            [parent]
        )

        return commit
