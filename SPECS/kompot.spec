# Supported targets: el9

%{!?kompot_core_version: %define kompot_core_version 1.0.18}
#define kompot_core_revision 1234567
%{!?kompot_wui_version: %define kompot_wui_version 1.0.9}
#define kompot_wui_revision 1234567

%{!?drawio_version: %define drawio_version 24.7.17}
%{!?drawio_ext_version: %define drawio_ext_version 1.2.1}

%global __brp_mangle_shebangs_exclude_from ^(/opt/kompot/www/cgi-bin/(rrd|action).cgi)$

%define zenetys_git_source() %{lua:
    local version_source = 'https://github.com/zenetys/%s/archive/refs/tags/v%s.tar.gz#/%s-%s.tar.gz'
    local revision_source = 'http://git.zenetys.loc/data/projects/%s.git/snapshot/%s.tar.gz#/%s-%s.tar.gz'
    local name = rpm.expand("%{1}")
    local iname = name:gsub("%W", "_")
    local version = rpm.expand("%{"..iname.."_version}")
    local revision = rpm.expand("%{?"..iname.."_revision}")
    if revision == '' then print(version_source:format(name, version, name, version))
    else print(revision_source:format(name, revision, name, revision)) end
}

Name: kompot
Version: %{kompot_core_version}
Release: 1%{?kompot_core_revision:.git%{kompot_core_revision}}%{?dist}.zenetys
Summary: Kompot monitoring utilities
Group: Applications/System
License: MIT
URL: https://github.com/zenetys/kompot

Source0: %zenetys_git_source kompot-core
Source10: %zenetys_git_source kompot-wui
Source100: https://github.com/jgraph/drawio/archive/v%{drawio_version}.tar.gz#/drawio-%{drawio_version}.tar.gz
Source101: https://github.com/zenetys/drawio-ext/archive/v%{drawio_ext_version}.tar.gz#/drawio-ext-%{drawio_ext_version}.tar.gz

BuildArch: noarch

# standard
BuildRequires: gawk
# yarn is available in epel
BuildRequires: yarnpkg

# standard
Requires(pre): gawk

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
Requires: s-nail
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
Requires: nagios-plugins-ntp
Requires: nagios-plugins-ping
Requires: nagios-plugins-procs
Requires: nagios-plugins-snmp
Requires: nagios-plugins-ssh
Requires: nagios-plugins-swap
Requires: nagios-plugins-tcp
Requires: nagios-plugins-users
Requires: net-tools
# zenetys
# https://packages.zenetys.com/projects/kompot/
Requires: catdoc
Requires: centreon-plugins
Requires: centreon-vmware
Requires: puppeteer
Requires: nagios4z
Requires: rsyslog8z
Requires: smstools
# influxdata
# https://repos.influxdata.com/
# required version is copied in kompot repo under external/
Requires: influxdb
# grafana
# https://rpm.grafana.com/
# required version is copied in kompot repo under external/
Requires: grafana

%description
This package installs Kompot.

%description setup
System setup and dependencies for Kompot.

%prep
%setup -c -T

# kompot-core
mkdir kompot-core
tar xvzf %{SOURCE0} --strip-components 1 -C kompot-core

# kompot-wui
mkdir kompot-wui
tar xvzf %{SOURCE10} --strip-components 1 -C kompot-wui

# drawio
%setup -T -D -a 100

# drawio-ext
%setup -T -D -a 101

%build
# kompot-wui
cd kompot-wui
node_modules_sig=$(md5sum package.json |awk '{print $1}')
if [ -f "%_sourcedir/node_modules_${node_modules_sig}_%{_arch}.tar.xz" ]; then
    tar xvJf "%{_sourcedir}/node_modules_${node_modules_sig}_%{_arch}.tar.xz"
else
    yarn
    tar cJf "%{_sourcedir}/node_modules_${node_modules_sig}_%{_arch}.tar.xz" node_modules yarn.lock
fi
(
    export VITE_APP_NAME=kompot
    export VITE_APP_VERSION=%{version}
    yarn build
)
cd ..

%install
# kompot-core
cd kompot-core
install -d -m 0755 %{buildroot}/opt/kompot/{lib,share,www}
cp -RT doc %{buildroot}/opt/kompot/share/doc
cp -RT configs %{buildroot}/opt/kompot/share/configs
cp -RT cgis %{buildroot}/opt/kompot/www/cgi-bin
cp -RT samples %{buildroot}/opt/kompot/share/samples
cp -RT scripts %{buildroot}/opt/kompot/bin
cp -RT plugins %{buildroot}/opt/kompot/lib/plugins
## apache
install -d -m 0755 %{buildroot}/opt/kompot/lib/httpd
mv -T %{buildroot}/opt/kompot/share/configs/apache/conf.d %{buildroot}/opt/kompot/lib/httpd/conf.d
## logrotate
install -d -m 0755 %{buildroot}/opt/kompot/lib/logrotate
mv -t %{buildroot}/opt/kompot/lib/logrotate/ %{buildroot}/opt/kompot/bin/logrotate-mk-olddir
mv -T %{buildroot}/opt/kompot/share/configs/logrotate/conf.d %{buildroot}/opt/kompot/lib/logrotate/conf.d
## nagios
mv -T %{buildroot}/opt/kompot/share/configs/nagios/objects %{buildroot}/opt/kompot/lib/nagios
## nagzen
mv -T %{buildroot}/opt/kompot/share/configs/nagzen/templates %{buildroot}/opt/kompot/lib/nagzen
## rsyslog
install -d -m 0755 %{buildroot}/opt/kompot/lib/rsyslog
mv -T %{buildroot}/opt/kompot/share/configs/rsyslog/conf.d %{buildroot}/opt/kompot/lib/rsyslog/conf.d
## migration scripts
migration_scripts=(
    to-kompot-1.0.2.sh
    to-kompot-1.0.15.sh
)
install -d -m 0755 %{buildroot}/opt/kompot/share/migration
for i in "${migration_scripts[@]}"; do
    install -DTp -m 755 "%{_sourcedir}/migration/$i" "%{buildroot}/opt/kompot/share/migration/$i"
done
cd ..

# drawio
drawio_files=(
    favicon.ico
    images
    img
    index.html
    js/app.min.js
    js/extensions.min.js
    js/open.js
    js/shapes-14-6-5.min.js
    js/stencils.min.js
    math/es5/core.js
    math/es5/input/asciimath.js
    math/es5/input/tex.js
    math/es5/output/svg.js
    math/es5/output/svg/fonts/tex.js
    math/es5/startup.js
    math/es5/ui/safe.js
    mxgraph/css
    mxgraph/images
    open.html
    resources/dia.txt
    resources/dia_fr.txt
    shortcuts.svg
    styles
    templates
)
cd drawio-%{drawio_version}
mkdir -p %{buildroot}/opt/kompot/www/drawio
for i in "${drawio_files[@]}"; do
    [ "$i" == "${i//\/}" ] || mkdir -p "%{buildroot}/opt/kompot/www/drawio/${i%/*}"
    cp -RT --preserve=timestamps "src/main/webapp/$i" "%{buildroot}/opt/kompot/www/drawio/$i"
done
mv %{buildroot}/opt/kompot/share/configs/drawio/js/PreConfig.js %{buildroot}/opt/kompot/www/drawio/js/
mv %{buildroot}/opt/kompot/share/configs/drawio/js/PostConfig.js %{buildroot}/opt/kompot/www/drawio/js/
rm -rf %{buildroot}/opt/kompot/share/configs/drawio
cd ..

# drawio-ext
cd drawio-ext-%{drawio_ext_version}
    install -Dp -m 644 src/live.js %{buildroot}/opt/kompot/www/drawio/js/
cd ..

# kompot-wui
cd kompot-wui
cp -RT dist %{buildroot}/opt/kompot/www/htdocs
install -Dp -m 644 misc/kedit.html %{buildroot}/opt/kompot/www/drawio/
cd ..

%pre
# backup modified files if any
if [ "$1" != 0 ]; then
    files=$(rpm -V '%{name}' |awk '$1 ~ /^..5/ { print substr($NF, 2) }')
    if [ -n "$files" ]; then
        tarball='/var/lib/kompot/backup/%{name}-before-%{version}-%{release}-%(date +\%s).tar.gz'
        echo "# Backup modified files to $tarball"
        mkdir -p "${tarball%/*}"
        echo "$files" |tar hcvzf "$tarball" -C / -T -
    fi
fi

%files
/opt/kompot
%exclude /opt/kompot/bin/setup-kompot
%exclude /opt/kompot/share/migration

%files setup
/opt/kompot/bin/setup-kompot
/opt/kompot/share/migration

%posttrans setup
set -e
# busybox sv is installed in /usr/local/bin on kompot docker
PATH+=:/usr/local/bin
if [ "$KOMPOT_SETUP" != 0 ]; then
    /opt/kompot/bin/setup-kompot
    /opt/kompot/bin/init-kompot condrestart
fi
