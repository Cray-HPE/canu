#!/bin/bash
pyinstaller --clean -y --dist ./dist/linux --workpath /tmp pyinstaller.spec
chown -R --reference=. ./dist/linux
