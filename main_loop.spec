# -*- mode: python -*-

import os
import pymunk

exclude = ['c_test', 'Resources', 'Templates', 'dist']
exclude_ext = ['.spec', '.txt', '.json', '.py', '.mp4', '.ppt', '.doc', '.bat']


def filter(path):
    path = os.path.normpath(path)
    for e in exclude:
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
            if os.path.splitext(ffp)[1] not in exclude_ext:
                datas.append((ffp, p))

pymunk_dir = os.path.dirname(pymunk.__file__)
chipmunk_libs = [
    ('chipmunk.dll', os.path.join(pymunk_dir, 'chipmunk.dll'), 'DATA'),
]


block_cipher = None


a = Analysis(['main_loop.py'],
             pathex=['D:\\Game\\Yandex\\Scripts\\pygame_project'],
             binaries=[],
             datas=datas,
             hiddenimports=[],
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
          [],
          exclude_binaries=True,
          name='Game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries + chipmunk_libs,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Game')
