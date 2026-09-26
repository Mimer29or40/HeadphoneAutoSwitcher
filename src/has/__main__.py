"""Headphone Auto Switcher Application entry point."""

from __future__ import annotations

from multiprocessing import freeze_support

from has.bootstrap import cli_framework_main

freeze_support()
cli_framework_main()
