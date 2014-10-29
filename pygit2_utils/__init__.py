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

import pygit2_utils.exceptions


class GitRepo(object):

    def __init__(self, path):
        """ Constructor of the GitRepo class.

        :arg path: the path of the git repo on the filesystem. If not
            provided.

        """
        if not os.path.isdir(path):
            raise OSError(
                errno.ENOTDIR, '%s could not be found' % path)

        self.path = path
        self.repository = pygit2.Repository(self.path)
        self.config = self.repository.config

        # If there is a local config, use it
        potential_config = os.path.join(self.path, '.git', 'config')
        if os.path.isfile(potential_config):
            self.config.add_file(potential_config)

    @classmethod
    def clone_repo(cls, url, dest_path, bare=False):
        """ Clone a git repo from the provided url at the specified dest_path.

        :arg url: the url of the git.
        :type url: str
        :arg dest_path: the path where to clone the git repo (including the
            name of the git repo itself, ie: if you clone foo in /home/bb/bar
            the dest_path will be /home/bb/bar/foo).
        :type dest_path: str
        :kwarg bare: a boolean specifying whether the cloned repo should be
            a bare repo or not
        :type bare: bool
        :return: a `GitRepo` object instanciated at the provided path
        :rtype: GitRepo
        :raises OSError: raised when the directory where is cloned the repo
            exists and is not empty
        :raises pygit2.GitError: raised then the url provided is invalid

        """

        if os.path.exists(dest_path):
            raise OSError(
                errno.EEXIST, '%s exists and is not empty' % dest_path)

        pygit2.clone_repository(url, dest_path, bare=bare)

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

    def diff(self, commitid1=None, commitid2=None):
        """ Returns the diff of commit(s).

        If no commits are given, the method returns the diff between HEAD
        and the files that changed locally (just like a `git diff` in a git
        repo).
        If one commit is specified, the method returns the diff of the
        specified commit (like a `git log -p <commitid>` in a git repo).
        If two commits are specified, the method returns the diff between
        the two commits.

        :kwarg commitid1: hash of the first commit to use (the oldest one).
            Can be None.
        :type commitid1: str
        :kwarg commitid2: hash of the second commit to use (the most recent).
            Can be None
        :type commitid2: str
        :return: the diff of the specified commits or with the current HEAD.
        :rtype: str
        :raises ValueError: if a commit is provided and could not be found
            in the repo
        :raises KeyError: if two commits are provided and at least one of
            them could not be found in the repo

        """
        if commitid1 is None and commitid2 is None:
            diff = self.repository.diff()
        elif None in [commitid1, commitid2]:
            commitid = [
                el
                for el in [commitid1, commitid2]
                if el is not None
            ][0]
            commit = self.repository.get(commitid)
            if len(commit.parents) > 1:
                diff = ''
            elif len(commit.parents) == 1:
                parent = self.repository.revparse_single('%s^' % commitid)
                diff = self.repository.diff(parent, commit)
            else:
                # First commit in the repo
                diff = commit.tree.diff_to_tree(swap=True)
        else:
            t0 = self.repository.revparse_single(commitid1)
            t1 = self.repository.revparse_single(commitid2)
            diff = self.repository.diff(t0, t1)

        return diff

    def list_branches(self, status='all'):
        """ Return the list of branches of the repo.

        :kwarg status: flag used to specify if it should return all the
            branches, only the local or the remote ones.
            Can be: `all`, `local`, `remote`. Detaults: `all`.
        :type status: str
        :return: the list of branches corresponding to the status specified
        :rtype: list(str)
        :raises ValueError: when the status specified in not allowed

        """
        statuses = ['remote', 'local', 'all']
        if status not in statuses:
            raise ValueError('status is not in %s' % statuses)

        if status == 'remote':
            branches = self.repository.listall_branches(
                pygit2.GIT_BRANCH_REMOTE)
        elif status == 'local':
            branches = self.repository.listall_branches(
                pygit2.GIT_BRANCH_LOCAL)
        else:
            branches = self.repository.listall_branches(
                pygit2.GIT_BRANCH_REMOTE | pygit2.GIT_BRANCH_LOCAL)

        return branches

    def list_tags(self):
        """ Return the list of tags present in the repository.

        """
        tags = [
            ref.replace('refs/tags/', '')
            for ref in self.repository.listall_references()
            if ref.startswith('refs/tags')
        ]
        return tags

    def tag(self, tag, commitid=None, message=None):
        """ Add a tag to the repository.

        :arg tag: the tag to apply
        :type tag: str
        :kwarg commitid: the hash of the commit to tag. If not specified it
            will use HEAD. Defaults to None.
        :type commitid: str
        :kwarg message: the message to associate to this tag.
            Defaults to None
        :type message: str
        :return: the hash of the commit tagged
        :rtype: str

        """

        author = pygit2.Signature(
            self.config.get_multivar('user.name')[0],
            self.config.get_multivar('user.email')[0],
        )

        # Create the tag
        if commitid is None:
            commitid = self.repository.revparse_single('HEAD').oid.hex

        return self.repository.create_tag(
            tag, commitid, pygit2.GIT_OBJ_COMMIT, author, message or '')

    def checkout(self, branch_name):
        """ Checkout the specified branch

        :arg branch_name: the name of the branch to checkout
        :type branch_name: str
        :raises pygit2_utils.exceptions.NoSuchBranchError: when the branch
            cannot be found in the repository

        """
        branch = self.repository.lookup_branch(branch_name)
        if branch is None:
            raise exceptions.NoSuchBranchError()
        ref = self.repository.lookup_reference(branch.name)

        self.repository.checkout(ref)

    def head_of_branch(self, branch_name):
        """ Return the HEAD commit of the specified branch.

        :arg branch_name: the name of the branch to checkout
        :type branch_name: str
        :return: the `pygit2.Commit` found to be the HEAD of the specified
            branch
        :rtype: pygit2.Commit
        :raises pygit2_utils.exceptions.NoSuchBranchError: when the branch
            cannot be found in the repository

        """
        branch = self.repository.lookup_branch(branch_name)
        if branch is None:
            raise exceptions.NoSuchBranchError()
        ref = self.repository.lookup_reference(branch.name)
        return ref.get_object()
