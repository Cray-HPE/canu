name = canu

version := $(shell cat canu/.version)

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
