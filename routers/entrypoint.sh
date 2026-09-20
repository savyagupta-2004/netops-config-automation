#!/bin/sh
set -e

mkdir -p /var/run/sshd

# Start FRR's own daemons (zebra, staticd, ospfd) using the packaged init
# script, same mechanism the frr .deb package's systemd unit uses.
/usr/lib/frr/frrinit.sh start

# Foreground process keeps the container alive; automation connects here.
exec /usr/sbin/sshd -D -e
