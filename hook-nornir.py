"""nornir hook file."""
from PyInstaller.utils.hooks import (
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

datas = copy_metadata("nornir") + copy_metadata("nornir_salt")

hiddenimports = collect_submodules("nornir") + collect_submodules("nornir_salt")

binaries = collect_dynamic_libs("nornir") + collect_dynamic_libs("nornir_salt")