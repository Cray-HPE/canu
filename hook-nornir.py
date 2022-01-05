"""nornir hook file."""
from PyInstaller.utils.hooks import (
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

datas = (
    copy_metadata("nornir")
    + copy_metadata("nornir_salt")
    + copy_metadata("nornir_netmiko")
)

hiddenimports = (
    collect_submodules("nornir")
    + collect_submodules("nornir_salt")
    + collect_submodules("nornir_netmiko")
)

binaries = (
    collect_dynamic_libs("nornir")
    + collect_dynamic_libs("nornir_salt")
    + collect_dynamic_libs("nornir_netmiko")
)
