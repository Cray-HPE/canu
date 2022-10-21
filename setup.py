#
# MIT License
#
# (C) Copyright [2022] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
import subprocess
from os.path import dirname
from os.path import isdir
from os.path import join
from os import devnull
import re

from setuptools import find_packages
from setuptools import setup

version_re = re.compile('^Version: (.+)$', re.M)

with open('LICENSE') as license_file:
    LICENSE = license_file.read()


def readme() -> str:
    """
    Print the README file.
    :returns: Read README file.
    """
    with open('README.md') as file:
        return str(file.read())


def get_version():
    d = dirname(__file__)

    if isdir(join(d, '.git')):
        # Get the version using "git describe".
        cmd = 'git describe --tags --match [0-9]*'.split()
        try:
            version = subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            print('Unable to get version number from git tags')
            exit(1)

        # PEP 386 compatibility
        if '-' in version:
            version = '.post'.join(version.split('-')[:2])

        # Don't declare a version "dirty" merely because a time stamp has
        # changed. If it is dirty, append the branch name as a suffix to
        # indicate a development revision after the release.
        with open(devnull, 'w') as fd_devnull:
            subprocess.call(
                ['git', 'status'],
                stdout=fd_devnull, stderr=fd_devnull
            )

        cmd = 'git diff-index --name-only HEAD'.split()
        try:
            dirty = subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            print('Unable to get git index status')
            exit(1)

        if dirty != '':
            version += '.dev1'

    else:
        # Extract the version from the PKG-INFO file.
        with open(join(d, 'PKG-INFO')) as f:
            version = version_re.search(f.read()).group(1)

    return version


setup(
    name="canu",
    author="Sean Lynn",
    author_email="sean.lynn@hpe.com",
    description="CSM Automatic Network Utility",
    long_description=readme(),
    version=get_version(),
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    exclude_package_data={
        "canu": ["canu_cache.yaml"]
    },
    extras_require={
        'ci': [
            'nox',
        ],
        'docs': [
            'myst-parser',
            'sphinx',
            'sphinx-markdown-builder',
            'sphinx_click',
        ],
        'lint': [
            'darglint',
            'flake8',
            'flake8-black',
            'flake8-bugbear',
            'flake8-commas',
            'flake8-comprehensions',
            'flake8-debugger',
            'flake8-docstrings',
            'flake8-eradicate',
            'flake8-import-order',
            'flake8-quotes',
            'flake8-string-format',
            'pep8-naming',
            'toml',
        ],
        'test': [
            'coverage',
            'pytest',
            'pytest-cov',
            'pytest-sugar',
            'testfixtures',
        ],
        'network_modeling': [
            'jsonschema<=4.4.0',
            'matplotlib<=3.5.1',
            'networkx<=2.6.3',
            'yamale<=4.0.2',
        ]
    },
    install_requires=[
        'aiohttp==3.8.0',
        'click-help-colors==0.9.1',
        'click-option-group==0.5.3',
        'click-params==0.1.2',
        'click-spinner==0.1.10',
        'click==8.0.3',
        'colorama==0.4.4',
        'emoji==1.6.0',
        'hier-config==1.6.1',
        'ipython==7.16.3',
        'jinja2==3.0.2',
        'jsonschema==3.2.0',
        'kubernetes==20.13.0',
        'mac-vendor-lookup==0.1.11',
        'natsort==7.1.1',
        'netaddr==0.8.0',
        'netmiko==3.4.0',
        'netutils==1.0.0',
        'nornir-netmiko==0.1.2',
        'nornir-salt==0.9.0',
        'nornir-scrapli==2022.1.30',
        'nornir-utils==0.2.0',
        'nornir==3.2.0',
        'openpyxl==3.0.9',
        'pyyaml==5.4.1',
        'requests==2.26.0',
        'responses==0.14.0',
        'ruamel.yaml<=0.16.13',
        'tabulate==0.8.9',
        'tokenize-rt==3.2.0',
        'tomli==1.1.0',
        'ttp==0.8.4',
        'urllib3==1.26.7',
        'yamale<=4.0.2',
    ],
    entry_points={
        'console_scripts': [
            'canu=canu.cli:cli'
        ],
    },
)
