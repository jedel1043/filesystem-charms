# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details

"""Constants used by the `lustre_ops` package."""

from pathlib import Path

LUSTRE_REPOSITORY_URI = "http://archive.ubuntu.com/ubuntu/"
LUSTRE_LNET_CONF = Path("/etc/lnet.conf")

IP_EXECUTABLE = "/usr/sbin/ip"
LCTL_EXECUTABLE = "/usr/sbin/lctl"
LNETCTL_EXECUTABLE = "/usr/sbin/lnetctl"
MODPROBE_EXECUTABLE = "/usr/sbin/modprobe"
RDMA_EXECUTABLE = "/usr/bin/rdma"

SYS_CLASS_NET = Path("/sys/class/net")
