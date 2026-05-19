# -*- mode: python ; coding: utf-8 -*-

import subprocess
with open('build/githash.py', 'w') as f:
  f.write(f'HASH="{subprocess.run(['git', 'show', '--format=%h', '--no-patch'], capture_output=True).stdout.decode('ascii').strip()}"\n')

a = Analysis(
    ['specmanip.py', 'build/githash.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='specmanip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
