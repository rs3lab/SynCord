will-it-scale
=============

QuickStart
----------

Open `runtest.py` and set desired cores to test in `data_points`.

	make wl=lock1
	python3 runtest.py lock1


Overview
--------
Will It Scale takes a testcase and runs it from 1 through to n parallel copies
to see if the testcase will scale. It builds both a process and threads based
test in order to see any differences between the two.

Instead of hwloc, we used `lscpu` and `setaffinity` to pin each task on its own
core.

Testcase design
---------------
Each test has two required components. A testcase description:

	char *testcase_description = "Context switch via pipes";

and a testcase() which is passed a pointer to an iteration count that the
testcase should increment. This testcase is run whatever number of times the
user specifies on the command line via the -t option:

	void testcase(unsigned long long *iterations)

A (not very useful) example:

	#include <sys/types.h>
	#include <unistd.h>

	char *testcase_description = "getppid";

	void testcase(unsigned long long *iterations)
	{
        	while (1) {
                	getppid();
                	(*iterations)++;
        	}
	}

If you need to setup something globally such as a single file for all
parallel testcases to operate on, there are two functions:

	void testcase_prepare(unsigned long nr_tasks)
	void testcase_cleanup(void)

Finally if you need a new task such as when you want to write a context
switch benchmark between two tasks, you can use:

	void new_task(void *(func)(void *), void *arg)

This takes care of creating a new process or a new thread depending on
which version of the test is being run.

Postprocessing and graphing
---------------------------
The graphing scripts use plotly, a client side javascript graphing package.

To generate html files for generated results:

	./postprocess.py

Then load the generated html file in the browser.

The graphs show number of tasks run on the x axis vs performance (in operations
per second) on the left y axis. We also plot the amount of idle time against
the right y axis. In the ideal case we should have an X pattern, with
operations per second increasing and idle time decreasing.
