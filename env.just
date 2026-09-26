# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

init:
    prek install

pre-commit:
    prek run --all-files

sync:
    uv sync --all-extras
