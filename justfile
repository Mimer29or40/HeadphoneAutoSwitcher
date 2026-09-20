# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

init:
    prek install

sync:
    uv sync --all-extras

build:
    uv run pyinstaller \
        --onefile \
        --specpath build \
        --hidden-import win32timezone \
        -n HeadphoneAutoSwitcher \
        src/HeadphoneAutoSwitcher.py
