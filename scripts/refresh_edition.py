"""Run the frozen engine, then stabilize edition bytes before evidence retention."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(root=ROOT):
    root = root.resolve()
    subprocess.run([sys.executable, str(root / 'scripts/refresh.py')], cwd=root, check=True)
    path = root / 'data/site.json'
    raw = path.read_bytes()
    normalized = raw.replace(b'\r\n', b'\n')
    if json.loads(normalized) != json.loads(raw):
        raise ValueError('Edition normalization changed JSON values')
    if normalized == raw:
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.edition-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(normalized)
            stream.flush()
            os.fsync(stream.fileno())
        if path.read_bytes() != raw:
            raise ValueError('Edition changed during normalization')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    run()
