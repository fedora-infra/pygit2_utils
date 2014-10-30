pygit2_utils
============

:Author: Pierre-Yves Chibon <pingou@pingoured.fr>

`pygit2 <http://www.pygit2.org>`_ is a python library interfacing with
`libgit2 <https://libgit2.github.com/>`_ to interact with `git
<http://git-scm.com/>`_.

pygit2 is very performant and offers an API that is quite close to the C
API from libgit2.
pygit2_utils aims at providing a simple(r) API for pygit2, taking care of
calling pygit2 under the hood and thus exposing a simple API to interact
with git repositories.


.. note:: This project is currently in a early-alpha stage and if we are
          pleased with its current status, its API might change in the
          future (until we make an official 1.0 release).
          We will try to minimize those API change though.


Why using pygit2_utils? pygit2_utils aims at providing a stable API, which
pygit2 does not (cf the note in this section of the
`pygit2 documentation <https://github.com/libgit2/pygit2/blob/master/docs/install.rst#version-numbers>`_
)


Dependencies
------------

The only dependency of this project is:

* `pygit2 <http://www.pygit2.org>`_


Testing:
--------

This project is fully compatible with python 2.7 and python 3.
It contains unit-tests allowing early detection of changes in pygit2 or
break in API and allowing to easily make sure that the code runs on both
python 2.7 and python 3.


To run them::

  python setup.py nosetests
  python3 setup.py nosetests



License:
--------

This project is licensed GPLv2+.
