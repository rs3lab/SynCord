---
title: Artifact Evaluation Guide
---

# Table of Contents
---

- [Overview](#overview)
	- [SynCord](#syncord)
	- [SynCord-linux](#syncord-linux)
	- [Environment](#environment)
- [Getting started instructions](#getting-started-instructions)
- [Detailed instructions](#detailed-instructions)
	- [To switch between locks](#to-switch-between-locks)
	- [Benchmark usage](#benchmark-usage)
		- [Will-it-scale](#will-it-scale)
		- [FxMark](#fxmark)
		- [Metis](#metis)
		- [LevelDB](#leveldb)
		- [xdir-rename](#xdir-rename)
- [How to create the disk image](#how-to-create-the-disk-image)


# Overview
---

## SynCord

[SynCord repository](https://github.com/rs3lab/SynCord) contains the source code
of SynCord framework and the benchmarks we used in the paper.
This is the directory structure of the SynCord repo.

	SynCord
	  ├── src                  : SynCord source code
	  |    ├── concord
	  |    └── kpatch
	  ├── benchmarks           : benchmark sets used in the paper
	  |    ├── will-it-scale
	  |    ├── fxmark
	  |    ├── metis
	  |    ├── levelDB
	  |    ├── xDir-rename
	  |    └── lockstat
	  └── scripts              : script to run qemu

## SynCord-linux

[SynCord-linux repository](https://github.com/rs3lab/SynCord-linux) contains
the linux source code modified for the SynCord as well as static lock
implementations compared in the paper.
It has six branches:

- **stock**: unmodified linux v5.4
- **cna**: CNA lock ([paper](https://dl.acm.org/doi/10.1145/3302424.3303984),
  [LWN](https://lwn.net/Articles/798629/)) ported to linux v5.4
- **shfllock**: ShflLock ([paper](https://dl.acm.org/doi/10.1145/3341301.3359629))
  ported to linux v5.4
- **stock-syncord**: linux v5.4 modified for SynCord
- **cna-syncord**: CNA lock ported to linux v5.4 and modified for
  SynCord
- **shfllock-syncord**: ShflLock ported to linux v5.4 and modified for SynCord



## Environment
The experiments in this artifact are designed to run on a *NUMA* machine with
multiple sockets and tens of CPUs.
The result shown in the paper is evaluated on a 8-socket, 224-core machine
equipped with Intel Xeon Platinum 8276L CPUs. The machine runs Ubuntu 20.04 with
Linux 5.4.0 and hyperthreading is disabled.


# Getting Started Instructions
---

## Description

The easiest way to reproduce SynCord is to use QEMU with our ready-to-use disk
image. In this guide, we introduce how to quickly setup an environment to
run SynCord using the disk image.
There is also a section guides [how to create the disk
image](#how-to-create-the-disk-image) from scratch.


## 1. Download the disk image and SynCord repo
---
Download the compresssed disk image
[here](https://zenodo.org/record/6549331#.YoAZhS8RoeY).
Once you finish downloading the file, uncompress it using following command.

	$ pv vm.img.xz | unxz -T <num_threads> > ubuntu-20.04.img


In addition, clone the SynCord repo.

	$ git clone https://github.com/rs3lab/SynCord.git


## 2. Start a QEMU virtual machine
---

Start qemu with following script.
The script is also available under `SynCord/scripts/run-vm.sh`.

> [Dependency]
> You may need following commands to install qemu and execute it without sudo.
>
	$ sudo apt install qemu-kvm
	$ sudo chmod 666 /dev/kvm

	$ ./qemu-system-x86_64 \
		--enable-kvm \
		-m 128G \
		-cpu host \
		-smp cores=28,threads=1,sockets=8 \
		-numa node,nodeid=0,mem=16G,cpus=0-27 \
		-numa node,nodeid=1,mem=16G,cpus=28-55 \
		-numa node,nodeid=2,mem=16G,cpus=56-83 \
		-numa node,nodeid=3,mem=16G,cpus=84-111 \
		-numa node,nodeid=4,mem=16G,cpus=112-139 \
		-numa node,nodeid=5,mem=16G,cpus=140-167 \
		-numa node,nodeid=6,mem=16G,cpus=168-195 \
		-numa node,nodeid=7,mem=16G,cpus=196-223 \
		-drive file=/path/to/downloaded/syncord-vm.img,format=raw \
		-nographic \
		-overcommit mem-lock=off
		-qmp tcp:127.0.0.1:5555,server,nowait \
		-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
		-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
		-netdev user,id=hostnet0,hostfwd=tcp::4444-:22 \


The command starts a virtual machine with 128G of memory and 8 NUMA sockets each
equipped with 28 cores, results in 224 cores in total. Please adjust the
numbers and path to the vm image for your environment.
The script opens port `4444` for ssh and `5555` for qmp.

When you face the grub menu, just wait for 5 seconds, then the guest will be
start with default `5.4.0-stock-syncord+` kernel.

The provided disk image contains one 30GB partition holding Ubuntu 20.04 and
one 20GB partition for experiments.
There is single user `syncord` with password `syncord`, who has sudo power.
Use port 4444 to ssh into the machine.

	$ ssh syncord@localhost -p 4444

The home directory already contains both `SynCord` and `SynCord-linux` repo.

	/home/syncord
		├── SynCord           : SynCord repo
		└── SynCord-linux     : SynCord-linux repo


## 3. Pin vCPU to physical cores
---

The port 5555 is for `qmp` which allows us to observe NUMA effect with vCPU by
pinning each vCPU to physical cores. __This step must be done__ before measuring numbers.
Run the `pin-vcpu.py` script to pin the cores. Here, `num_vm_cores` is 224 with
above example.

	$ python2 ./SynCord/scripts/pin-vcpu.py 5555 <num_vm_cores>

> [Dependency] Since the `pin-vcpu.py` use python2.7, you might need following commands to
> install pip for python2.7 and psutil package.
> If you didn't change the kvm permission in above [step](#2-start-a-qemu-virtual-machine),
> run following commands and above `pin-vcpu.py` with `sudo`

	$ sudo python2 ./SynCord/scripts/get-pip.py
	$ python2 -m pip install psutil


Once you start the VM, let's check you're on the right kernel version.

	(guest)$ uname -r

If you see `5.4.0-stock-syncord+`, you're all set and now it's time to use SynCord!


## 4. rename lock profiling
---

One of a simplest example of SynCord usecase is lock profiling.
Let's profile a `rename_lock`.

The VM image already has compiled policy program, we can just execute it!

	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf
	(guest)$ cd ~/SynCord/src/concord/output/lockstat
	(guest)$ sudo ./eBPFGen/lockstat
	./eBPFGen/lockstat_kern.o loaded
	/sys/fs/bpf/lockstat_to_enter_slow_path loaded and pinned
	/sys/fs/bpf/lockstat_lock_acquired loaded and pinned
	/sys/fs/bpf/lockstat_lock_to_release loaded and pinned
	hashmap pinned
	(guest)$ sudo insmod ./LivePatchGen/livepatch-concord.ko
	(guest)$ sudo ~/SynCord/benchmarks/lockstat/get-lockstat/get_bpflockstat

Then, you'll see following results printed on your screen but there's no
profiled data yet.

	==================================================================================================================================================
	       lock addr     contentions     con-bounces     acquisition     acq-bounces   wait-min   wait-max   wait-tot   hold-min   hold-max   hold-tot
	==================================================================================================================================================

Let's use a rename lock by executing following commands.

	(guest)$ touch file
	(guest)$ mv file newfile

See the profiling result again,

	(guest)$ sudo ~/SynCord/benchmarks/lockstat/get-lockstat/get_bpflockstat

	======================================================================================================================================================
	           lock addr     contentions     con-bounces     acquisition     acq-bounces   wait-min   wait-max   wait-tot   hold-min   hold-max   hold-tot
	======================================================================================================================================================
      0xffffffff82608584               0               0               0               0          0          0          0       4923       4923       4923

You could try `mv` command several times to check how the profiling result is changed.

To disable the profiling,

	(guest)$ sudo ~/SynCord/scripts/uninstall_policy.sh

To make sure the uninstallation is complete, check the `dmesg | grep concord` and find
`livepatch: 'livepatch_concord': unpatching complete` message.

# Detailed instructions
---

The following table summarizes graphs shown in the paper. Each row represents
underlying lock while each column shows lock policy.

The first three rows are static implementation of stock (unmodified linux v5.4),
CNA and ShflLock, and the following three rows are dynamic implementation using
SynCord. All six versions are available as branches of `SynCord-linux` repo.

We recommend you to start by testing the static lock and reproduce graphs
before jumping into the syncord.
This step can confirm that your environment is suitable to show the NUMA effect.


|                  | NUMA-aware | AMP            | SCL                    | Profiling  | per-CPU RW |
|------------------|:----------:|:--------------:|:----------------------:|:----------:|:---------:|
| stock            | Fig 5      | Fig 7          | Fig 9, Fig 10          | Fig 13     | Fig 12    |
| CNA              | Fig 5      |                |                        |            |           |
| ShflLock         | Fig 5      | Fig 7          | Fig 9                  |            |           |
| stock-syncord    |            |                |                        | Fig 13<br>[Guide E](#guide-e)| Fig 12<br>[Guide F](#guide-f) |
| CNA-syncord      | Fig 5<br>[Guide A](#guide-a) |           |           |            |           |
| ShflLock-syncord | Fig 5<br>[Guide B](#guide-b) | Fig 7, Table 4<br>[Guide C](#guide-c) | Fig 9, Fig 10, Table 3<br>[Guide D](#guide-d) |  |  |


## To switch between locks
---

To switch between underlying locks (i.e., rows in the above table), you need to
switch the kernel.

The provided vm image already contains all six version of kernels so you could
just select using grub menu.


## Benchmark usage
---

Below table summarizes benchmark used in each figure.
All the benchmarks locate under `~/SynCord/benchmarks`.

| Benchmark        | Figure / Table                         |
|:-----------------|:---------------------------------------|
| will-it-scale    | Figure 5, Figure 7, Figure 12          |
| FxMark           | Figure 5, Figure 7, Figure 13, Table 4 |
| Metis            | Figure 12                              |
| LevelDB          | Figure 5, Figure 7                     |
| xDir-rename      | Figure 9, Figure 10, Table 3           |


Please make sure you [pinned vCPU](#3-pin-vcpu-to-physical-cores) before measuring
numbers.

<br>

### Will-it-scale
---

Will-it-scale is a micro benchmark in the kernel space. We used `lock1` and
`page_fault1` in the paper.

Open `~/SynCord/benchmarks/will-it-scale/runtest.py` and set desired cores to
test in `data_points`. This would be the x-axis of the graph.
For example, we used following lines to test on the 224 core machine with 8
sockets each equipped 28 cores.

	data_points = [1,2,4,8,16,28,56,84,112,140,168,196,224]

To build and run pagefault1 workload,

	(guest)$ cd ~/SynCord/benchmark/will-it-scale
	(guest)$ make wl=page_fault1
	(guest)$ python3 runtest.py page_fault1
	(num_cores, num_nodes, cores_per_socket) = (224, 8, 28)
	# core,total,fast,slow
	1,344532,344532,0
	2,644264,322118,322145
	4,1210049,603170,606879
	8,2311181,1149210,1161971
	16,2621709,1308808,1312901
	28,2527580,1266116,1261464
	56,1692341,845047,847293
	84,1499735,750348,749387
	...

The first line of the printed message explains the number of physical cores,
numa nodes, and cores per socket. The second line shows how
to interpret following numbers.

We took the first column(`core` field) as x-axis and the second
column(`total` field) as y-axis to generate figures in our paper.
The `fast` and `slow` indicates throughput breakdown for the first half cores
of each socket (core 0-13, 28-41, ..) and the second half cores (core 14-27, 42-55, ..)
for the AMP machine.

It's worth to check how the throughput decreases after the threads count exceeds a
socket(>28) on stock linux.

<br>
### FxMark
---

FxMark is a file system microbenchmark in the kernelspace.

> [Dependency]
> fxmark requires python2 and gnuplot
>
	(guest)# sudo apt install python2 gnuplot

To build and run FxMark,

	(guest)$ cd ~/SynCord/benchmarks/fxmark
	(guest)$ make
	(guest)$ bin/run-fxmark.py

The `make` command automatically detect your environment and set the number of
cores to test. If you want to change it manually, revise
`test_hw_thr_cnts_coarse_grain` in `bin/cpupol.py`.

The `run-fxmark.py` script runs the benchmark and creates a log file
`fxmark.log` under `logs` directory.

To plot the graph, pass the log file with `--log` option and give a name for
an output directory with `--out` option.

	(guest)$ bin/plotter.py --log logs/<log_dir>/fxmark.log --ty sc --out <output_dirname>
	(guest)$ cat <output_dirname>/mem:tmpfs:MWRL:bufferedio.dat


<br>
### Metis
---

Metis is a map-reduce library to stress readers-writer lock in the kernel.

> [Dependency]
>
	(guest)$ sudo apt install libnuma-dev

To build and run,

	(guest)$ cd ~/SynCord/benchmarks/metis
	(guest)$ make
	(guest)$ obj/app/wrmem -p <num_cpu>

	Starting mapreduce
	Finished mapreduce
	Runtime in milliseconds [2 cores]
			Sample: 1565    Map:    36995   Reduce: 1294    Merge:  0     Sum:     39856   Real:   39857
	Number of Tasks
			Sample: 2       Map:    30      Reduce: 439

	wordreverseindex: results (TOP 5 from 4394 keys, 536870912 words):
				ABA - 122171
				ABC - 122489
				ABE - 122321
				ABG - 122292
				ABI - 122269

We took the number after `Real: ` which indicates how much time it tooks to
complete the workload.

<br>
### LevelDB
---

We used the 'readrandom' workload of LevelDB, representing an oltp scenario.
The workload is affected by the futex system call that manipulates a hashtable
using per-bucket spinlock.

Open `~/SynCord/benchmarks/leveldb/run_db_bench.sh` and set `cores` to match
with your environment. Then, set `core_per_socket` at
`leveldb-1.20/db/db_bench.cc`.

To build and run LevelDB,

	(guest)$ cd ~/SynCord/benchmarks/leveldb
	(guest)$ cd leveldb-1.20
	(guest)$ make
	(guest)$ cd ..
	(guest)$ ./run_db_bench.sh <output_dir_name>

To get statistics,

	(guest)$ python3 plot.py <output_dir_name>
	#num_threads, fast, slow, tot ops/s
	1, 833275.072, 0, 833275.072
	2, 624161.158, 617354.500, 1241514.790
	...

Each line of the output shows the number of threads, thorughput of fast and
slow cores for AMP machine, and total throughput.

<br>
### xDir-rename
---

xDir-rename workload is a simple program proposed by [SCL
lock](https://dl.acm.org/doi/10.1145/3342195.3387521).
The program creates two types of threads: *victim* threads and *bully* threads,
that both repeatedly performs cross-directory renames.
The victim threads repeatedly create a file from empty directory (`src_empty`)
and move it to another empty directory (`dst_empty`), while bully threads move it
to a directory containing 500,000 empty files (`dst_500000_files`).

Before proceed, create a direcotry `temp` under `xDir-rename` and mount it into
a separate disk partition, as the benchmark requires to disable `dir_index` for
the partition.
The VM image we provided already has sda3 partition with the three directories
and 500K files.

If you want to use other directory or partition, change variables at the top of
`run_bench.py`.

	(guest)$ cd ~/SynCord/benchmarks/xDir-rename
	(guest)$ mkdir temp
	(guest)$ sudo mount /dev/sda3 /home/syncord/SynCord/benchmarks/xDir-rename/temp/

To see the benchmark usage:

	(guest)$ python3 run_bench.py -h
	usage: run_bench.py [-h] [--scl SCL] n duration bully victim

	xDir benchmark creates 3 directories. Two empty directory `src_empty`,
	`dst_empty`, and `dst_N_files` directory which has N empty files

	positional arguments:
	  n           the number of files to creat under `dst_N_files`
	  duration    duration in sec to run the benchmark
	  bully       the number of bully threads
	  victim      the number of victim threads

	optional arguments:
	  -h, --help  show this help message and exit
	  --scl SCL   directory path to output/scl directory

To run a single benchmark with specific number of bully and victim threads, use following command:

	(guest)$ make
	(guest)$ python3 run_bench.py 500000 60 2 2
	[b] task 0: lock_hold=17232679264, runs=535
	[b] task 2: lock_hold=18639737162, runs=550
	[v] task 1: lock_hold=16680754, runs=536
	[v] task 3: lock_hold=16078292, runs=499
	fairness=0.500913
	Ops/sec: 212.000000
	Bully  Ops/sec: 108.500000
	Victim Ops/sec: 103.500000

The result shows that bully threads took the lock almost 1000x longer than
victims, with similar chance to grab the lock. You can find fairness, total
throughput, and throughput aggregated only for bullies and victims respectively.

The benchmark first turn off `dir_index` using `tune2fs` command, and create (or
check if they're already exist)
three directories under `temp`. Then it starts run the benchmark.


## SynCord usage
---

In order to use SynCord, you need to select one of the `-syncord` variant
kernels to start a vm. Basically, the `-syncord` variant works on identical
logic with its static implementation by default.

For example, `ShflLock-syncord` work just like `ShflLock` when there's no policy
enabled. Thus, enabling NUMA-aware policy to ShflLock-syncord and CNA-syncord
don't have any benefits but it can show the overhead coming from SynCord compared
to its static implementation.

When you follow below guides, please make sure to (i) start a VM with correct kernel
version and (ii) to checkout into correct branch of SynCord-linux which is
passed to concord.py using `--linux`.

__The policy programs described in Guide A to F are already compiled in the
provided VM image. Feel free to skip 'build' instruction if you want.__

<br>
#### Policy Uninstall

The following script file is to uninstall a policy. This is common across all
guides.

	(guest)$ sudo ~/SynCord/scripts/uninstall_policy.sh



<br>
### Guide A
---

This is a guide to reproduce Fig 5.

In specific,

- underlying lock: ShflLock-syncord
- policy         : NUMA-aware
- benchmark      : will-it-scale/lock1, FxMark/MWRL, LevelDB

#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-shfllock-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f shfllock-syncord
	Switched to branch 'shfllock-syncord'
	Your branch is up to date with 'origin/shfllock-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-syncord .config


#### Build
To create the NUMA-aware policy for ShflLock, run following commands.

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ python3 concord.py -v --linux ~/SynCord-linux --policy
		policy/numa-grouping --livepatch patches/numa-grouping.patch

This will generate `output/numa-grouping` directory.


#### Policy install
To enable the policy:

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf
	(guest)$ sudo ./output/numa-grouping/eBPFGen/numa-grouping
	(guest)$ sudo insmod ./output/numa-grouping/LivePatchGen/livepatch-concord.ko


<br>
### Guide B
---

This is a guide to reproduce Fig 5.

In specific,

- underlying lock: CNA-syncord
- policy         : NUMA-aware
- benchmark      : will-it-scale/lock1, FxMark/MWRL, LevelDB

#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-cna-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f cna-syncord
	Switched to branch 'cna-syncord'
	Your branch is up to date with 'origin/cna-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-cna .config

> [Tips]
> `cna-syncord` kernel needs
  `CONFIG_PARAVIRT_SPINLOCKS=y` and `CONFIG_NUMA_AWARE_SPINLOCKS=y` to be set.
> The sample config file can be found at `SynCord/scripts/config-cna`.
> Please make sure those flags are set in the `SynCord-linux/.config` file to test cna-syncord.


#### Build
To create the NUMA-aware policy for ShflLock, run following commands.
Please make sure the SynCord-linux repo in the guest machine is also pointing to
the correct branch.

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ python3 concord.py -v --linux ~/SynCord-linux --policy
		policy/numa-grouping-cna --livepatch patches/numa-grouping-cna.patch

This will generate `output/numa-grouping-cna` directory.


#### Policy install
To enable the policy:

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf
	(guest)$ sudo ./output/numa-grouping-cna/eBPFGen/numa-grouping-cna
	(guest)$ sudo insmod ./output/numa-grouping-cna/LivePatchGen/livepatch-concord.ko


<br>
### Guide C
---

This is a guide to reproduce Fig 7.

- underlying lock: shfllock-syncord
- policy         : amp
- benchmark      : will-it-scale/lock1, FxMark/MWRL, LevelDB


Asymmetric multiprocessing(AMP) machine consists of heterogeneous cores:
power-efficient slow cores and power-hungry fast cores.
Since there is no NUMA-AMP machine yet, we emulate the AMP environment by
changing the CPU frequency using `cpupower` command.
`~/SynCord/scripts/change-cpu-freq.sh` has a sample bash script on how to change
the cpu frequency.
In our environment, fast cores are 4x faster than slow cores and each
socket has 14 fast and 14 slow cores, respectively. Following is the example how
we used the script.
Please note that this job should be done in the HOST, not in the guest.
Moreover, please be aware that forcing maximum frequency might damage your CPU.
If you're not confident to enforce higher frequency for fast cores, you might
want to skip these steps modifying the cpu frequency.
It's difficult to see the performance improvement in overall throughput without
emulating AMP, but you can still check the impact of the policy that half of the cores are prioritized
over other cores.

	# To see the default cpu frequency on the system
	$ cpupower frequency-info | grep policy
	current policy: frequency should be within 1000 MHz and 2.20 GHz.

	# To see the hardware limit
	$ cpupower frequnecy-info | grep limit
	hardware limits: 1000 MHz - 4.00 GHz

	$ ./change-cpu-freq.sh --help
	usage: ./change-cpu-freq.sh num_cpu thread_per_core core_per_socket [amp|restore] fast_freq slow_freq

	# To emulate AMP
	$ ./change-cpu-freq.sh 224 1 28 amp 4000000 1000000

	# To restore the frequency,
	$ ./change-cpu-freq.sh 224 1 28 resotre 2200000 100000


#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-shfllock-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f shfllock-syncord
	Switched to branch 'shfllock-syncord'
	Your branch is up to date with 'origin/shfllock-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-syncord .config


#### Build

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ python3 concord.py -v --linux ~/SynCord-linux
			--policy policy/amp --livepatch patches/amp.patch

#### Policy install

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf
	(guest)$ sudo ./output/amp/eBPFGen/amp
	(guest)$ sudo insmod ./output/amp/LivePatchGen/livepatch-concord.ko


All the listed benchmark shows total throughput as well as breakdown throughput
for fast and slow cores. You can verify AMP policy is working by comparing the
throughput between fast and slow cores. The slow cores' throughput should be
restricted and the fast cores' throughput increases.


<br>
### Guide D
---

This is a guide to reproduce Figure 9, *SCL and *NUMA-SCL policy using SynCord.

- underlying lock: shfllock-syncord
- policy         : scl and numa-scl
- benchmark      : xDir-rename

#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-shfllock-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f shfllock-syncord
	Switched to branch 'shfllock-syncord'
	Your branch is up to date with 'origin/shfllock-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-syncord .config


#### Build

	(guest)$ cd ~/SynCord/src/concord/

	# Build *SCL policy
	(guest)$ python3 concord.py -v --linux_src ~/SynCord-linux
			--policy policy/scl --livepatch patches/scl.patch

	# Build *NUMA-SCL policy
	(guest)$ python3 concord.py -v --linux_src ~/SynCord-linux
			--policy policy/numa-scl --livepatch patches/numa-scl.patch

#### Usage

	# One time mounting bpffs
	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf

	# Build benchmark and mount temp (See xDir-rename section)

	# Run benchmark for 16 threads (8 bullies and 8 victims) with *SCL policy
	(guest)$ python3 run_bench.py 500000 60 8 8 --scl ~/SynCord/src/concord/output/scl

	# Run benchmark for 16 threads (8 bullies and 8 victims) with *NUMA-SCL policy
	(guest)$ python3 run_bench.py 500000 60 8 8 --scl ~/SynCord/src/concord/output/numa-scl

SCL policy tracks the *number of threads* using the lock.
Once the policy is enabled, it tries to balance the lock hold time across
threads. Since the number of lock users is cumulative,
the policy should be disabled when a workload is done.
Thus, it is recommended to use the policy by passing the compiled output to
the `run_bench.py` script with `--scl` option. With the option, `run_bench.py`
first enables the policy, run the benchmark, and then uninstall the policy after
the benchmark is done.

To reproduce the stock or shfllock in the Fig 9 graph, start the VM with `5.4.0-stock-syncord` or
`5.4.0-shfllock-syncord` kernel and follow [xDir-rename](#xdir-rename) instructions.
For these two variants, there's no need to pass `--scl` option to `run_bench.py`.


<br>
### Guide E
---

This is the guide to enable SynCord-lockstat with 10 counters.
We already tested this in the [quickstart](#4-rename-lock-profiling) section.

- underlying lock: stock-syncord
- policy         : profiling
- benchmark      : FxMark/MWRL

#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-stock-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f stock-syncord
	Switched to branch 'stock-syncord'
	Your branch is up to date with 'origin/stock-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-syncord .config


#### Build

	(guest)$ cd ~/SynCord/src/concord
	(guest)$ python3 concord.py -v --linux_src ~/SynCord-linux
		--policy policy/lockstat --livepatch patches/lockstat.patch


The Fig13 slowdown graph compares the FxMark results executed on different
kernels with profiling features enabled:

- baseline: FxMark result measured on `stock` kernel,
- lockstat: FxMark result measured on `stock-lockstat` kernel, a stock kernel with lockstat enabled
- SynCord-lockstat: FxMark result measured on SynCord-lockstat (profiling feature enabled by this guide E instructions)


<br>
### Guide F
---

This is a guide to reproduce per-CPU RW policy (Fig 12).

- underlying lock: stock-syncord
- policy         : bravo
- benchmark      : will-it-scale/pagefault1, Metis

#### Check
Please make sure you're using the correct kernel version and the SynCord-linux
repo is on the correct branch.

	(guest)$ uname -r
	5.4.0-stock-syncord+

	(guest)$ cd ~/SynCord-linux
	(guest)$ git checkout -f stock-syncord
	Switched to branch 'stock-syncord'
	Your branch is up to date with 'origin/stock-syncord'.
	(guest)$ cp ~/SynCord/scripts/config-syncord .config


#### Build

	(guest)$ cd ~/SynCord/src/concord/
	(guest)$ python3 concord.py -v --linux_src ~/SynCord-linux --policy
			policy/bravo --livepatch patches/bravo.patch

#### Policy install

	(guest)$ sudo mount bpffs -t bpf /sys/fs/bpf
	(guest)$ cd ~/SynCord/src/concord/output/bravo
	(guest)$ sudo ./eBPFGen/bravo
	(guest)$ sudo insmod ./LivePatchGen/livepatch-concord.ko


# How to create the disk image
---

## 1. Create a bootable image

First, download a ubuntu 20.04 LTS image ([link](https://releases.ubuntu.com/20.04/)).

	$ wget https://releases.ubuntu.com/20.04/ubuntu-20.04.4-live-server-amd64.iso

Create a storage image.

	$ qemu-img create ubuntu-20.04.img 30G

Start QEMU and use the downloaded iso image as a booting disk.

	$ ./qemu-system-x86_64 \
		--enable-kvm \
		-m 128G \
		-cpu host \
		-smp cores=28,threads=1,sockets=8 \
		-numa node,nodeid=0,mem=16G,cpus=0-27 \
		-numa node,nodeid=1,mem=16G,cpus=28-55 \
		-numa node,nodeid=2,mem=16G,cpus=56-83 \
		-numa node,nodeid=3,mem=16G,cpus=84-111 \
		-numa node,nodeid=4,mem=16G,cpus=112-139 \
		-numa node,nodeid=5,mem=16G,cpus=140-167 \
		-numa node,nodeid=6,mem=16G,cpus=168-195 \
		-numa node,nodeid=7,mem=16G,cpus=196-223 \
		-drive file=/path/to/created/ubuntu-20.04.img,format=raw \
		-cdrom /path/to/downloaded/ubuntu-20.04.4-live-server-amd64.iso \


Please make sure to have multiple sockets and enough number of cores to evaluate
lock scalability on NUMA machine.

If X11 connection is there, you'll see the QEMU GUI popup window to install
ubuntu. Install ubuntu server with OpenSSH package and disabled LVM.
Then login to the installed user.
If you don't have X11 connection, please refer this
[link](https://github.com/XieGuochao/cloud-image-builder) to setup the image.

Open `/etc/default/grub` and update `GRUB_CMDLINE_LINUX_DEFAULT="console=ttyS0"`.
This will print initial booting messages to the console on the start of the
guest vm.
Then, run the following commands to apply the change and shutdown the guest
machine.

	(guest)$ sudo update-grub
	(guest)$ sudo shutdown -h now

Now, you can start your QEMU without the iso file and graphic.

	$ ./qemu-system-x86_64 \
		--enable-kvm \
		-m 128G \
		-cpu host \
		-smp cores=28,threads=1,sockets=8 \
		-numa node,nodeid=0,mem=16G,cpus=0-27 \
		-numa node,nodeid=1,mem=16G,cpus=28-55 \
		-numa node,nodeid=2,mem=16G,cpus=56-83 \
		-numa node,nodeid=3,mem=16G,cpus=84-111 \
		-numa node,nodeid=4,mem=16G,cpus=112-139 \
		-numa node,nodeid=5,mem=16G,cpus=140-167 \
		-numa node,nodeid=6,mem=16G,cpus=168-195 \
		-numa node,nodeid=7,mem=16G,cpus=196-223 \
		-drive file=/path/to/created/ubuntu-20.04.img,format=raw \
		-nographic \
		-overcommit mem-lock=off \
		-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
		-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
		-netdev user,id=hostnet0,hostfwd=tcp::4444-:22 \
		-qmp tcp:127.0.0.1:5555,server,nowait \


## 2. Install custom kernel
---

To use custom kernel, you have two options.

First, compile the kernel and install it within the guest vm.\\
Or, compile the kernel in the host machine and pass it to the qemu via `-kernel`
option.

The second option is more convenient for frequent kernel changes, but it still
requires one time static install for kernel modules.
SynCord-linux has three lock implementation all based on linux kernel v5.4, so you
can reuse kernel modules across the three branches (stock, cna, shfllock) once
installed.

To build and install a kernel inside the vm, first clone the SynCord-linux repo
and resolve dependencies.

	(guest)$ git clone -b stock https://github.com/rs3lab/SynCord-linux.git
	(guest)$ cd SynCord-linux

> [Dependency]
> You may need following commands to build linux
>
	(guest) $ sudo apt-get install build-essential libncurses5 libncurses5-dev bin86 \
		kernel-package libssl-dev bison flex libelf-dev
>
> [Dependency]
> In addition, please make sure you're using gcc-7.
>
	(guest) $ gcc -v
	...
	gcc version 7.5.0 (Ubuntu 7.5.0-6ubuntu2)


Before start compilation, please make sure `CONFIG_PARAVIRT_SPINLOCKS` is not
set in your `.config` file.

	(guest)$ make -j <num_threads>
	(guest)$ sudo make modules_install
	(guest)$ sudo make install
	(guest)$ sudo shutdown -h now		# Install complete. Shut down guest machine

Now, in the host machine, you can choose a branch you want to use and then start
a qemu with that lock implementation. Please make sure you're using gcc-7 here
too.

	$ gcc -v
	...
	gcc version 7.5.0

	$ git clone https://github.com/rs3lab/SynCord-linux.git
	$ cd ~/SynCord-linux
	$ git checkout -t origin/stock		# or select origin/cna, origin/shfllock
	$ make -j <num_threads>

	$ ./qemu-system-x86_64 \
		--enable-kvm \
		-m 128G \
		-cpu host \
		-smp cores=28,threads=1,sockets=8 \
		-numa node,nodeid=0,mem=16G,cpus=0-27 \
		-numa node,nodeid=1,mem=16G,cpus=28-55 \
		-numa node,nodeid=2,mem=16G,cpus=56-83 \
		-numa node,nodeid=3,mem=16G,cpus=84-111 \
		-numa node,nodeid=4,mem=16G,cpus=112-139 \
		-numa node,nodeid=5,mem=16G,cpus=140-167 \
		-numa node,nodeid=6,mem=16G,cpus=168-195 \
		-numa node,nodeid=7,mem=16G,cpus=196-223 \
		-drive file=/path/to/created/ubuntu-20.04.img,format=raw \
		-nographic \
		-overcommit mem-lock=off \
		-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0x6 \
		-device virtio-net-pci,netdev=hostnet0,id=net0,bus=pci.0,addr=0x3 \
		-netdev user,id=hostnet0,hostfwd=tcp::4444-:22 \
		-qmp tcp:127.0.0.1:5555,server,nowait \
		-kernel ~/SynCord-linux/arch/x86/boot/bzImage \
		-append "root=/dev/sda2 console=ttyS0" \

The `uname -r` command confirms that the current guest VM is booted using the
custom kernel.

	(guest)$ uname -r
	5.4.0-syncord

## 3. Setup SynCord

Inside the guest VM, clone the [SynCord](https://github.com/rs3lab/SynCord) and
[SynCord-linux](https://github.com/rs3lab/SynCord-linux) repositories.

install dependencies and build:

	$ sudo apt install python3-pip clang llvm
	$ pip3 install gitpython
	$ cd ~/Syncord/src/kpatch && make
