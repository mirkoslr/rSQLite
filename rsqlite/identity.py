"""
rSQLite identity management.

Responsibilities:
- Load an existing Reticulum Identity
- Create and save a new Identity if none exists
"""

import RNS
from pathlib import Path

def prepare_identity(identity_file):
    """Load an existing Reticulum identity or create a new one 
    if it doesn't exist."""
    path=Path(identity_file).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        identity=RNS.Identity.from_file(str(path))
        if identity is None:
            raise RuntimeError(f'Unable to load identity: {path}')
        RNS.log(f'Loaded identity {path}')
        return identity
    identity=RNS.Identity()
    identity.to_file(str(path))
    RNS.log(f'Created identity {path}')
    return identity
