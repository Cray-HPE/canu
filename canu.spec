#
# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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

Name: %(echo $NAME)
BuildArch: %(echo $ARCH)
License: MIT License
Summary: CSM Automatic Network Utility
Version: %(echo $VERSION)
Release: 1
Source: %{name}-%{version}.tar.bz2
Vendor: Hewlett Packard Enterprise Development LP

%description
A network device configuration and firmware utility. Designed for use on Cray-HPE Shasta systems, canu
will faciliate paddling through network topology plumbing.

%prep
%setup -q

%install
# install the 'canu' wrapper script to the bindir
mkdir -p %{buildroot}%{_bindir}
install -m 755 ./canu %{buildroot}%{_bindir}/canu

%pre
getent passwd canu >/dev/null || \
    useradd -U -m -s /bin/bash -c "CANU user" canu

%files
%attr(755, canu, canu) %{_bindir}/canu
%license LICENSE

%changelog
