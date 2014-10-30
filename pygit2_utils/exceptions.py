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
This module presents all the exceptions raised by pygit2_utils.

All these exceptions are inheriting from `PyGitUtilsError` which can then
be used to catch them.

"""


class PyGitUtilsError(Exception):
    """ This class is never thrown but can be used to catch errors thrown
    by pygit2_utils.
    It is inherited by all other exceptions raised by the library.
    """
    message = 'An error occured in pygit2_utils'


class NoSuchRefError(PyGitUtilsError):
    """ Exception raised when a reference is looked-up but could not be
    found in the repo.
    """
    message = 'This reference could not be found'


class NoSuchBranchError(PyGitUtilsError):
    """ Exception raised when a branch is looked-up but could not be found
    in the repo.
    """
    message = 'This branch could not be found'


class NothingToMergeError(PyGitUtilsError):
    """ Exception raised when trying to merge two branches which are already
    in sync.
    """
    message = 'Nothing to merge, these branches are already in sync'


class MergeConflictsError(PyGitUtilsError):
    """ Exception raised when trying to merge two branches with a conflict.
    """
    message = 'Can not merge these branches, there is a conflict'
