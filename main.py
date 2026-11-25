"""Compatibility entry point; use ``python -m nightygo`` for new installs."""

from nightygo.app import main


if __name__ == "__main__":
    raise SystemExit(main())
