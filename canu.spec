%global __python /usr/local/bin/python3.10
%define __pyinstaller /usr/local/bin/pyinstaller

Name: canu
BuildArch: x86_64
License: MIT License
Summary: CSM Automatic Network Utility
Version: %(cat .version)
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Vendor: Cray Inc.
Group: Metal

%description
CSM Automatic Network Utility

%prep
%setup -q

%build
# PIP and Setuptools updates.
%{__python} -m pip install -U pip
%{__python} -m pip install -U setuptools
%{__python} -m pip install -U pyinstaller

# Build the wheel.
%{__python} -m pip install -q build
%{__python} -m build

%install
mv pyinstaller.py pyinstaller.spec
%{__pyinstaller} pyinstaller.spec

mkdir -p %{buildroot}%{_bindir}
install -m 755 dist/linux/canu %{buildroot}%{_bindir}/canu

%pre
useradd -ms /bin/bash canu

%files
%attr(755, canu, canu) %{_bindir}/canu
%license LICENSE

%changelog
