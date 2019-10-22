import pymunk
import os

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

if __name__ == '__main__':
    for i in datas:
        print(i)