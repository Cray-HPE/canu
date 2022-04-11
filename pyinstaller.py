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
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ("canu/.version", "canu"),
    ("canu/canu.yaml", "canu"),
    ("canu/validate/switch/config/*.yaml", "canu/validate/switch/config"),
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
    ("canu/test/aruba/test_suite.yaml", "canu/test/aruba"),
    ("canu/test/dellanox/test_suite.yaml", "canu/test/dellanox"),
]
a = Analysis(
    ["canu/cli.py"],
    pathex=["canu", "/workspace"],
    binaries=[],
    datas=added_files,
    hiddenimports=["network_modeling"],
    hookspath=["./"],
    runtime_hooks=[],
    excludes=["tests"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="canu",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
