# Source1 is not in the repository. ext-rpm.sh makes it on the runner while it
# builds the SRPM, with `cargo vendor --locked` against Cargo.lock, so COPR
# builds offline from the SRPM.
#
# trawlcat depends on the trawldb crate, and trawldb's tests on trawld, from
# crates.io rather than by path, so Cargo.lock and the vendor tarball carry
# registry copies of both beside the workspace members.

Name:           trawl
Version:        0.2.6
Release:        1%{?dist}
Summary:        X resources style configuration system for Regolith
# trawl is Apache-2.0. The rest covers the vendored crates: update it from the
# %%{cargo_license_summary} output in the build log whenever Cargo.lock changes.
License:        Apache-2.0 AND MIT AND MPL-2.0 AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND (MIT OR Zlib OR Apache-2.0) AND (Unlicense OR MIT)
URL:            https://github.com/regolith-linux/trawl
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  systemd-rpm-macros

%global _description %{expand:
A configuration system in the style of X resources that works the same under
Wayland and X11. Each user runs a daemon on the D-Bus session bus that holds
key and value pairs loaded from resource files.}

%description %{_description}

%package -n     trawld
Summary:        Configuration manager daemon for trawl
# Not in debian/control: trawld preprocesses resource files with /usr/bin/cpp
# unless told --nocpp, and without it a merge loads nothing. Ubuntu happens to
# have cpp installed; Fedora doesn't.
Recommends:     cpp

%description -n trawld %{_description}

This package provides the daemon, trawld, and its systemd user unit.

%package -n     trawldb
Summary:        Command line tool for managing trawl resources
Requires:       trawld = %{version}-%{release}

%description -n trawldb %{_description}

This package provides trawldb, which loads, merges, queries and removes
resources in the running daemon.

%package -n     trawlcat
Summary:        Command line tool that prints a trawl resource value
Requires:       trawld = %{version}-%{release}
Provides:       regolith-resource-loader

%description -n trawlcat %{_description}

This package provides trawlcat, which prints the value of one resource, or
a default when it is not set. It is the Regolith resource loader.

%prep
%autosetup -a1
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
# A workspace of three binaries: %%cargo_install handles one crate.
install -Dpm 0755 target/rpm/trawld %{buildroot}%{_bindir}/trawld
install -Dpm 0755 target/rpm/trawldb %{buildroot}%{_bindir}/trawldb
install -Dpm 0755 target/rpm/trawlcat %{buildroot}%{_bindir}/trawlcat
install -Dpm 0644 trawld/trawld.service %{buildroot}%{_userunitdir}/trawld.service

%check
# trawldb's integration tests talk to a running trawld on a session bus,
# which the build root doesn't have.
%cargo_test -- --lib --bins -- --test-threads=1

%post -n trawld
%systemd_user_post trawld.service

%preun -n trawld
%systemd_user_preun trawld.service

%postun -n trawld
%systemd_user_postun trawld.service

%files -n trawld
%license LICENSE.dependencies cargo-vendor.txt
%doc README.md
%{_bindir}/trawld
%{_userunitdir}/trawld.service

%files -n trawldb
%license LICENSE.dependencies cargo-vendor.txt
%{_bindir}/trawldb

%files -n trawlcat
%license LICENSE.dependencies cargo-vendor.txt
%{_bindir}/trawlcat

%changelog
* Wed Nov 04 2026 Regolith Fedora Port <port@regolith.invalid> - 0.2.6-1
- Initial package
