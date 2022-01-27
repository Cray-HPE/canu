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
import os

from setuptools import find_packages
from setuptools import setup

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, ".version")) as version_file:
    VERSION = version_file.read()


def readme() -> str:
    """
    Print the README file.
    :returns: Read README file.
    """
    with open('README.md') as file:
        return str(file.read())


setup(
    name="canu",
    author="Sean Lynn",
    author_email="sean.lynn@hpe.com",
    description="CSM Automatic Network Utility",
    long_description=readme(),
    version=VERSION,
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
            'sphinx',
            'sphinx_click',
            'myst-parser',
            'sphinx-markdown-builder',
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
        'aiohttp<=0.8.0',
        'click<=8.0.3',
        'click-help-colors<=0.9.1',
        'click-option-group<=0.5.3',
        'click-params<=0.1.2',
        'click-spinner<=0.1.10',
        'colorama<=0.4.4',
        'emoji<=1.6.3',
        'ipython<=8.3.0',
        'jinja2<=3.0.3',
        'hier_config<=2.2.0',
        'kubernetes<=21.7.0',
        'mac_vendor_lookup<=0.1.11.post1',
        'natsort<=8.0.2',
        'netutils<=1.0.0',
        'nornir<=3.2.0',
        'nornir-netmiko<=0.1.2',
        'nornir-salt<=0.8.0',
        'nornir-utils<=0.2.0',
        'netaddr<=0.8.0',
        'netmiko<=3.4.0',
        'netutils<=1.0.0',
        'openpyxl<=3.0.9',
        'pyyaml==5.4.1',
        'requests<=2.27.1',
        'responses<=0.20.0',
        'ruamel.yaml<=0.17.20',
        'tabulate<=0.8.9',
        'tomli<=2.0.0',
        'tokenize-rt<=4.2.1',
        'ttp<=0.8.4',
        'urllib3<=1.26.8',
    ],
    entry_points={
        'console_scripts': [
            'canu=canu.cli:cli'
        ],
    },
)
