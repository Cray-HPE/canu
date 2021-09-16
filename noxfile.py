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
"""Nox definitions for tests, docs, and linting."""

import nox


COVERAGE_FAIL = 90
ERROR_ON_GENERATE = True
locations = "canu", "tests", "noxfile.py", "network_modeling"
nox.options.sessions = "tests", "lint", "cover"


@nox.session(python="3")
def tests(session):
    """Default unit test session."""
    # Install all test dependencies, then install this package in-place.
    path = "tests"
    session.install("-r", "requirements-test.txt")
    session.install("-e", ".")

    if session.posargs:
        path = session.posargs[0]

    # Run pytest against the tests.
    session.run(
        "pytest",
        "--quiet",
        "--cov=canu",
        "--cov=tests",
        "--cov=network_modeling",
        "--cov-append",
        "--cov-report=",
        "--cov-fail-under={}".format(COVERAGE_FAIL),
        path,
        *session.posargs
    )


@nox.session(python="3")
def lint(session):
    """Run flake8 linter and plugins."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
        "toml",
    )
    session.run("flake8", *args)


@nox.session(python="3")
def black(session):
    """Run Black, the uncompromising Python code formatter."""
    args = session.posargs or locations
    # exclude = "(/bin, /lib)"
    exclude = """
    ^/(
    (
        canu/lib
        | canu/bin
    )
    )
    """
    session.install("black")
    session.run("black", "--exclude", exclude, *args)


@nox.session(python="3")
def cover(session):
    """Run the final coverage report."""
    session.install("coverage", "pytest-cov")
    session.run(
        "coverage", "report", "--show-missing", "--fail-under={}".format(COVERAGE_FAIL)
    )
    session.run("coverage", "erase")
