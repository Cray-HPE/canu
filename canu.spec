#
# MIT License
#
# (C) Copyright 2022 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
%global __python /usr/local/bin/python3.10
%define __pyinstaller /home/jenkins/.local/bin/pyinstaller

Name: %(echo $NAME)
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
%{__python} -m pip install -q build
%{__python} -m build
%{__python} -m pip install dist/%{name}*.tar.gz
git status
git diff-index --name-only HEAD

cp -pv pyinstaller.py pyinstaller.spec
git status
git diff-index --name-only HEAD
%{__pyinstaller} --clean -y --dist ./dist/linux --workpath /tmp pyinstaller.spec
rm pyinstaller.spec
chown -R --reference=. ./dist/linux

%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 dist/linux/canu %{buildroot}%{_bindir}/canu

%pre
getent passwd canu >/dev/null || \
    useradd -U -m -s /bin/bash -c "CANU user" canu

%files
%attr(755, canu, canu) %{_bindir}/canu
%license LICENSE

%changelog
