# use PowerShell instead of sh:
set shell := ["powershell.exe", "-c"]

export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')
export PYTHONPATH := join(justfile_directory(), "src")

__build__ name script:
    uv run pyinstaller \
        --specpath build \
        --hidden-import win32timezone \
        -n {{name}} \
        {{ script }}

pkg:
    uv build --all-packages --sdist --wheel --clear
#    uv build --all-packages --sdist --wheel --force-pep517 --clear

exe_cli: (__build__ "HeadphoneAutoSwitcher-cli"  "src/has/bootstrap_cli.py")
exe_web: (__build__ "HeadphoneAutoSwitcher-web"  "src/has/bootstrap_web.py")
