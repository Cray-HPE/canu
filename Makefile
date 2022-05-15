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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
name ?= ${GIT_REPO_NAME}

version := $(shell cat $(name)/.version)

build_image := cdrx/pyinstaller-linux:python3

# Default release if not set
BUILD_METADATA ?= "1~development~$(shell git rev-parse --short HEAD)"

spec_file := ${name}.spec
source_name := ${name}-${version}

build_dir := $(PWD)/dist/rpmbuild
source_path := ${build_dir}/SOURCES/${source_name}.tar.bz2

all : prepare binary test rpm
rpm: rpm_package_source rpm_build_source rpm_build

prepare:
		rm -rf dist
		mkdir -p $(build_dir)/SPECS $(build_dir)/SOURCES
		cp $(spec_file) $(build_dir)/SPECS/

binary:
		docker run --rm -v $(PWD):/src $(build_image) ./pyinstaller.sh

test:
		docker run --rm -v $(PWD):/src $(build_image) nox

rpm_package_source:
		tar --transform 'flags=r;s,^,/$(source_name)/,' --exclude .git --exclude .nox --exclude dist/rpmbuild -cvjf $(source_path) .

rpm_build_source:
		BUILD_METADATA=$(BUILD_METADATA) rpmbuild -ts $(source_path) --define "_topdir $(build_dir)"

rpm_build:
		BUILD_METADATA=$(BUILD_METADATA) rpmbuild -ba $(spec_file) --define "_topdir $(build_dir)"
