#!/bin/bash

IMAGE=/home/spark/images/ubuntu-20.04.img
PORT_TCP=4444
PORT_QMP=5555

CORES=4
SOCKETS=1

KERNEL_SRC=/home/spark/etc/syncord/SynCord-linux
KERNEL=${KERNEL_SRC}/arch/x86/boot/bzImage

qemu-system-x86_64 \
	--enable-kvm \
	-m 2G \
	-cpu host \
	-smp cores=${CORES},threads=1,sockets=1 \
	-drive file=${IMAGE},format=raw\
	-nographic \
	-qmp tcp:127.0.0.1:${PORT_QMP},server,nowait \
	-net user,hostfwd=tcp::${PORT_TCP}-:22 -net nic \
	-overcommit mem-lock=off \
	-kernel ${KERNEL} \
	-append "root=/dev/sda2 console=ttyS0" \

	# -cdrom /home/spark/images/ubuntu-20.04.4-live-server-amd64.iso \
