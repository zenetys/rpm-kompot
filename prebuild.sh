#!/bin/bash -xe

build_dl "https://dl.fedoraproject.org/pub/epel/epel-release-latest-$DIST_VERSION.noarch.rpm"
rpm -Uvh "$CACHEDIR/epel-release-latest-$DIST_VERSION.noarch.rpm"

case "$DIST" in
    el9)
        dnf module enable -y nodejs:18
        echo install_weak_deps=False >> /etc/dnf/dnf.conf
        ;;
    *)
        echo "FATAL: Unsupported build target, DIST=$DIST"
        exit 2
        ;;
esac
