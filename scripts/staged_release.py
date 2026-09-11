"""Require native Git publication to contain the checked working release."""
import subprocess
from deploy_release import release_paths, ALLOW_ROOT


def verify_staged_release(root, paths=None):
    root = root.resolve()
    full_release = paths is None
    paths = release_paths(root) if full_release else paths
    names = []
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError('Release path must be a regular file: ' + str(path))
        names.append(path.resolve().relative_to(root).as_posix())
    if not names:
        raise ValueError('Empty release file set')
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root).decode('utf-8').split('\0')
    staged = {}
    for entry in filter(None, entries):
        metadata, name = entry.split('\t', 1)
        mode, identity, stage = metadata.split()
        if full_release and (name.startswith(('src/', 'public/')) or name in ALLOW_ROOT) and name not in names:
            raise ValueError('Staged release file is absent from the working release: ' + name)
        if name in names:
            if stage != '0' or mode not in ('100644', '100755'):
                raise ValueError('Unresolved or non-file release entry: ' + name)
            staged[name] = identity
    missing = sorted(set(names) - set(staged))
    if missing:
        raise ValueError('Release files absent from Git staging: ' + ', '.join(missing))
    # Hash actual contents rather than trusting mtimes or assume-unchanged flags.
    # Git applies repository text filters for Windows/Linux consistency.
    for name in names:
        identity = subprocess.check_output(['git', 'hash-object', '--path=' + name, name], cwd=root, text=True).strip()
        if identity != staged[name]:
            raise ValueError('Release file differs from Git staging: ' + name)
    return len(names)
