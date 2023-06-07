#!/bin/bash -xe

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
