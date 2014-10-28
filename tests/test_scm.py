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

    def test_diff_head(self):
        """ Test the pygit2_utils.GitRepo().diff returning the diff against
        HEAD
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        repo = pygit2_utils.GitRepo(repo_path)
        repo_obj = pygit2.Repository(repo_path)

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


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ScmTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
