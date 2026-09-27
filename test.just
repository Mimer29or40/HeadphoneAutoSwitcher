# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

__run__ module="" coverage="src":
    uv run pytest --cov={{ coverage }} --cov-report=markdown --cov-report=html {{ module }}

__run-no-cov__ module="":
    uv run pytest {{ module }}

_all: __run__

ca: (__run__ "test/test_ca" "src/ca")
ca-utils: (__run__ "test/test_ca/test_utils.py" "src/ca")
ca-0-domain: (__run__ "test/test_ca/test_domain.py" "src/ca")
ca-1-application: (__run__ "test/test_ca/test_application.py" "src/ca")
ca-2-interface: (__run__ "test/test_ca/test_interface.py" "src/ca")
ca-3-infrastructure: (__run__ "test/test_ca/test_infrastructure.py" "src/ca")
