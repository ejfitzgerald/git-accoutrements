import subprocess
from typing import Optional


def has_signing_key(cwd: Optional[str] = None) -> bool:
    try:
        cmd = ['git', 'config', 'user.signingkey']
        return subprocess.check_output(cmd, cwd=cwd).decode().strip() != ''
    except subprocess.CalledProcessError:
        return False
