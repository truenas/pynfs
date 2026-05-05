# Compatibility shim.
#
# The original pynfs ships a top-level ``config`` module here.  When
# pynfs is installed via ``pip install ...`` the module name ``config``
# collides with files of the same name on the consumer's ``sys.path``
# (for example, the TrueNAS middleware test runner generates a
# top-level ``tests/config.py`` before invoking pytest, which shadows
# pynfs's module on import resolution).
#
# To work around that, the shipped install renames this module to
# ``_pynfs_config`` and pynfs's own internals (fs.py, nfs4server.py)
# import from ``_pynfs_config`` directly.  This file remains for
# in-tree development use (``cd nfs4.1 && python testserver.py``) so
# any third-party scripts that still do ``from config import ...``
# keep working without touching their imports.  ``pyproject.toml``
# deliberately does NOT include ``config`` in its ``py-modules`` list
# - only ``_pynfs_config`` is shipped.
from _pynfs_config import *  # noqa: F401,F403
from _pynfs_config import (  # noqa: F401
    ConfigAction,
    ConfigLine,
    MetaConfig,
    ServerConfig,
    ServerPerClientConfig,
    OpsConfigServer,
    Actions,
)
