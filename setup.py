# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
import os
from setuptools import setup, find_packages

BASE_DIR=os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "requirements.txt")) as req_file:
    REQUIREMENTS = req_file.read()

with open(os.path.join(BASE_DIR, "canu", ".version")) as version_file:
    VERSION = version_file.read()

setup(
    name="canu",
    author="Sean Lynn",
    author_email="sean.lynn@hpe.com",
    description="CSM Automatic Network Utility",
    long_description="CANU floats through Shasta networks and makes configuration a breeze.",
    version=VERSION,
    py_modules=["canu"],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    package_data={"canu": [".version",
                           "canu.yaml",
                           "validate/switch/config/*.yaml"],
                  "network_modeling": ["schema/*.json",
                                       "schema/*.yaml",
                                       "models/*yaml",
                                       "configs/templates/**/*"],
    },
    exclude_package_data={"canu": ["canu_cache.yaml"]},
    install_requires=REQUIREMENTS,
    entry_points="""
        [console_scripts]
        canu=canu.cli:cli
    """,
)
