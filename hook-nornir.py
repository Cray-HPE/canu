"""nornir hook file."""
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("nornir") + collect_all("nornir_salt")
