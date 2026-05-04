#!/usr/bin/env python3
"""Build entry point for pynfs.

All distribution metadata lives in ``pyproject.toml``.  This file's only
job is to regenerate the XDR Python bindings (``*_const.py``,
``*_type.py``, ``*_pack.py``) from their ``.x`` source files before
setuptools collects modules, so that the generated files are always
present in the source tree -- this matters for plain wheels, sdists
*and* editable installs (PEP 660), which all import setup.py via the
setuptools build backend before snapshotting the package contents.
"""
from __future__ import annotations

import os
import sys

from setuptools import setup

ROOT = os.path.dirname(os.path.abspath(__file__))

# xdrgen lives at <root>/xdr/xdrgen.py and is intentionally NOT installed
# as part of the wheel -- it is only needed at build time, and the .x
# sources we ship are enough for downstream consumers to regenerate.
_XDRGEN_DIR = os.path.join(ROOT, "xdr")
if _XDRGEN_DIR not in sys.path:
    sys.path.insert(0, _XDRGEN_DIR)

# (directory containing the .x file, .x filename) pairs.
_XDR_SOURCES: list[tuple[str, str]] = [
    (os.path.join(ROOT, "nfs4.1", "xdrdef"), name)
    for name in (
        "nfs4.x",
        "nfs3.x",
        "mnt3.x",
        "sctrl.x",
        "portmap.x",
        "pnfs_block.x",
    )
] + [
    (os.path.join(ROOT, "rpc"), name) for name in ("rpc.x", "gss.x")
]


def _needs_regen(directory: str, xdr_filename: str) -> bool:
    src = os.path.join(directory, xdr_filename)
    base = xdr_filename[: xdr_filename.rfind(".")]
    targets = [
        os.path.join(directory, base + suffix)
        for suffix in ("_const.py", "_type.py", "_pack.py")
    ]
    if not all(os.path.exists(t) for t in targets):
        return True
    src_mtime = os.path.getmtime(src)
    return any(os.path.getmtime(t) < src_mtime for t in targets)


def _regenerate_xdr_modules() -> None:
    import xdrgen  # noqa: WPS433  build-time only

    cwd = os.getcwd()
    try:
        for directory, xdr_filename in _XDR_SOURCES:
            if not _needs_regen(directory, xdr_filename):
                continue
            os.chdir(directory)
            xdrgen.run(xdr_filename)
            for stale in ("parser.out", "parsetab.py"):
                stale_path = os.path.join(directory, stale)
                if os.path.exists(stale_path):
                    os.remove(stale_path)
    finally:
        os.chdir(cwd)


_regenerate_xdr_modules()
setup()
