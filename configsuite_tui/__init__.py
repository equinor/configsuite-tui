from configsuite_tui.tui import tui

try:
    from ._version import version as __version__
except ImportError:
    from .__about__ import __version__
