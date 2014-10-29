#!/usr/bin/python
from setuptools import setup

setup(
    name="pygit2.utils",
    version="0.1",
    author="Pierre-Yves Chibon",
    author_email="pingou@pingoured.fr",
    description=("A python library providing a simple interface to pygit2"),
    license="GPLv2+",
    url = "",
    packages = ['pygit2_utils'],
    classifiers=(
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    test_suite="nose.collector",
)
