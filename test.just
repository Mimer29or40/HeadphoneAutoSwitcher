# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

__run_test__ module="" coverage="src":
    uv run pytest --cov={{ coverage }} --cov-report=markdown --cov-report=html {{ module }}

__run_test_no_coverage__ module="":
    uv run pytest {{ module }}

_all: __run_test__

_ca: (__run_test__ "test/test__ca" "src/_ca")
_ca_layer0_domain: (__run_test__ "test/test__ca/test_domain.py" "src/_ca")
_ca_layer1_application: (__run_test__ "test/test__ca/test_application.py" "src/_ca")
_ca_layer2_interface: (__run_test__ "test/test__ca/test_interface.py" "src/_ca")
_ca_layer3_infrastructure: (__run_test__ "test/test__ca/test_infrastructure.py" "src/_ca")
_ca_utils: (__run_test__ "test/test__ca/test_utils.py" "src/_ca")

architecture: (__run_test_no_coverage__ "test/test_architecture.py")

layer0_domain: (__run_test__ "test/test_domain")
layer0_domain_entity: (__run_test__ "test/test_domain/test_entity.py")
layer0_domain_exception: (__run_test__ "test/test_domain/test_exception.py")
layer0_domain_service: (__run_test__ "test/test_domain/test_service.py")
layer0_domain_value: (__run_test__ "test/test_domain/test_value.py")

layer1_application: (__run_test__ "test/test_application")
layer1_application_dto: (__run_test__ "test/test_application/test_dto.py")
layer1_application_port: (__run_test__ "test/test_application/test_port.py")
layer1_application_repository: (__run_test__ "test/test_application/test_repository.py")
layer1_application_use_case: (__run_test__ "test/test_application/test_use_case.py")

layer2_interface: (__run_test__ "test/test_interface")
layer2_interface_controller: (__run_test__ "test/test_interface/test_controller.py")
layer2_interface_presenter: (__run_test__ "test/test_interface/test_presenter.py")
layer2_interface_view_model: (__run_test__ "test/test_interface/test_view_model.py")

layer3_infrastructure: (__run_test__ "test/test_infrastructure")
layer3_infrastructure_runner: (__run_test__ "test/test_infrastructure/test_runner.py")
