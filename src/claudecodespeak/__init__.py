#
# (c) 2026 Yoichi Tanibayashi
#
from importlib.metadata import PackageNotFoundError, version

if __package__:
    try:
        __version__ = version(__package__)
    except PackageNotFoundError:
        __version__ = "0.0.0"
else:
    __version__ = "_._._"


__all__ = ["__version__"]
