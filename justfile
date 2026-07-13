# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

init:
    prek install

install-deps:
    uv --system-certs sync --all-extras

pre-commit:
    prek run --all-files

tests:
    uv run pytest --cov=src --cov-report=markdown

build:
    uv run pyinstaller --onefile --specpath build -n HeadphoneAutoSwitcher src/HeadphoneAutoSwitcher.py
