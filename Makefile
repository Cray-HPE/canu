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

ifeq ($(IMAGE_VERSION),)
export IMAGE_VERSION := $(shell python3 -m setuptools_scm | tr -s '+' '_' | sed 's/^v//')
endif

ifeq ($(PYTHON_VERSION),)
export PYTHON_VERSION := 3.10
endif

ifeq ($(ALPINE_IMAGE),)
export ALPINE_IMAGE := artifactory.algol60.net/docker.io/library/alpine
endif

ifeq ($(ALPINE_VERSION),)
export ALPINE_VERSION := 3.17
endif

export PYTHON_BIN := python$(PYTHON_VERSION)

ifeq ($(VERSION),)
export VERSION := $(shell python3 -m setuptools_scm | tr -s '-' '~' | tr -s '+' '_' | sed 's/^v//')
endif

ifeq ($(DOCKER_BUILDKIT),)
export DOCKER_BUILDKIT := 1
endif

BUILD_ARGS ?= --build-arg 'PYTHON_VERSION=${PYTHON_VERSION}' --build-arg 'ALPINE_IMAGE=${ALPINE_IMAGE}' --build-arg 'ALPINE_VERSION=${ALPINE_VERSION}'

PLATFORMS := linux/amd64,linux/arm64

SPEC_FILE := ${NAME}.spec
SOURCE_NAME := ${NAME}-${VERSION}

BUILD_DIR := $(PWD)/dist/rpmbuild
SOURCE_PATH := ${BUILD_DIR}/SOURCES/${SOURCE_NAME}.tar.bz2

BRANCH := $(shell git rev-parse --abbrev-ref HEAD)

BUILDER ?= canu_builder

.PHONY: docs

all : prepare binary test rpm
rpm: rpm_package_source rpm_build_source rpm_build

# docs are deployed with mike, but we can build them locally with mkdocs
# mike can also serve local docs, but requires a bit more setup
# with deploy and set-default and using a specfic branch so as not to overwrite gh-pages
docs:
	mkdocs serve --config-file mkdocs.yml

cdocs:
	docker run -it --rm -p 8000:8000 '${NAME}:${VERSION}-docs'

prepare:
	@echo $(NAME)
	rm -rf $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/SPECS $(BUILD_DIR)/SOURCES
	cp $(SPEC_FILE) $(BUILD_DIR)/SPECS/

image_%:
	@echo Building $@ ...

	# Build multi_arch image.
	docker buildx use $(BUILDER) 2>/dev/null || docker buildx create --platform ${PLATFORMS} --use --name $(BUILDER)
	docker buildx build --platform=${PLATFORMS} --pull --progress plain --builder $(BUILDER) ${BUILD_ARGS} ${DOCKER_ARGS} --target $(@:image_%=%) .

	# Load only supports one arch at a time, but our tags for one platform will apply to all platforms so just refer to the amd64 platform to work around it.
	docker buildx build --platform linux/amd64 --pull --load --builder $(BUILDER) ${BUILD_ARGS} ${DOCKER_ARGS} -t '${NAME}:${VERSION}-$(@:image_%=%)' --target $(@:image_%=%) .

	if [ $@ = "image_prod" ]; then \
		docker buildx build --platform linux/amd64 --pull --progress plain --load --builder $(BUILDER) ${BUILD_ARGS} ${DOCKER_ARGS} -t '${NAME}:${VERSION}' --target $(@:image_%=%) . ;\
		docker buildx build --platform linux/amd64 --pull --progress plain --load --builder $(BUILDER) ${BUILD_ARGS} ${DOCKER_ARGS} -t '${NAME}:${VERSION}-p${PYTHON_VERSION}' --target $(@:image_%=%) . ;\
	fi

dev:
	./canuctl -d

prod:
	./canuctl -p

snyk:
	snyk container test --severity-threshold=high --file=Dockerfile --fail-on=all --docker ${NAME}:${VERSION}

# touch the archive before creating it to prevent 'tar: .: file changed as we read it' errors
rpm_package_source:
		touch $(SOURCE_PATH)
		tar --transform 'flags=r;s,^,/$(SOURCE_NAME)/,' --exclude .nox --exclude dist/rpmbuild --exclude ${SOURCE_NAME}.tar.bz2 -cvjf $(SOURCE_PATH) .

rpm_build_source:
		rpmbuild -vv -ts $(SOURCE_PATH) --target ${ARCH} --define "_topdir $(BUILD_DIR)"

rpm_build:
		rpmbuild -vv -ba $(SPEC_FILE) --target ${ARCH} --define "_topdir $(BUILD_DIR)"
