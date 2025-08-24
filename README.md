| Package&nbsp;name | Supported&nbsp;targets |
| :--- | :--- |
| kompot<br/>kompot-setup | el9 |
<br/>

## Build:

The package can be built easily using the rpmbuild-docker script provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull Rocky Linux (el9) images from internet if not already downloaded.

```
$ ./rpmbuild-docker -d el9
```

## Prebuilt packages:

Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/projects/kompot/latest/redhat/


## Setup:

The RPM spec file builds two packages:

* <u>kompot</u> only installs files in /opt/kompot without touching the system.
* <u>kompot-setup</u> is a glue package that depends on the various components used in Kompot, eg: nagios, rsyslog, grafana, etc. Unless installed with KOMPOT_SETUP=0 in environment, it runs a setup script on %posttrans that installs Kompot configuration bits in /etc.

**Requirements:**

* Before installing kompot-setup, make sure you have configured the required YUM repositories and RPM GPG keys installed:

```
dnf -y install epel-release
crb enable
cd /etc/yum.repos.d
curl -OL https://packages.zenetys.com/projects/kompot/latest/redhat/kompot.repo
rpm --import https://rpm.grafana.com/gpg.key
rpm --import https://repos.influxdata.com/influxdata-archive.key
```

* For now SELinux must be disabled on the system.
* Make sure your system is timesync'ed (eg: chrony, ntpd).
* Disable firewalld or tune it properly, you will need HTTP access on port 80 for a start.

**Install:**

```
dnf --setopt install_weak_deps=0 install kompot kompot-setup
```

Puppeteer won't be installed by default because it requires a lot of dependencies while must users don't need it. To install it, run:

```
dnf module enable nodejs:18
dnf --setopt install_weak_deps=0 install puppeteer
```

**Start services:**

You may login again to get /opt/kompot/bin in your PATH.

```
/opt/kompot/bin/init-kompot restart
```

**Test:**

Point your browser to <u>http://\<ip-address\>/kompot/</u> and switch to level 5.

<i>More to come in a proper doc on the main project page or wiki...</i>
