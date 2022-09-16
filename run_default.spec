# -*- mode: python ; coding: utf-8 -*-
import os
import pymunk

ONE_FILE = False
EXCLUDE = ['c_test', 'Resources', 'Templates',
           'build', 'dist', 'venv']
EXCLUDE_EXT = ['.spec', '.txt', '.json', '.py', '.mp4', '.ppt', '.doc', '.bat']


def filter(path):
    path = os.path.normpath(path)
    for e in EXCLUDE:
        if path.startswith(e):
            return False
    for i in path.split('\\'):
        if i.startswith('.'):
            return False
        if i.startswith('_'):
            return False
    return True


datas = []
for p, ds, fs in os.walk('.'):
    if filter(p):
        for f in fs:
            ffp = os.path.join(p, f)
            if os.path.splitext(ffp)[1] not in EXCLUDE_EXT:
                datas.append((ffp, p))

pymunk_dir = os.path.dirname(pymunk.__file__)
# chipmunk_libs = [
#    ('chipmunk.dll', os.path.join(pymunk_dir, 'chipmunk.dll'), 'DATA'),
# ]

block_cipher = None

a = Analysis(
    ['run_default.py'],
    pathex=[],
    binaries=[(os.path.join(pymunk_dir, 'chipmunk.dll'), '.')],
    datas=datas,
    hiddenimports=[],
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
    *([a.binaries, a.zipfiles, a.datas]
      if ONE_FILE
      else []),
    [],
    exclude_binaries=not ONE_FILE,
    name='YetAnotherGame',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
if not ONE_FILE:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='YetAnotherGame',
    )
