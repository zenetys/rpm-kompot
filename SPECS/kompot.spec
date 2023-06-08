# Supported targets: el9

%define kompot_version 1.0.0
#define kompot_revision 1234567

%define drawio_version 14.7.6
%define drawio_ext_version 1.1.0
%define centreon_plugins_version 20230118
%define puppeteer_version 18.2.1
%define nagios4z_version 4.4.11
%define rsyslog8z_version 8.2304.0
%define influxdb_version 1.8.10
%define grafana_version 9.5.2

%global __brp_mangle_shebangs_exclude_from ^(/opt/kompot/www/cgi-bin/(rrd|action).cgi)$

Name: kompot
Version: %{kompot_version}
Release: 2%{?kompot_revision:.git%{kompot_revision}}%{?dist}.zenetys
Summary: Kompot monitoring utilities
Group: Applications/System
License: MIT
URL: https://github.com/zenetys/kompot

%if 0%{?kompot_revision:1}
Source0: http://git.zenetys.loc/data/projects/kompot.git/snapshot/%{kompot_revision}.tar.gz#/kompot-%{kompot_revision}.tar.gz
%else
Source0: https://github.com/zenetys/kompot/archive/refs/tags/v%{kompot_version}.tar.gz#/kompot-%{kompot_version}.tar.gz
%endif

Source100: https://github.com/jgraph/drawio/archive/v%{drawio_version}.tar.gz#/drawio-%{drawio_version}.tar.gz
Source101: https://github.com/zenetys/drawio-ext/archive/v%{drawio_ext_version}.tar.gz#/drawio-ext-%{drawio_ext_version}.tar.gz

BuildArch: noarch

BuildRequires: npm

%package setup
Summary: Glue package for Kompot
Group: Applications/System
Requires: %{name} = %{?epoch:%{epoch}:}%{version}-%{release}

# standard
Requires: cronie
Requires: diffutils
Requires: findutils
Requires: httpd
Requires: iproute
Requires: jq
Requires: logrotate
Requires: net-snmp
Requires: net-snmp-utils
Requires: openssh-server
Requires: procps-ng
Requires: psmisc
Requires: sqlite
Requires: sudo
# epel
# https://dl.fedoraproject.org/pub/epel/
Requires: nagios-plugins-by_ssh
Requires: nagios-plugins-dig
Requires: nagios-plugins-disk
Requires: nagios-plugins-dummy
Requires: nagios-plugins-http
Requires: nagios-plugins-icmp
Requires: nagios-plugins-load
Requires: nagios-plugins-ping
Requires: nagios-plugins-procs
Requires: nagios-plugins-snmp
Requires: nagios-plugins-ssh
Requires: nagios-plugins-swap
Requires: nagios-plugins-tcp
Requires: nagios-plugins-users
Requires: net-tools
# zenetys
# https://packages.zenetys.com/
Requires: catdoc
Requires: centreon-plugins = %{centreon_plugins_version}
Requires: puppeteer = %{puppeteer_version}
Requires: nagios4z = %{nagios4z_version}
Requires: rsyslog8z = %{rsyslog8z_version}
# influxdata
# https://repos.influxdata.com/
Requires: influxdb = %{influxdb_version}
# grafana
# https://rpm.grafana.com/
Requires: grafana = %{grafana_version}

%description
This package installs Kompot.

%description setup
System setup and dependencies for Kompot.

%prep
# kompot
%setup -c -T
mkdir kompot
tar xvzf %{SOURCE0} --strip-components 1 -C kompot

# drawio
%setup -T -D -a 100

# drawio-ext
%setup -T -D -a 101

%build
# kompot
cd kompot/wui
node_modules_sig=$(md5sum package.json |awk '{print $1}')
if [ -f "%_sourcedir/node_modules_${node_modules_sig}_%{_arch}.tar.xz" ]; then
    tar xvJf "%{_sourcedir}/node_modules_${node_modules_sig}_%{_arch}.tar.xz"
else
    npm install --loglevel verbose
    tar cJf "%{_sourcedir}/node_modules_${node_modules_sig}_%{_arch}.tar.xz" node_modules
fi
sed -i -r -e 's,^(\s*"name"\s*:\s*)"[^"]*",\1"kompot",' \
    -e 's,^(\s*"version"\s*:\s*)"[^"]*",\1"%{version}",' package.json
npm run build
cd ../..

%install
# kompot
install -d -m 0755 %{buildroot}/opt/kompot/{lib,share,www}
cd kompot
cp -RT configs %{buildroot}/opt/kompot/share/configs
cp -RT cgis %{buildroot}/opt/kompot/www/cgi-bin
cp -RT samples %{buildroot}/opt/kompot/share/samples
cp -RT scripts %{buildroot}/opt/kompot/bin
cp -RT plugins %{buildroot}/opt/kompot/lib/plugins
cp -RT wui/dist %{buildroot}/opt/kompot/www/htdocs
mv -T %{buildroot}/opt/kompot/share/configs/nagios/objects %{buildroot}/opt/kompot/lib/nagios
cd ..

# drawio
drawio_files=(
    favicon.ico
    images/android-chrome-196x196.png
    images/manifest.json
    images/osa_database.png
    images/osa_drive-harddisk.png
    index.html
    js/PostConfig.js
    js/app.min.js
    js/croppie/croppie.min.css
    js/extensions.min.js
    js/shapes-14-6-5.min.js
    js/stencils.min.js
    math/MathJax.js
    math/config/TeX-MML-AM_SVG-full.js
    math/jax/output/SVG/fonts/TeX/fontdata.js
    mxgraph/css/common.css
    resources/dia.txt
    resources/dia_fr.txt
    styles/grapheditor.css
)
cd drawio-%{drawio_version}
for i in "${drawio_files[@]}"; do
    install -DTp -m 644 "src/main/webapp/$i" "%{buildroot}/opt/kompot/www/drawio/$i"
done
mv %{buildroot}/opt/kompot/share/configs/drawio/js/PreConfig.js %{buildroot}/opt/kompot/www/drawio/js/
rm -rf %{buildroot}/opt/kompot/share/configs/drawio
cd ..

# drawio-ext
cd drawio-ext-%{drawio_ext_version}
    install -Dp -m 644 src/live.js %{buildroot}/opt/kompot/www/drawio/js/
cd ..

%files
/opt/kompot
%exclude /opt/kompot/bin/setup-kompot

%files setup
/opt/kompot/bin/setup-kompot

%posttrans setup
set -e
# busybox sv is installed in /usr/local/bin on kompot docker
PATH+=:/usr/local/bin
if [ "$KOMPOT_SETUP" != 0 ]; then
    /opt/kompot/bin/setup-kompot
    /opt/kompot/bin/init-kompot condrestart
fi
