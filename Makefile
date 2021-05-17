default: build

filepath := $(PWD)
build_image := cdrx/pyinstaller-linux:python3

build:
		docker run --rm -v $(filepath):/src $(build_image) ./pyinstaller.sh
		rpmbuild -bb canu.rpm.spec

test:
		docker run --rm -v $(filepath):/src $(build_image) nox
