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

"""
pygit2_utils module.

This module aims at providing a simple(r) interface to `pygit2
<http://www.pygit2.org/>`_. It does not mean to be a replacement for it, as
such it will contain some of but not all features that pygit2 offers.

"""

import datetime
import errno
import os

import pygit2

import pygit2_utils.exceptions


class GitRepo(object):
    """ Generic interface to a git repository. """

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

    def get_config(self, configkey):
        """ For a specified configuration key returned the value
        corresponding to the setting in the configuration of the repo.

        :arg configkey: the configuration key to search for
            (for example: "user.email" or "user.name")
        :type configkey: str
        :return: the setting corresponding to this key in the configuration
        :rtype: str
        """
        value = self.config.get_multivar(configkey)
        if isinstance(value, list):
            value = value[0]
        elif str(type(value)) == "<class "\
                "'pygit2.config.ConfigMultivarIterator'>":
            value = value.next()
        else:
            raise ('Unknown data format retrieved for %s: %s' % (
                configkey, type(value)))
        return value

    def commit(self, message, files, branch='master', username=None,
               useremail=None):
        """ Commmit the specified list of files with the provided commit
        message.

        :arg message: the message to use in the git commit
        :type message: str
        :arg files: the list of files to include in the commit
        :type files: list(str)
        :kwarg branch: the name of the branch to update. Defaults to `master`
        :type branch: str
        :kwarg username: the username to use for the commit
        :type username: str
        :kwarg useremail: the email address to use for the commit
        :type useremail: str
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
        if username is None:
            username = self.config.get_multivar('user.name')[0]
        if useremail is None:
            useremail = self.config.get_multivar('user.email')[0]

        author = pygit2.Signature(username, useremail)

        parent = None
        try:
            parent = self.repository.revparse_single('HEAD')
        except KeyError:
            pass

        parents = []
        if parent:
            parents.append(parent.oid.hex)

        ref = 'refs/heads/%s' % branch

        # Do the commit
        commit = self.repository.create_commit(
            # the name of the reference to update
            ref,
            author,
            author,
            message,
            # binary string representing the tree object ID
            tree,
            # list of binary strings representing parents of the new commit
            parents
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
        :raises ValueError: if a single commit id is provided but is too
            short
        :raises NoSuchRefError: if a single commit id is provided but does
            not correspond to any commit
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
            if commit is None:
                 raise pygit2_utils.exceptions.NoSuchRefError()
            if len(commit.parents) > 1:
                diff = ''
            elif len(commit.parents) == 1:
                parent = self.repository.revparse_single('%s^' % commitid)
                diff = self.repository.diff(parent, commit)
            else:
                # First commit in the repo
                diff = commit.tree.diff_to_tree(swap=True)
        else:
            c_t0 = self.repository.revparse_single(commitid1)
            c_t1 = self.repository.revparse_single(commitid2)
            diff = self.repository.diff(c_t0, c_t1)

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

        :arg branch_name: the name of the branch to checkout. It can be a
            local or remote branch, in the later case it has to be specified
            as <remote>/<branchname>
        :type branch_name: str
        :raises pygit2_utils.exceptions.NoSuchBranchError: when the branch
            cannot be found in the repository

        """
        # Check if the branch exists locally
        branch = self.repository.lookup_branch(
            branch_name, pygit2.GIT_BRANCH_LOCAL)
        # If we do not have a local branch, check if it is a remote one
        if branch is None:
            branch = self.repository.lookup_branch(
                branch_name, pygit2.GIT_BRANCH_REMOTE)
        # If it is not a local nor a remote, raise exception
        if branch is None:
            raise pygit2_utils.exceptions.NoSuchBranchError()

        ref = self.repository.lookup_reference(branch.name)

        self.repository.checkout(ref)

    def head_of_branch(self, branch_name):
        """ Return the HEAD commit of the specified branch.

        :arg branch_name: the name of the branch to checkout. It can be a
            local or remote branch, in the later case it has to be specified
            as <remote>/<branchname>
        :type branch_name: str
        :return: the `pygit2.Commit` found to be the HEAD of the specified
            branch
        :rtype: pygit2.Commit
        :raises pygit2_utils.exceptions.NoSuchBranchError: when the branch
            cannot be found in the repository

        """
        # Check if the branch exists locally
        branch = self.repository.lookup_branch(
            branch_name, pygit2.GIT_BRANCH_LOCAL)
        # If we do not have a local branch, check if it is a remote one
        if branch is None:
            branch = self.repository.lookup_branch(
                branch_name, pygit2.GIT_BRANCH_REMOTE)
        # If it is not a local nor a remote, raise exception
        if branch is None:
            raise pygit2_utils.exceptions.NoSuchBranchError()

        ref = self.repository.lookup_reference(branch.name)
        return ref.get_object()

    def add_remote(self, remote_name, remote_url):
        """ Add a remote to the git repository using the provided name and
        url.

        :arg remote_name: the name of the remote
        :type remote_name: str
        :arg remote_url: the url pointing to the remote
        :type remote_url: str
        :return: the remote created
        :rtype: pygit2.Remote

        """

        remote = self.repository.create_remote(remote_name, remote_url)

        return remote

    def get_patch(self, commit_ids):
        """ Return the patch formated as would `git-format patch` for one or
        more commits.

        For one or more commit hash in the git repo, returns a string
        representation of the changes the commit did in a format that allows
        it to be used as patch.

        :arg commit_ids: one or more commit hashes to return in a
            `git format-path` format thus compatible with `git am`.
        :type commit_ids: str or list(str)
        :return: the diff of the commits in a `git format-patch` format
        :rtype: str

        """

        if not isinstance(commit_ids, list):
            commit_ids = [commit_ids]

        patch = ""
        for cnt, commitid in enumerate(commit_ids):
            commit = self.repository.revparse_single(commitid)
            diff = self.diff(commit.oid.hex)

            subject = message = ''
            if '\n' in commit.message:
                subject, message = commit.message.split('\n', 1)
            else:
                subject = commit.message

            if len(commit_ids) > 1:
                subject = '[PATCH %s/%s] %s' % (
                    cnt + 1, len(commit_ids), subject)

            var = {
                'commit': commit.oid.hex,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'date': datetime.datetime.utcfromtimestamp(
                    commit.commit_time).strftime('%b %d %Y %H:%M:%S +0000'),
                'subject': subject,
                'msg': message,
                'patch': diff.patch,
            }

            patch += """From %(commit)s Mon Sep 17 00:00:00 2001
From: %(author_name)s <%(author_email)s>
Date: %(date)s
Subject: %(subject)s

%(msg)s
---

%(patch)s
""" % (var)
        return patch

    def merge(self, commitid, branch_name='master', message=None,
              username=None, useremail=None):
        """ Merge a specified commit into the specified branch of the repo.

        If the commit is ahead of the repo by more than one commits, all the
        commits in the pile will be merged.

        :arg commitid: the hash of the commit to merge in the specified
            branch of the repository
        :type commitid: str
        :arg branch_name: the name of the branch into which merge the
            specified commit. Can be the branch name itself, or its reference
            (ie: refs/heads/<branch_name>)
        :type branch_name: str
        :kwarg message: the message to use in the merge commit (in case
            fastforward is not an option)
        :type message: str
        :kwarg username: the username to use for the merge commit (if there
            is one)
        :type username: str
        :kwarg useremail: the email address to use for the merge commit (if
            there is one)
        :type useremail: str
        :raises pygit2_utils.exceptions.NothingToMergeError: when there is
            nothing to merge because the two branches are already up to date
        :raises pygit2_utils.exceptions.MergeConflictsError: when the merge
            cannot be done because of a conflict

        """
        if message is None:
            message = 'Merge %s into %s' % (commitid, branch_name)

        merge = self.repository.merge(commitid)
        try:
            branch_ref = self.repository.lookup_reference(
                branch_name).resolve()
        except ValueError:
            branch_ref = self.repository.lookup_reference(
                'refs/heads/%s' % branch_name).resolve()

        parent = self.repository.revparse_single('HEAD').oid.hex

        if username is None:
            username = self.config.get_multivar('user.name')[0]
        if useremail is None:
            useremail = self.config.get_multivar('user.email')[0]

        author = pygit2.Signature(username, useremail)

        sha = None
        if merge.is_uptodate:
            raise pygit2_utils.exceptions.NothingToMergeError()
        elif merge.is_fastforward:
            branch_ref.target = merge.fastforward_oid
            sha = merge.fastforward_oid
        else:
            self.repository.index.write()
            try:
                tree = self.repository.index.write_tree()
            except pygit2.GitError:
                raise pygit2_utils.exceptions.MergeConflictsError()
            sha = self.repository.create_commit(
                self.repository.head.name,
                author,
                author,
                message,
                tree,
                [parent, commitid])

        return sha
