# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['canu/cli.py'],
             pathex=['canu', '/workspace'],
             binaries=[],
             datas=[
               ('.version', '.'),
               ('canu/canu.yaml', 'canu'),
               ('network_modeling/models/*', 'network_modeling/models'),
               ('network_modeling/schema/*', 'network_modeling/schema'),
             ],
             hiddenimports=['network_modeling'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='canu',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
