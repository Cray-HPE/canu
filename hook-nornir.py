"""nornir hook file."""
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = collect_submodules("nornir")
datas = copy_metadata("nornir")
