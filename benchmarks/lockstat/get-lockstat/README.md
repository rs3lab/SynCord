This is a simple eBPF program that prints profiled results.
It collects data similar to the
[lockstat](https://www.kernel.org/doc/html/latest/locking/lockstat.html)

To use,

	$ make
	$ sudo ./get_bpflockstat

Each column shows statistics:

 lock addr
	- address of lock instances
 contentions
	- number of lock acquisitions that had to wait
 con-bounces
	- number of lock contention
 acquisitions
	- number of times we took the lock
 acq-bounces
	- number of lock acquisitions that involved x-cpu data
 wait-min
	- shortest (non-0) time we ever had to wait for a lock
 wait-max
	- longest time we ever had to wait for a lock
 wait-tot
	- total time we spend waiting on this lock
 hold min
	- shortest (non-0) time we ever held the lock
 hold max
	- longest time we ever held the lock
 hold tot
	- total time this lock was held
