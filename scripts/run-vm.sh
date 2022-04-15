#!/bin/bash

IMAGE=/home/sujin/artifact/images/ubuntu-20.04.img
KERNEL_SRC=/home/sujin/artifact/SynCord-linux

CORES=28
SOCKETS=8

PORT_TCP=4444
PORT_QMP=5555

qemu-system-x86_64 \
	--enable-kvm \
	-m 128G \
	-cpu host \
	-smp cores=${CORES},threads=1,sockets=${SOCKETS} \
	-numa node,nodeid=0,mem=16G,cpus=0-27 \
	-numa node,nodeid=1,mem=16G,cpus=28-55 \
	-numa node,nodeid=2,mem=16G,cpus=56-83 \
	-numa node,nodeid=3,mem=16G,cpus=84-111 \
	-numa node,nodeid=4,mem=16G,cpus=112-139 \
	-numa node,nodeid=5,mem=16G,cpus=140-167 \
	-numa node,nodeid=6,mem=16G,cpus=168-195 \
	-numa node,nodeid=7,mem=16G,cpus=196-223 \
	-drive file=${IMAGE},format=raw\
	-nographic \
	-overcommit mem-lock=off \
	-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
	-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
	-netdev user,id=hostnet0,hostfwd=tcp::${PORT_TCP}-:22 \
	-qmp tcp:127.0.0.1:${PORT_QMP},server,nowait \
	-kernel ${KERNEL_SRC}/arch/x86/boot/bzImage \
	-append "root=/dev/sda2 console=ttyS0" \

	# -cdrom /home/spark/images/ubuntu-20.04.4-live-server-amd64.iso \
