Name: canu
BuildArch: x86_64
License: MIT License
Summary: CSM Automatic Network Utility
Version: %(cat canu/.version)
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Vendor: Cray Inc.
Group: Metal

%description
CSM Automatic Network Utility

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}%{_bindir}
install -m 755 dist/linux/canu %{buildroot}%{_bindir}/canu

%files
%{_bindir}/canu
%license LICENSE

%changelog
