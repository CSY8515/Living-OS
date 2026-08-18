"""Living OS v2.0.9.9 Streamlit entry point."""

from importlib import import_module, reload


EXPECTED_VERSION = "v2.0.9.9"


def _current_shell():
    """Refresh only stale deploy modules after a Streamlit repository update."""

    version_module = import_module("subsystems.foundation.engines.version")
    if getattr(version_module, "PRODUCT_VERSION", "") != EXPECTED_VERSION:
        reload(version_module)

    shell_module = import_module("app.shell")
    if getattr(shell_module, "VERSION", "") != EXPECTED_VERSION:
        shell_module = reload(shell_module)
    return shell_module


_shell = _current_shell()
VERSION = _shell.VERSION
main = _shell.main


if __name__ == "__main__":
    main()
