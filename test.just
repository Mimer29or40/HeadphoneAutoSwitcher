# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

__run__ coverage module="":
    uv run pytest --cov={{ coverage }} --cov-report=markdown --cov-report=html {{ module }}

__run-no-cov__ module="":
    uv run pytest {{ module }}

_all: (__run__ "src")

ca: (__run__ "src/ca" "test/test_ca")
ca-utils: (__run__ "src/ca" "test/test_ca/test_utils.py")

ca-0-domain: (__run__ "src/ca" "test/test_ca/test_domain.py")

ca-1-application: (__run__ "src/ca" "test/test_ca/test_application.py")

ca-2-interface: (__run__ "src/ca" "test/test_ca/test_interface.py")

ca-3-infrastructure: (__run__ "src/ca" "test/test_ca/test_infrastructure.py")

has: (__run__ "src/has" "test/test_has")
has-utils: (__run__ "src/has" "test/test_has/test_utils.py")

has-0-domain: (__run__ "src/has" "test/test_has/test_domain")

has-1-application: (__run__ "src/has" "test/test_has/test_application")

has-2-interface: (__run__ "src/has" "test/test_has/test_interface")

has-3-infrastructure: (__run__ "src/has" "test/test_has/test_infrastructure")
has-3-infrastructure-click: (__run__ "src/has" "test/test_has/test_infrastructure/test_click.py")
has-3-infrastructure-pywinusb: (__run__ "src/has" "test/test_has/test_infrastructure/test_pywinusb.py")
