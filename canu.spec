%global __python /usr/local/bin/python3.10
%define __pyinstaller /home/jenkins/.local/bin/pyinstaller

Name: canu
BuildArch: x86_64
License: MIT License
Summary: CSM Automatic Network Utility
Version: %(echo $VERSION)
Release: 1
Source: %{name}-%{version}.tar.bz2
Vendor: Cray HPE

%description
%{summary}

%prep
%setup -q

%build
# PIP and Setuptools updates.
%{__python} -m pip install -U pyinstaller

# Build the wheel.
%{__python} -m pip install -q build
%{__python} -m build

%install
mv pyinstaller.py pyinstaller.spec
%{__pyinstaller} pyinstaller.spec

mkdir -p %{buildroot}%{_bindir}
install -m 755 dist/canu %{buildroot}%{_bindir}/canu

%pre
useradd -ms /bin/bash canu

%preun
userdel canu

%files
%attr(755, canu, canu) %{_bindir}/canu
%license LICENSE

%changelog
