#!/bin/bash
IMAGE=/home/sujin/images/ubuntu-16.04.img
PORT_TCP=4444
PORT_QMP=5555

CORES=28
SOCKETS=8

KERNEL_SRC=/home/sujin/SynCord-linux
KERNEL=${KERNEL_SRC}/arch/x86/boot/bzImage

qemu-system-x86_64 \
	-nographic \
	--enable-kvm \
	-kernel ${KERNEL} \
	-append "root=/dev/sda1 console=ttyS0" \
	-initrd /home/sujin/images/initrd.img-5.4.0-shfllock \
	-drive file=${IMAGE},if=virtio \
	-m 128G \
	-cpu host \
	-numa node,nodeid=0,mem=16G,cpus=0-27 \
	-numa node,nodeid=1,mem=16G,cpus=28-55 \
	-numa node,nodeid=2,mem=16G,cpus=56-83 \
	-numa node,nodeid=3,mem=16G,cpus=84-111 \
	-numa node,nodeid=4,mem=16G,cpus=112-139 \
	-numa node,nodeid=5,mem=16G,cpus=140-167 \
	-numa node,nodeid=6,mem=16G,cpus=168-195 \
	-numa node,nodeid=7,mem=16G,cpus=196-223 \
	-smp cores=${CORES},threads=1,sockets=${SOCKETS} \
	-qmp tcp:127.0.0.1:${PORT_QMP},server,nowait \
	-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
	-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
    -netdev user,id=hostnet0,hostfwd=tcp::${PORT_TCP}-:22 \
	-realtime mlock=off
	# -append "root=/dev/sda1 console=ttyS0" \
	# -append "root=/dev/sda1 kgdboc=ttyS0,115200 nokaslr" -serial pty\
    # -append "root=UUID=2cd78b8d-819f-461e-b0e0-1b14a8e87585 ro console=ttyS0" \
	# -append "root=/dev/sda1 console=ttyS0 idle=poll" \
