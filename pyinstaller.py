# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

hiddenimports = []
hiddenimports += collect_submodules("canu")
hiddenimports += collect_submodules("network_modeling")
added_files = []
added_files += collect_data_files("canu", True) + copy_metadata("canu")
block_cipher = None

added_files += [
    ("network_modeling/models/*", "network_modeling/models"),
    ("network_modeling/mac_vendors", "network_modeling"),
    ("network_modeling/schema/*", "network_modeling/schema"),
    (
        "network_modeling/configs/templates/1.0/aruba/common/*.j2",
        "network_modeling/configs/templates/1.0/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.0/aruba/full/*.j2",
        "network_modeling/configs/templates/1.0/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.0/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.0/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.0/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.0/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.0/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.0/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.2/arista/*.j2",
        "network_modeling/configs/templates/1.2/arista",
    ),
    (
        "network_modeling/configs/templates/1.2/aruba/common/*.j2",
        "network_modeling/configs/templates/1.2/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.2/aruba/full/*.j2",
        "network_modeling/configs/templates/1.2/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.2/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.2/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.2/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.2/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.2/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.2/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.3/arista/*.j2",
        "network_modeling/configs/templates/1.3/arista",
    ),
    (
        "network_modeling/configs/templates/1.3/aruba/common/*.j2",
        "network_modeling/configs/templates/1.3/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.3/aruba/*.j2",
        "network_modeling/configs/templates/1.3/aruba/",
    ),
    (
        "network_modeling/configs/templates/1.3/aruba/full/*.j2",
        "network_modeling/configs/templates/1.3/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.3/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.3/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.3/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.3/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.3/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.3/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.4/arista/*.j2",
        "network_modeling/configs/templates/1.4/arista",
    ),
    (
        "network_modeling/configs/templates/1.4/aruba/common/*.j2",
        "network_modeling/configs/templates/1.4/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.4/aruba/*.j2",
        "network_modeling/configs/templates/1.4/aruba/",
    ),
    (
        "network_modeling/configs/templates/1.4/aruba/full/*.j2",
        "network_modeling/configs/templates/1.4/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.4/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.4/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.4/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.4/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.4/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.4/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.5/arista/*.j2",
        "network_modeling/configs/templates/1.5/arista",
    ),
    (
        "network_modeling/configs/templates/1.5/aruba/common/*.j2",
        "network_modeling/configs/templates/1.5/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.5/aruba/*.j2",
        "network_modeling/configs/templates/1.5/aruba/",
    ),
    (
        "network_modeling/configs/templates/1.5/aruba/full/*.j2",
        "network_modeling/configs/templates/1.5/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.5/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.5/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.5/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.5/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.5/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.5/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.6/arista/*.j2",
        "network_modeling/configs/templates/1.6/arista",
    ),
    (
        "network_modeling/configs/templates/1.6/aruba/common/*.j2",
        "network_modeling/configs/templates/1.6/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.6/aruba/*.j2",
        "network_modeling/configs/templates/1.6/aruba/",
    ),
    (
        "network_modeling/configs/templates/1.6/aruba/full/*.j2",
        "network_modeling/configs/templates/1.6/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.6/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.6/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.6/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.6/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.6/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.6/dellmellanox/full",
    ),
    (
        "network_modeling/configs/templates/1.7/arista/*.j2",
        "network_modeling/configs/templates/1.7/arista",
    ),
    (
        "network_modeling/configs/templates/1.7/aruba/common/*.j2",
        "network_modeling/configs/templates/1.7/aruba/common",
    ),
    (
        "network_modeling/configs/templates/1.7/aruba/*.j2",
        "network_modeling/configs/templates/1.7/aruba/",
    ),
    (
        "network_modeling/configs/templates/1.7/aruba/full/*.j2",
        "network_modeling/configs/templates/1.7/aruba/full",
    ),
    (
        "network_modeling/configs/templates/1.7/aruba/tds/*.j2",
        "network_modeling/configs/templates/1.7/aruba/tds",
    ),
    (
        "network_modeling/configs/templates/1.7/dellmellanox/common/*.j2",
        "network_modeling/configs/templates/1.7/dellmellanox/common",
    ),
    (
        "network_modeling/configs/templates/1.7/dellmellanox/full/*.j2",
        "network_modeling/configs/templates/1.7/dellmellanox/full",
    ),
]
a = Analysis(
    ["canu/cli.py"],
    pathex=["canu"],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=["./pyinstaller_hooks"],
    runtime_hooks=[],
    excludes=["tests"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
a_pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
a_exe = EXE(
    a_pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="canu",
    debug=False,
    bootloader_ignore_signal=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)


b = Analysis(
    ["canu/inventory/ansible.py"],
    pathex=["canu"],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=["./pyinstaller_hooks"],
    runtime_hooks=[],
    excludes=["tests"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

b_pyz = PYZ(b.pure, b.zipped_data, cipher=block_cipher)
b_exe = EXE(
    b_pyz,
    b.scripts,
    b.binaries,
    b.zipfiles,
    b.datas,
    [],
    name="canu-inventory",
    debug=False,
    bootloader_ignore_signal=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

coll = COLLECT(
    b_exe,
    b.binaries,
    b.zipfiles,
    b.datas,
    a_exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="canupkg",
)
