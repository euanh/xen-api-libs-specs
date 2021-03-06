Name:           xenopsd
Version:        0.16.0
Release:        1%{?dist}
Summary:        Simple VM manager
License:        LGPL
URL:            https://github.com/xapi-project/xenopsd
Source0:        https://github.com/xapi-project/xenopsd/archive/v%{version}/xenopsd-%{version}.tar.gz
Source1:        xenopsd-xc.service
Source2:        xenopsd-xenlight.service
Source3:        xenopsd-simulator.service
Source4:        xenopsd-sysconfig
Source5:        xenopsd-64-conf
BuildRequires:  ocaml
BuildRequires:  optcomp
BuildRequires:  ocaml-findlib
BuildRequires:  ocaml-findlib-devel
BuildRequires:  ocaml-rpc-devel
BuildRequires:  ocaml-xcp-idl-devel
BuildRequires:  ocaml-cmdliner-devel
BuildRequires:  ocaml-cohttp-devel
BuildRequires:  forkexecd-devel
BuildRequires:  ocaml-oclock-devel
BuildRequires:  ocaml-uuidm-devel
BuildRequires:  ocaml-qmp-devel
BuildRequires:  ocaml-sexplib-devel
BuildRequires:  xen-ocaml-devel
BuildRequires:  ocaml-xenstore-clients-devel
BuildRequires:  ocaml-xenstore-devel
BuildRequires:  ocaml-xcp-inventory-devel
BuildRequires:  xen-devel
BuildRequires:  xen-libs-devel
BuildRequires:  xen-dom0-libs-devel
BuildRequires:  ocaml-uutf-devel
BuildRequires:  ocaml-xcp-rrd-devel
BuildRequires:  python-devel
BuildRequires:  systemd ocaml-bisect-ppx-devel
Requires:       message-switch
Requires:       xenops-cli
Requires:       xen-dom0-tools

%{?systemd_requires}

%description
Simple VM manager for the xapi toolstack.

%package        xc
Summary:        Xenopsd using xc
Requires:       %{name} = %{version}-%{release}
Requires:       forkexecd
Requires:       xen-libs
%description    xc
Simple VM manager for Xen using libxc.

%package        xc-cov
Summary:        Xenopsd using xc
Requires:       %{name} = %{version}-%{release}
Requires:       forkexecd
Requires:       xen-libs

%description    xc-cov
Simple VM manager for Xen using libxc with coverage
profiling.


%package        simulator
Summary:        Xenopsd simulator
Requires:       %{name} = %{version}-%{release}
%description    simulator
A synthetic VM manager for testing.

%package        simulator-cov
Summary:        Xenopsd simulator
Requires:       %{name} = %{version}-%{release}

%description    simulator-cov
A synthetic VM manager for testing with coverage profiling.



%package        xenlight
Summary:        Xenopsd using libxenlight
Requires:       %{name} = %{version}-%{release}

%description    xenlight
Simple VM manager for Xen using libxenlight

%package        xenlight-cov
Summary:        Xenopsd using libxenlight
Requires:       %{name} = %{version}-%{release}

%description    xenlight-cov
Simple VM manager for Xen using libxenlight with coverage profiling.


%prep
%autosetup

%build
# this is a hack: we build and install two builds into the source
# directory under build-bin/ and build-cov/. In the install step all we do is
# copying files from it.

mkdir build-bin build-cov
./configure --libexecdir %{_libexecdir}/%{name}

# regular build
make
make install DESTDIR=$PWD/build-bin LIBEXECDIR=%{_libexecdir}/%{name} SBINDIR=%{_sbindir} MANDIR=%{_mandir}
make clean

# now build for coverage profiling
make coverage
make
make install DESTDIR=$PWD/build-cov LIBEXECDIR=%{_libexecdir}/%{name} SBINDIR=%{_sbindir} MANDIR=%{_mandir}

%install
# this installs the files from the bin build
(cd build-bin/; tar cf - .) | (cd %{buildroot}; tar xf -)

# rename regular binaries
mv %{buildroot}%{_sbindir}/xenopsd-xc                     %{buildroot}%{_sbindir}/xenopsd-xc.bin
mv %{buildroot}%{_libexecdir}/%{name}/set-domain-uuid     %{buildroot}%{_libexecdir}/%{name}/set-domain-uuid.bin

# install selected binaries with coverage profiling from coverage build
install -D ./xenops_xc_main.native        %{buildroot}%{_sbindir}/xenopsd-xc.cov
install -D ./set_domain_uuid.native       %{buildroot}%{_libexecdir}/%{name}/set-domain-uuid.cov

# touch files that are created dynamically and are ghost'ed in files
touch %{buildroot}%{_sbindir}/xenopsd-xenlight
touch %{buildroot}%{_sbindir}/xenopsd-simulator
touch %{buildroot}%{_sbindir}/xenopsd-xc
touch %{buildroot}%{_libexecdir}/%{name}/set-domain-uuid

# this is the same for both builds - should really be in Makefile
gzip %{buildroot}%{_mandir}/man1/*.1

%{__install} -D -m 0755 %{SOURCE1} %{buildroot}%{_unitdir}/xenopsd-xc.service
%{__install} -D -m 0755 %{SOURCE2} %{buildroot}%{_unitdir}/xenopsd-xenlight.service
%{__install} -D -m 0755 %{SOURCE3} %{buildroot}%{_unitdir}/xenopsd-simulator.service
%{__install} -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/xenopsd
%{__install} -D -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/xenopsd.conf

%files
%doc README.md LICENSE
%{_sysconfdir}/udev/rules.d/xen-backend.rules
%{_libexecdir}/%{name}/vif
%{_libexecdir}/%{name}/vif-real
%{_libexecdir}/%{name}/block
%{_libexecdir}/%{name}/tap
%{_libexecdir}/%{name}/qemu-dm-wrapper
%{_libexecdir}/%{name}/qemu-vif-script
%{_libexecdir}/%{name}/setup-vif-rules
%{_libexecdir}/%{name}/setup-pvs-proxy-rules
%{_libexecdir}/%{name}/common.py
%{_libexecdir}/%{name}/common.pyo
%{_libexecdir}/%{name}/common.pyc
%config(noreplace) %{_sysconfdir}/sysconfig/xenopsd
%config(noreplace) %{_sysconfdir}/xenopsd.conf

# ---

%files xc
%{_sbindir}/xenopsd-xc.bin
%ghost %{_sbindir}/xenopsd-xc
%{_unitdir}/xenopsd-xc.service
%{_mandir}/man1/xenopsd-xc.1.gz
%{_libexecdir}/%{name}/set-domain-uuid.bin
%ghost %{_libexecdir}/%{name}/set-domain-uuid

%post xc
case $1 in
  1) # install
    ln -fs %{_sbindir}/xenopsd-xc.bin %{_sbindir}/xenopsd-xc
    ln -fs %{_libexecdir}/%{name}/set-domain-uuid.bin %{_libexecdir}/%{name}/set-domain-uuid
    ;;
  2) # upgrade
    ln -fs %{_sbindir}/xenopsd-xc.bin %{_sbindir}/xenopsd-xc
    ln -fs %{_libexecdir}/%{name}/set-domain-uuid.bin %{_libexecdir}/%{name}/set-domain-uuid
    ;;
esac
%systemd_post xenopsd-xc.service

%preun xc
%systemd_preun xenopsd-xc.service

%postun xc
%systemd_postun_with_restart xenopsd-xc.service

%files xc-cov
%{_sbindir}/xenopsd-xc.cov
%{_unitdir}/xenopsd-xc.service
%{_mandir}/man1/xenopsd-xc.1.gz
%{_libexecdir}/%{name}/set-domain-uuid.cov
%ghost %{_sbindir}/xenopsd-xc

%post xc-cov
case $1 in
  1) # install
    ln -fs %{_sbindir}/xenopsd-xc.cov %{_sbindir}/xenopsd-xc
    ln -fs %{_libexecdir}/%{name}/set-domain-uuid.cov %{_libexecdir}/%{name}/set-domain-uuid
    ;;
  2) # upgrade
    ln -fs %{_sbindir}/xenopsd-xc.cov %{_sbindir}/xenopsd-xc
    ln -fs %{_libexecdir}/%{name}/set-domain-uuid.cov %{_libexecdir}/%{name}/set-domain-uuid
    ;;
esac
%systemd_post xenopsd-xc.service

%preun xc-cov
%systemd_preun xenopsd-xc.service

%postun xc-cov
%systemd_postun_with_restart xenopsd-xc.service

%files simulator
%{_sbindir}/xenopsd-simulator
%{_unitdir}/xenopsd-simulator.service
%{_mandir}/man1/xenopsd-simulator.1.gz

%post simulator
%systemd_post xenopsd-simulator.service

%preun simulator
%systemd_preun xenopsd-simulator.service

%postun simulator
%systemd_postun_with_restart xenopsd-simulator.service

%files xenlight
%{_sbindir}/xenopsd-xenlight
%{_unitdir}/xenopsd-xenlight.service
%{_mandir}/man1/xenopsd-xenlight.1.gz

%post xenlight
%systemd_post xenopsd-xenlight.service

%preun xenlight
%systemd_preun xenopsd-xenlight.service

%postun xenlight
%systemd_postun_with_restart xenopsd-xenlight.service

%changelog
* Thu Oct 13 2016 Euan Harris <euan.harris@citrix.com> - 0.16.0-1
- Add PVS support

* Wed Sep 14 2016 Euan Harris <euan.harris@citrix.com> - 0.15.0-1
- Add force option to VM.start
- Add device information in VIF.state

* Fri Sep 02 2016 Euan Harris <euan.harris@citrix.com> - 0.14.0-1
- Update to 0.14.0

* Mon Aug 22 2016 Rafal Mielniczuk <rafal.mielniczuk@citrix.com> - 0.13.0-2
- Package for systemd

* Fri Aug 12 2016 Christian Lindig <christian.lindig@citrix.com> - 0.13.0-1
- Version bump; xenopsd maintains state for nested_virt, nomigrate

* Fri Jul 22 2016 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.12.2-1
- New release

* Thu May 26 2016 Christian Lindig <christian.lindig@citrix.com> - 0.12.1-2
- Fix post xc-cov: have to rm existing symlink just like in upgrade

* Fri May 20 2016 Christian Lindig <christian.lindig@citrix.com> - 0.12.1-1
- New upstream release that supports coverage analysis
- Introduce subpackages *-cov for coverage analysis

* Mon May 16 2016 Si Beaumont <simon.beaumont@citrix.com> - 0.12.0-2
- Re-run chkconfig on upgrade

* Thu Sep 24 2015 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.12.0-1
- New upstream release, and an extra file

* Thu Apr 30 2015 Jon Ludlam <jonathan.ludlam@citrix.com> - UNRELEASED
- Revert some PCI passthrough patches

* Mon Sep 8 2014 David Scott <dave.scott@citrix.com> - 0.9.43-4
- Add a search-path to the xenopsd.conf

* Thu Sep 4 2014 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.9.43-3
- Remove xen-missing-headers dependency

* Thu Sep 4 2014 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.9.43-2
- Reinstate xenlight package in CentOS

* Sun Aug 24 2014 David Scott <dave.scott@citrix.com> - 0.9.43-1
- Update to 0.9.43 which supports OCaml 4.01.0

* Fri Aug 22 2014 David Scott <dave.scott@citrix.com> - 0.9.41-1
- Update to 0.9.41: now pygrub, eliloader, hvmloader and vncterm
  are optional

* Fri Aug 22 2014 David Scott <dave.scott@citrix.com> - 0.9.39-5
- vncterm-wrapper: ensure the groups are added on startup.

* Fri Aug 22 2014 David Scott <dave.scott@citrix.com> - 0.9.39-4
- Add a vncterm-wrapper: needed to locate the qemu keymaps

* Thu Aug 21 2014 David Scott <dave.scott@citrix.com> - 0.9.39-2
- Include {vbd,vif}-xl in the package

* Wed Aug 20 2014 David Scott <dave.scott@citrix.com> - 0.9.39-2
- Package xenopsd-xenlight

* Wed Aug 20 2014 Jon Ludlam <jonathan.ludlam@citrix.com> - 0.9.39-1
- Update to 0.9.39 which compiles without warnings

* Tue Aug 19 2014 David Scott <dave.scott@citrix.com> - 0.9.38-1
- Update to 0.9.38 with better libxl support

* Sat Jun 21 2014 David Scott <dave.scott@citrix.com> - 0.9.37-1
- Depend on the ocaml-xen-lowlevel-libs-runtime package
- Don't include xenguest: this now comes from ocaml-xen-lowlevel-libs

* Fri Jun  6 2014 Jonathan Ludlam <jonathan.ludlam@citrix.com> - 0.9.37-1
- Update to 0.9.37

* Fri Jan 17 2014 Euan Harris <euan.harris@eu.citrix.com> - 0.9.34-1
- Update to 0.9.34, restoring fixes from the 0.9.32 line which were
  not merged to trunk before 0.9.33 was tagged

* Wed Dec 4 2013 Euan Harris <euan.harris@eu.citrix.com> - 0.9.33-1
- Update to 0.9.33, with fixes for suspending and resuming HVM guests

* Mon Oct 28 2013 David Scott <dave.scott@eu.citrix.com> - 0.9.32-1
- Update to 0.9.32, with udev fix (no more "task was asynchronously cancelled")

* Mon Oct 21 2013 David Scott <dave.scott@eu.citrix.com>
- Update to 0.9.31
- move scripts back to libexecdir

* Sun Oct 20 2013 David Scott <dave.scott@eu.citrix.com>
- give up on making libxl work, since it requires xen-4.4
- move scripts from libexecdir to libdir

* Fri Oct 18 2013 David Scott <dave.scott@eu.citrix.com>
- update to 0.9.29

* Fri Oct 18 2013 David Scott <dave.scott@eu.citrix.com>
- update to 0.9.28

* Wed Sep 25 2013 David Scott <dave.scott@eu.citrix.com>
- modprobe blk{tap,back} in the xenopsd-xc init.d script since
  we need these to make virtual disks work
- update to 0.9.27

* Tue Sep 24 2013 David Scott <dave.scott@eu.citrix.com>
- Update to 0.9.26, which includes fixes for networking and libxl

* Fri Sep 20 2013 Euan Harris <euan.harris@citrix.com>
- Generate xenopsd.conf automatically

* Mon Sep 16 2013 Euan Harris <euan.harris@citrix.com>
- Update to 0.9.25, which includes linker paths required on Debian

* Tue Sep 10 2013 David Scott <dave.scott@eu.citrix.com>
- Update to 0.9.24

* Fri Jun 21 2013 David Scott <dave.scott@eu.citrix.com>
- Update to 0.9.5, which includes xenopsd-xenlight

* Thu May 30 2013 David Scott <dave.scott@eu.citrix.com>
- Initial package

