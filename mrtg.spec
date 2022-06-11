%global _use_internal_dependency_generator 0
%global contentdir  %{_localstatedir}/www/mrtg
%global libdir      %{_localstatedir}/lib/mrtg
%global __find_requires %_sourcedir/filter-requires-mrtg.sh
%global __find_provides %_sourcedir/filter-provides-mrtg.sh

Name:               mrtg
Version:            2.17.10
Release:            1
Summary:            Multi Router Traffic Grapher

License:            GPLv2+
URL:                http://oss.oetiker.ch/mrtg/
Source0:            http://oss.oetiker.ch/mrtg/pub/mrtg-%{version}.tar.gz
Source1:            mrtg.cfg
Source2:            filter-requires-mrtg.sh
Source3:            mrtg-httpd.conf
Source4:            filter-provides-mrtg.sh
Source5:            mrtg.tmpfiles
Source6:            mrtg.service
Source7:            mrtg.timer

Patch0:             mrtg-2.15.0-lib64.patch
Patch1:             mrtg-2.17.2-socket6-fix.patch
Patch2:             mrtg-2.17.4-cfgmaker-ifhighspeed.patch

BuildRequires:      gd-devel libpng-devel perl-generators systemd-units gcc
Requires(post):     systemd-units
Requires(preun):    systemd-units
Requires(postun):   systemd-units
Requires:           perl-Socket6 perl-IO-Socket-INET6 gd

%description
MRTG is a tool to monitor SNMP network devices and draw pretty pictures showing 
how much traffic has passed through each interface.

%package_help

%prep
%autosetup -n %{name}-%{version} -p1

rm -rf contrib/nt-services

for i in doc/mrtg-forum.1 doc/mrtg-squid.1 CHANGES; do
    iconv -f iso-8859-1 -t utf-8 < "$i" > "${i}_"
    mv "${i}_" "$i"
done

%build
%configure
make LIBS='-lgd -lm'
pushd contrib
find . -type f -exec \
    %{__perl} -e 's,^#!/\s*\S*perl\S*,#!%{__perl},gi' -p -i \{\} \;
find . -name "*.pl" -exec %{__perl} -e 's;\015;;gi' -p -i \{\} \;
find . -type f | xargs chmod a-x
popd

%install
chmod +x %_sourcedir/filter-*-mrtg.sh
%make_install

pushd %{buildroot}
mkdir -p .%{contentdir}
mkdir -p .%{_sysconfdir}/mrtg
mkdir -p .%{_sysconfdir}/httpd/conf.d
mkdir -p .%{_localstatedir}/lib/mrtg
mkdir -p .%{_localstatedir}/lock/mrtg

install -m 644 %_builddir/%{name}-%{version}/images/* .%{contentdir}/
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/mrtg/mrtg.cfg
install -m 644 %{SOURCE3} .%{_sysconfdir}/httpd/conf.d/mrtg.conf
mkdir -p ./%{_tmpfilesdir}
install -p -D -m 644 %{SOURCE5} ./%{_tmpfilesdir}/mrtg.conf

mkdir -p .%{_unitdir}
install -p -m 644 %{SOURCE6} .%{_unitdir}/mrtg.service
install -p -m 644 %{SOURCE7} .%{_unitdir}/mrtg.timer

for i in mrtg cfgmaker indexmaker mrtg-traffic-sum; do
    sed -i 's;@@lib@@;%{_lib};g' .%{_bindir}/"$i"
done

sed -i 's;@@lib@@;%{_lib};g' .%{_mandir}/man1/*.1
popd

%post
install -d -m 0755 -o root -g root /var/lock/mrtg
restorecon /var/lock/mrtg
%systemd_post mrtg.service

%preun
if [ $1 -eq 0 ]; then
  rm -rf /var/lock/mrtg
fi
%systemd_preun mrtg.service

%postun
%systemd_postun_with_restart mrtg.service 

%files
%defattr(-,root,root)
%license COPYING COPYRIGHT
%ghost /var/lock/mrtg
%{_tmpfilesdir}/mrtg.conf
%dir %{_sysconfdir}/mrtg
%config(noreplace) %{_sysconfdir}/mrtg/mrtg.cfg
%config(noreplace) %{_sysconfdir}/httpd/conf.d/mrtg.conf
%{_bindir}/*
%{_libdir}/mrtg2
%dir %{_localstatedir}/lib/mrtg
%{_unitdir}/mrtg.timer
%{_unitdir}/mrtg.service
%{contentdir}
%exclude %{_datadir}/doc/mrtg2
%exclude %{_datadir}/mrtg2/icons
%exclude %{_libdir}/mrtg2/Pod

%files help
%defattr(-,root,root)
%doc contrib CHANGES README THANKS
%{_mandir}/*/*

%changelog
* Sat Jun 11 2022 YukariChiba <i@0x7f.cc> - 2.17.10-1
- Upgrade version

* Thu Nov 21 2019 openEuler Buildteam <buildteam@openeuler.org> - 2.17.7-3
- Package init
