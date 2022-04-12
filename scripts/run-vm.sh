#!/bin/bash

IMAGE=/home/spark/images/ubuntu-20.04.img
KERNEL_SRC=/home/spark/etc/syncord/SynCord-linux

CORES=4
SOCKETS=1

PORT_TCP=4444
PORT_QMP=5555

qemu-system-x86_64 \
	--enable-kvm \
	-m 2G \
	-cpu host \
	-smp cores=${CORES},threads=1,sockets=${SOCKETS} \
	-drive file=${IMAGE},format=raw\
	-nographic \
	-overcommit mem-lock=off \
	-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
	-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
	-netdev user,id=hostnet0,hostfwd=tcp::${PORT_TCP}-:22 \
	-qmp tcp:127.0.0.1:${PORT_QMP},server,nowait \
	-kernel ${KERNEL}/arch/x86/boot/bzImage \
	-append "root=/dev/sda2 console=ttyS0" \

	# -cdrom /home/spark/images/ubuntu-20.04.4-live-server-amd64.iso \
