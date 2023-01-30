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
NAME := $(shell basename $(shell pwd))
endif

ifeq ($(ARCH),)
ARCH := x86_64
endif

ifeq ($(IMAGE_VERSION),)
IMAGE_VERSION := $(shell git describe --tags | tr -s '-' '_' | tr -d '^v')
endif

ifeq ($(PY_FULL_VERSION),)
PY_FULL_VERSION := $(shell awk -v replace="'" '/pythonVersion/{gsub(replace,"", $$NF); print $$NF; exit}' Jenkinsfile.github)
PY_VERSION := $(shell echo ${PY_FULL_VERSION} | awk -F '.' '{print $$1"."$$2}')
endif

ifeq ($(SLE_VERSION),)
SLE_VERSION := $(shell awk -v replace="'" '/mainSleVersion/{gsub(replace,"", $$NF); print $$NF; exit}' Jenkinsfile.github)
endif

ifeq ($(VERSION),)
VERSION := $(shell git describe --tags | tr -s '-' '~' | tr -d '^v')
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

image:
		docker build --build-arg SLE_VERSION='${SLE_VERSION}' --build-arg PY_VERSION='${PY_VERSION}' --tag 'cray-${NAME}:${IMAGE_VERSION}' .

snyk:
	snyk container test --severity-threshold=high --file=Dockerfile --fail-on=all --docker cray-canu:${IMAGE_VERSION}

rpm_package_source:
		tar --transform 'flags=r;s,^,/$(SOURCE_NAME)/,' --exclude .nox --exclude dist/rpmbuild -cvjf $(SOURCE_PATH) .

rpm_build_source:
		rpmbuild -ts $(SOURCE_PATH) --define "_topdir $(BUILD_DIR)"

rpm_build:
		rpmbuild -ba $(SPEC_FILE) --define "_topdir $(BUILD_DIR)"
