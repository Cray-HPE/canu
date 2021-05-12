Name: canu
BuildArch: x86_64
License: MIT License
Summary: CSM Automatic Network Utility
Version: %(cat .version)
Release: 1
Vendor: Cray Inc.
Group: Metal

%define _sourcedir %(pwd)
%define _rpmdir %(pwd)/dist/linux


%description
CSM Automatic Network Utility

%prep

%build

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/licenses/%{name}-%{version}
cp %{_sourcedir}/LICENSE %{buildroot}%{_datadir}/licenses/%{name}-%{version}/LICENSE
install -m 755  %{_sourcedir}/dist/linux/canu %{buildroot}%{_bindir}/canu

%files
%{_datadir}/licenses/%{name}-%{version}/LICENSE
%{_bindir}/canu


%changelog
