#
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
#
ifeq ($(NAME),)
export NAME := $(shell basename $(shell pwd))
endif

ifeq ($(ARCH),)
export ARCH := x86_64
endif

ifeq ($(PYTHON_VERSION),)
export PYTHON_VERSION := 3.10
endif

ifeq ($(ALPINE_IMAGE),)
export ALPINE_IMAGE := artifactory.algol60.net/docker.io/library/alpine:3.17
endif

export PYTHON_BIN := python$(PYTHON_VERSION)

ifeq ($(VERSION),)
export VERSION := $(shell python3 -m setuptools_scm | tr -s '-' '~' | tr -s '+' '_' | sed 's/^v//')
endif

SPEC_FILE := ${NAME}.spec
SOURCE_NAME := ${NAME}-${VERSION}

BUILD_DIR := $(PWD)/dist/rpmbuild
SOURCE_PATH := ${BUILD_DIR}/SOURCES/${SOURCE_NAME}.tar.bz2

all : prepare binary test rpm
rpm: rpm_package_source rpm_build_source rpm_build

prepare:
		@echo $(NAME)
		rm -rf dist
		mkdir -p $(BUILD_DIR)/SPECS $(BUILD_DIR)/SOURCES
		cp $(SPEC_FILE) $(BUILD_DIR)/SPECS/

image: prod_image
	docker tag '${NAME}:${VERSION}' '${NAME}:${VERSION}-p${PYTHON_VERSION}'

deps_image:
	docker build --progress plain --no-cache --pull --build-arg PYTHON_VERSION='${PYTHON_VERSION}' --tag '${NAME}:${VERSION}-deps' -f Dockerfile --target deps .

dev_image:
	docker build --progress plain --no-cache --pull --build-arg PYTHON_VERSION='${PYTHON_VERSION}' --tag '${NAME}:${VERSION}-dev' -f Dockerfile --target dev .

build_image:
	docker build --progress plain --no-cache --pull --build-arg PYTHON_VERSION='${PYTHON_VERSION}' --tag '${NAME}:${VERSION}-build' -f Dockerfile --target build .

prod_image:
	docker build --progress plain --no-cache --pull --build-arg PYTHON_VERSION='${PYTHON_VERSION}' --tag '${NAME}:${VERSION}' -f Dockerfile --target prod .

dev:
	./canu-docker -d

prod:
	./canu-docker -p

snyk:
	snyk container test --severity-threshold=high --file=Dockerfile --fail-on=all --docker ${NAME}:${VERSION}

# touch the archive before creating it to prevent 'tar: .: file changed as we read it' errors
rpm_package_source:
		touch $(SOURCE_PATH)
		tar --transform 'flags=r;s,^,/$(SOURCE_NAME)/,' --exclude .nox --exclude dist/rpmbuild --exclude ${SOURCE_NAME}.tar.bz2 -cvjf $(SOURCE_PATH) .

rpm_build_source:
		rpmbuild -vv -ts $(SOURCE_PATH) --define "_topdir $(BUILD_DIR)"

rpm_build:
		rpmbuild -vv -ba $(SPEC_FILE) --define "_topdir $(BUILD_DIR)"
