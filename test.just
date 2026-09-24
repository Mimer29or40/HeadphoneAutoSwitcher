# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

__run__ module="" coverage="src":
    uv run pytest --cov={{ coverage }} --cov-report=markdown --cov-report=html {{ module }}

__run_no_coverage__ module="":
    uv run pytest {{ module }}

_all: __run__
