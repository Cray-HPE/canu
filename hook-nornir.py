"""nornir hook file."""
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("nornir", "nornir_salt", "nornir-netmiko")
