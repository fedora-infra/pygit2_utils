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


import unittest
import sys
import os

import pygit2

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import pygit2_utils

from tests import BaseTests


class ScmTests(BaseTests):
    """ SCM tests. """

    def test_gitrepo(self):
        """ Test the pygit2_utils.GitRepo() constructor
        """

        repo_path = os.path.join(self.gitroot, 'test_repo')

        self.assertRaises(
            OSError,
            pygit2_utils.GitRepo,
            repo_path,

        )

    def test_clone_repo(self):
        """ Test the pygit2_utils.clone_repo to clone a repo """
        self.setup_git_repo()

        bare_repo_path = os.path.join(self.gitroot, 'test_repo.git')
        git_repo_path = os.path.join(self.gitroot, 'cloned_repo')

        # Fails: target exists
        self.assertRaises(
            OSError,
            pygit2_utils.GitRepo.clone_repo,
            bare_repo_path,
            self.gitroot
        )

        # Fails: url invalid
        self.assertRaises(
            pygit2.GitError,
            pygit2_utils.GitRepo.clone_repo,
            'foo',
            git_repo_path
        )

        # Works
        pygit2_utils.GitRepo.clone_repo(bare_repo_path, git_repo_path)

        self.assertTrue(
            os.path.exists(git_repo_path)
        )
        self.assertTrue(
            os.path.isdir(git_repo_path)
        )
        self.assertTrue(
            os.path.exists(os.path.join(git_repo_path, '.git'))
        )

    def test_current_branch(self):
        """ Test the pygit2_utils.GitRepo().current_branch returning the
        current branch
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        self.assertEqual(repo.current_branch, 'master')

        repo_path = os.path.join(self.gitroot, 'test_repo.git')
        repo = pygit2_utils.GitRepo(repo_path)

        self.assertEqual(repo.current_branch, 'master')

    def test_remote_current_branch(self):
        """ Test the pygit2_utils.GitRepo().remote_current_branch returning
        the remote of the current branch
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        self.assertEqual(repo.remote_current_branch, 'origin/master')

        repo_path = os.path.join(self.gitroot, 'test_repo.git')
        repo = pygit2_utils.GitRepo(repo_path)

        self.assertEqual(repo.remote_current_branch, None)

    def test_files_changed(self):
        """ Test the pygit2_utils.GitRepo().files_changed returning the
        list of files tracked that have changed locally
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        with open(os.path.join(repo_path, 'sources'), 'w') as stream:
            stream.write('\nBoo!!2')
        with open(os.path.join(repo_path, '.gitignore'), 'w') as stream:
            stream.write('boo!')
        with open(os.path.join(repo_path, 'bar'), 'w') as stream:
            stream.write('blah')

        self.assertEqual(
            sorted(repo.files_changed),
            ['.gitignore', 'sources']
        )

    def test_files_untracked(self):
        """ Test the pygit2_utils.GitRepo().files_untracked returning the
        list of files not tracked but present locally
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        with open(os.path.join(repo_path, 'sources'), 'w') as stream:
            stream.write('\nBoo!!2')
        with open(os.path.join(repo_path, 'bar'), 'w') as stream:
            stream.write('blah')

        self.assertEqual(
            repo.files_untracked,
            ['bar']
        )

    def test_commit(self):
        """ Test the pygit2_utils.GitRepo().commit returning the commit
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        repo_obj = pygit2.Repository(repo_path)

        # Check before commit that the commit we do, does not already exist
        commit = repo_obj.get(repo_obj.revparse_single('HEAD').oid.hex)
        self.assertNotEqual(commit.message, 'Commit from the tests')
        self.assertNotEqual(commit.author.name, 'foo')
        self.assertNotEqual(commit.author.email, 'foo@bar.com')

        with open(os.path.join(repo_path, 'sources'), 'w') as stream:
            stream.write('\nBoo!!2')

        # Commit with a list of (one) file
        commitid = repo.commit('Commit from the tests', ['sources'])

        # Check that the commitid returned has an .hex attribute that is a
        # string
        self.assertTrue(isinstance(commitid.hex, str))

        # Check the latest commit has the same hash as the commitid returned
        self.assertEqual(
            commitid.hex,
            repo_obj.revparse_single('HEAD').oid.hex
        )

        # Check the information of the latest commit
        commit = repo_obj.get(repo_obj.revparse_single('HEAD').oid.hex)

        self.assertEqual(commit.message, 'Commit from the tests')
        self.assertEqual(commit.author.name, 'foo')
        self.assertEqual(commit.author.email, 'foo@bar.com')

        with open(os.path.join(repo_path, 'sources'), 'w') as stream:
            stream.write('\nBoo!!2')

        # Commit with a single file
        commitid = repo.commit(
            'Commit from the tests', 'sources',
            username='bar', useremail='bar@foo.com')

        # Check that the commitid returned has an .hex attribute that is a
        # string
        self.assertTrue(isinstance(commitid.hex, str))

        # Check the latest commit has the same hash as the commitid returned
        self.assertEqual(
            commitid.hex,
            repo_obj.revparse_single('HEAD').oid.hex
        )

        # Check the information of the latest commit
        commit = repo_obj.get(repo_obj.revparse_single('HEAD').oid.hex)

        self.assertEqual(commit.message, 'Commit from the tests')
        self.assertEqual(commit.author.name, 'bar')
        self.assertEqual(commit.author.email, 'bar@foo.com')

    def test_diff_head(self):
        """ Test the pygit2_utils.GitRepo().diff returning the diff against
        HEAD
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        with open(os.path.join(repo_path, 'sources'), 'w') as stream:
            stream.write('\nBoo!!2')

        exp = '''diff --git a/sources b/sources
index e69de29..d7d49f8 100644
--- a/sources
+++ b/sources
@@ -0,0 +1,2 @@
+
+Boo!!2
\ No newline at end of file
'''

        diff = repo.diff()
        self.assertEqual(diff.patch, exp)

    def test_diff_commit(self):
        """ Test the pygit2_utils.GitRepo().diff returning the diff of a
        specified commit with its parents.
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

        # Fails: hash invalid
        self.assertRaises(
            ValueError,
            repo.diff,
            'foo'
        )

        commitid = repo_obj.revparse_single('HEAD').oid.hex

        exp = '''diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/.gitignore
diff --git a/sources b/sources
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/sources
'''

        diff = repo.diff(commitid)
        self.assertEqual(diff.patch, exp)

        self.add_commits()

        commitid = repo_obj.revparse_single('HEAD').oid.hex

        exp = '''diff --git a/sources b/sources
index 94921de..fa457ba 100644
--- a/sources
+++ b/sources
@@ -1 +1 @@
-0/2
+1/2
'''

        diff = repo.diff(commitid)
        self.assertEqual(diff.patch, exp)

    def test_diff_commits(self):
        """ Test the pygit2_utils.GitRepo().diff returning the diff of two
        specific commits.
        """
        self.setup_git_repo()
        self.add_commits()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

        # Fails: hash invalid
        self.assertRaises(
            KeyError,
            repo.diff,
            'foo',
            'bar'
        )

        # Retrieve some commits to work with
        commitid = repo_obj.revparse_single('HEAD').oid.hex
        commitid1 = repo_obj.revparse_single('HEAD^').oid.hex
        commitid2 = repo_obj.revparse_single('%s^' % commitid1).oid.hex

        exp = '''diff --git a/sources b/sources
index fa457ba..94921de 100644
--- a/sources
+++ b/sources
@@ -1 +1 @@
-1/2
+0/2
'''

        diff = repo.diff(commitid, commitid1)
        self.assertEqual(diff.patch, exp)

        exp = '''diff --git a/sources b/sources
index 94921de..e69de29 100644
--- a/sources
+++ b/sources
@@ -1 +0,0 @@
-0/2
'''

        diff = repo.diff(commitid1, commitid2)
        self.assertEqual(diff.patch, exp)

        exp = '''diff --git a/sources b/sources
index fa457ba..e69de29 100644
--- a/sources
+++ b/sources
@@ -1 +0,0 @@
-1/2
'''

        diff = repo.diff(commitid, commitid2)
        self.assertEqual(diff.patch, exp)

        exp = '''diff --git a/sources b/sources
index e69de29..fa457ba 100644
--- a/sources
+++ b/sources
@@ -0,0 +1 @@
+1/2
'''

        diff = repo.diff(commitid2, commitid)
        self.assertEqual(diff.patch, exp)

    def test_list_branches(self):
        """ Test the pygit2_utils.GitRepo().list_branches method returning
        the list of branches.
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        # Fails: status invalid
        self.assertRaises(
            ValueError,
            repo.list_branches,
            'foo',
        )

        branches = repo.list_branches()
        self.assertEqual(branches, ['master', 'origin/master'])

        self.add_branches()

        branches = repo.list_branches()
        self.assertEqual(
            sorted(branches),
            ['foo0', 'foo1', 'master', 'origin/master']
        )

        branches = repo.list_branches('local')
        self.assertEqual(sorted(branches), ['foo0', 'foo1', 'master'])

        branches = repo.list_branches('remote')
        self.assertEqual(sorted(branches), ['origin/master'])

    def test_list_tags(self):
        """ Test the pygit2_utils.GitRepo().list_tags method returning the
        list of tags. present in the repo
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        tags = repo.list_tags()
        self.assertEqual(tags, [])

        self.add_tags()

        tags = repo.list_tags()
        self.assertEqual(tags, ['v0', 'v1'])

    def test_tag(self):
        """ Test the pygit2_utils.GitRepo().tag method used to tag a
        specific commit
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

        tags = repo.list_tags()
        self.assertEqual(tags, [])

        self.add_commits(n=4)

        commitid = repo_obj.revparse_single('HEAD~3').oid.hex
        tagid = repo.tag('test1', commitid, 'test commit')
        tagobj = repo_obj.get(tagid)
        self.assertEqual(tagobj.name, 'test1')
        self.assertEqual(tagobj.target.hex, commitid)
        self.assertEqual(tagobj.message, 'test commit')

        tags = repo.list_tags()
        self.assertEqual(tags, ['test1'])

        commitid = repo_obj.revparse_single('HEAD~2').oid.hex
        tagid = repo.tag('test2', commitid)
        tagobj = repo_obj.get(tagid)
        self.assertEqual(tagobj.name, 'test2')
        self.assertEqual(tagobj.target.hex, commitid)
        self.assertEqual(tagobj.message, '')

        tags = repo.list_tags()
        self.assertEqual(tags, ['test1', 'test2'])

        tagid = repo.tag('test3')
        tagobj = repo_obj.get(tagid)
        self.assertEqual(tagobj.name, 'test3')
        self.assertEqual(
            tagobj.target.hex,
            repo_obj.revparse_single('HEAD').oid.hex)
        self.assertEqual(tagobj.message, '')

        tags = repo.list_tags()
        self.assertEqual(tags, ['test1', 'test2', 'test3'])

    def test_checkout(self):
        """ Test the pygit2_utils.GitRepo().checkout method used to change
        branch
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        branches = repo.list_branches('local')
        self.assertEqual(branches, ['master'])
        self.assertEqual(repo.current_branch, 'master')

        self.assertRaises(
            pygit2_utils.exceptions.NoSuchBranchError,
            repo.checkout,
            'foo0'
        )

        self.add_branches()
        branches = repo.list_branches('local')
        self.assertEqual(branches, ['foo0', 'foo1', 'master'])
        self.assertEqual(repo.current_branch, 'master')

        repo.checkout('foo0')
        branches = repo.list_branches('local')
        self.assertEqual(branches, ['foo0', 'foo1', 'master'])
        self.assertEqual(repo.current_branch, 'foo0')

    def test_head_of_branch(self):
        """ Test the pygit2_utils.GitRepo().head_of_branch method used to
        retrieve the HEAD commit of a specified branch
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        branches = repo.list_branches('local')
        self.assertEqual(branches, ['master'])
        self.assertEqual(repo.current_branch, 'master')

        self.assertRaises(
            pygit2_utils.exceptions.NoSuchBranchError,
            repo.head_of_branch,
            'foo0'
        )

        self.add_branches()
        branches = repo.list_branches('local')
        self.assertEqual(branches, ['foo0', 'foo1', 'master'])
        self.assertEqual(repo.current_branch, 'master')

        commit = repo.head_of_branch('foo0')
        self.assertEqual(repo.current_branch, 'master')
        self.assertTrue(isinstance(commit, pygit2.Commit))

        # Check that both commits are the same since `master` and `foo0`
        # are at the same level
        commit_master = repo.head_of_branch('master')
        self.assertEqual(repo.current_branch, 'master')
        self.assertTrue(commit, commit_master)

    def test_add_remote(self):
        """ Test the pygit2_utils.GitRepo().add_remote method used to add a
        remote to a git repository.
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)

        remote = repo.add_remote('origin_master', repo_path)

        remote.fetch()

        branches = repo.list_branches()
        self.assertEqual(
            branches,
            ['master', 'origin/master', 'origin_master/master'])
        self.assertEqual(repo.current_branch, 'master')

        commit_local = repo.head_of_branch('master')
        self.assertEqual(repo.current_branch, 'master')
        self.assertTrue(isinstance(commit_local, pygit2.Commit))

        # Check that both commits are the same since `master` and `foo0`
        # are at the same level
        commit_remote = repo.head_of_branch('origin_master/master')
        self.assertEqual(repo.current_branch, 'master')
        self.assertTrue(commit_local, commit_remote)

    def test_patch(self):
        """ Test the pygit2_utils.GitRepo().patch returning the patch of
        one commit
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

        # Fails: hash invalid
        self.assertRaises(
            KeyError,
            repo.patch,
            'foo'
        )

        # Retrieve one commit to work with
        commitid = repo_obj.revparse_single('HEAD').oid.hex

        patch = repo.patch(commitid)

        exp = """From <id> Mon Sep 17 00:00:00 2001
From: Alice Author <alice@authors.tld>
Date:
Subject: Add basic file required


---

diff --git a/.gitignore b/.gitignore
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/.gitignore
diff --git a/sources b/sources
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/sources

"""
        patch = patch.split('\n')
        # We can't predict the git hash
        patch[0] = 'From <id> Mon Sep 17 00:00:00 2001'
        # nor the exact date & time we create the commit
        patch[2] = 'Date:'
        patch = '\n'.join(patch)

        self.assertEqual(patch, exp)

    def test_patch_multi(self):
        """ Test the pygit2_utils.GitRepo().patch returning a single patch
        for multiple commits
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

        # Fails: hash invalid
        self.assertRaises(
            KeyError,
            repo.patch,
            'foo'
        )

        self.add_commits()

        commitids = [repo_obj.revparse_single('HEAD').oid.hex]
        commitids.append(repo_obj.revparse_single('HEAD^').oid.hex)

        patch = repo.patch(commitids)

        exp = """From <id> Mon Sep 17 00:00:00 2001
From: Alice Author <alice@authors.tld>
Date:
Subject: [PATCH 1/2] Add commit 1 out of 2


 foo
---

diff --git a/sources b/sources
index 94921de..fa457ba 100644
--- a/sources
+++ b/sources
@@ -1 +1 @@
-0/2
+1/2

From <id> Mon Sep 17 00:00:00 2001
From: Alice Author <alice@authors.tld>
Date:
Subject: [PATCH 2/2] Add commit 0 out of 2


 foo
---

diff --git a/sources b/sources
index e69de29..94921de 100644
--- a/sources
+++ b/sources
@@ -0,0 +1 @@
+0/2

"""
        patch = patch.split('\n')
        # We can't predict the git hash
        patch[0] = 'From <id> Mon Sep 17 00:00:00 2001'
        patch[17] = 'From <id> Mon Sep 17 00:00:00 2001'
        # nor the exact date & time we create the commit
        patch[2] = 'Date:'
        patch[19] = 'Date:'
        patch = '\n'.join(patch)

        self.assertEqual(patch, exp)

    def test_merge(self):
        """ Test the pygit2_utils.GitRepo().merge method used to merge a
        branch from a repo to another
        """

        # Create second repo
        second_path = os.path.join(self.gitroot, 'second_test_repo')
        second_repo_obj = pygit2.init_repository(second_path)
        second_repo = pygit2_utils.GitRepo(second_path)

        # Create a commit in our second repo to create the `master` branch
        open(os.path.join(second_path, 'tmp'), 'w').close()
        second_repo.commit('first commit', 'tmp')

        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)
        # Add commit to the original repo
        self.add_commits()

        # Add original repo to second repo
        remote = second_repo.add_remote('upstream', repo_path)
        remote.fetch()

        commit = repo_obj.lookup_reference('HEAD').get_object()
        # Merge original repo into second repo
        second_repo.merge(
            commit.oid.hex,
            branch_name='upstream/master',
            message='test merge')

        commit = second_repo_obj.lookup_reference('HEAD').get_object()
        self.assertEqual(commit.message, 'test merge')


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ScmTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
