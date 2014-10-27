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

    def test_git_config(self):
        """ Test the pygit2_utils.GitConfig to object to browse the git
        config
        """
        self.setup_git_repo()

        repo_path = os.path.join(self.gitroot, 'test_repo')
        config = pygit2_utils.GitConfig(repopath=repo_path)

        # Fails: section does not exists
        self.assertRaises(
            configparser.NoSectionError,
            config.get,
            'foo',
            'email'
        )

        # Fails: option does not exists
        self.assertRaises(
            configparser.NoOptionError,
            config.get,
            'user',
            'bar'
        )

        # Works
        self.assertEqual(config.get('user', 'name'), 'foo')
        self.assertEqual(config.get('user', 'email'), 'foo@bar.com')
        self.assertEqual(config.get_user(), 'foo <foo@bar.com>')

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

        self.assertEqual(repo.current_remote_name, 'origin/master')

        repo_path = os.path.join(self.gitroot, 'test_repo.git')
        repo = pygit2_utils.GitRepo(repo_path)

        self.assertEqual(repo.current_remote_name, None)


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(ScmTests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
