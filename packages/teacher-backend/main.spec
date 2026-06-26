# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

base_dir = Path(SPECFILE).parent
shared_dir = base_dir.parent / 'shared'

a = Analysis(
    ['app/main.py'],
    pathex=[str(base_dir), str(shared_dir)],
    binaries=[],
    datas=[],
    hiddenimports=['uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
                   'uvicorn.protocols', 'uvicorn.protocols.http',
                   'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='teacher-backend',
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
