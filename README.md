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
https://packages.zenetys.com/latest/redhat/


## Setup:

The RPM spec file builds two packages:

* _kompot_ only installs files in /opt/kompot without touching the system.
* _kompot-setup_ is a glue package that depends on the various components used in Kompot, eg: nagios, rsyslog, grafana, etc. Unless installed with KOMPOT_SETUP=0 in environment, it runs a setup script on %posttrans that installs Kompot configuration bits in /etc.

Requirements:

* Before installing kompot-setup, make sure you have configured the required YUM repositories. You also need to enable nodejs:18 module stream.

```
dnf -y install epel-release
crb enable
cd /etc/yum.repos.d
curl -OL https://packages.zenetys.com/latest/redhat/zenetys-latest.repo
curl -OL https://raw.githubusercontent.com/zenetys/docker-kompot/master/repos/grafana.repo
curl -OL https://raw.githubusercontent.com/zenetys/docker-kompot/master/repos/influxdata.repo
dnf -y module enable nodejs:18
```

* For now SELinux must be disabled on the system.
* Make sure your system is timesync'ed (eg: chrony, ntpd).

Install:

```
dnf install kompot kompot-setup
```

Start services. You may login again to get /opt/kompot/bin in your PATH.

```
/opt/kompot/bin/init-kompot restart
```

Now point your browser to http://\<ip-address\>/kompot/