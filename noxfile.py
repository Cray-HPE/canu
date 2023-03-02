# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
from os import listdir, path
from pathlib import Path
import shutil
import sys

import nox

# Get project root directory
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):  # pragma: no cover
    project_root = sys._MEIPASS
else:
    prog = __file__
    project_root = Path(__file__).resolve().parent


COVERAGE_FAIL = 85
ERROR_ON_GENERATE = True
locations = "canu", "tests", "noxfile.py", "network_modeling", "docs/templates/conf.py"
nox.options.sessions = "tests", "lint", "cover", "docs"


@nox.session(python="3")
def tests(session):
    """Default unit test session."""
    # Install all test dependencies, then install this package in-place.
    path = "tests"
    session.install(".[test]")
    session.install(".[network_modeling]")
    session.install(".")

    if session.posargs:
        path = session.posargs[0]

    # Run pytest against the tests.
    session.run(
        "pytest",
        "--log-level=ERROR",
        "--cov-report=",
        f"--cov-fail-under={COVERAGE_FAIL}",
        "--cov=canu",
        "--cov=tests",
        "--cov=network_modeling",
        path,
    )


@nox.session(python="3")
def lint(session):
    """Run flake8 linter and plugins."""
    args = session.posargs or locations
    session.install(".[lint]")
    session.install(".")
    session.run("flake8", *args)


@nox.session(python="3")
def black(session):
    """Run Black, the uncompromising Python code formatter."""
    args = session.posargs or locations
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
    session.install(".[test]")
    session.install(".[network_modeling]")
    session.install(".")
    session.run(
        "coverage",
        "report",
        "--show-missing",
        "--fail-under={}".format(COVERAGE_FAIL),
    )
    session.run("coverage", "erase")


# Docs start as md templates in '/docs/templates'
# sphinx_click runs CANU and generates docs from the flags and docstrings
# myst-parser allows it all to be read in as markdown
# sphinx-markdown-builder exports all docs as markdown
# exported markdown files are moved from '/docs/_build/markdown/' to '/docs/'
@nox.session(python="3")
def docs(session) -> None:
    """Build the documentation."""
    session.install(".[docs]")
    session.install(".[network_modeling]")
    session.run(
        "sphinx-build",
        "-M",
        "markdown",
        "docs/templates",
        "docs/_build",
        "-a",
    )
    copy_built_md_docs()


def copy_built_md_docs():
    """Copy markdown docs from '/docs/_build/markdown' to '/docs'."""
    source_dir = path.join(project_root, "docs", "_build", "markdown")
    target_dir = path.join(project_root, "docs")

    file_names = listdir(source_dir)

    for file_name in file_names:
        shutil.copyfile(
            path.join(source_dir, file_name),
            path.join(target_dir, file_name),
        )
