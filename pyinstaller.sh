#!/bin/bash
# Pyinstaller needs a .spec file but it conflicts with rpm builds
cp pyinstaller.py pyinstaller.spec
pyinstaller --clean -y --dist ./dist/linux --workpath /tmp pyinstaller.spec
rm pyinstaller.spec
chown -R --reference=. ./dist/linux
