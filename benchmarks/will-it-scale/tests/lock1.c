#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <assert.h>

char *testcase_description = "Separate file write lock/unlock";

void testcase(unsigned long long *iterations, unsigned long nr)
{
	char tmpfile[] = "/tmp/willitscale.XXXXXX";
	int fd = mkstemp(tmpfile);

	assert(fd >= 0);
	unlink(tmpfile);

	while (1) {
		struct flock lck;

		lck.l_type = F_WRLCK;
		lck.l_whence = SEEK_SET;
		lck.l_start = 0;
		lck.l_len = 1;
		assert(fcntl(fd, F_SETLKW, &lck) == 0);

		lck.l_type = F_UNLCK;
		lck.l_whence = SEEK_SET;
		lck.l_start = 0;
		lck.l_len = 1;
		assert(fcntl(fd, F_SETLKW, &lck) == 0);

		(*iterations) += 2;
	}
}

/** This program simply 1)sets write lock on tmpfile's first byte and
    2)unlock the it. */

/** struct flock  */
/**    - l_type:  */
/**          Type of lock: F_RDLCK(read), F_WRLCK(write), F_UNLCK  */
/**    - l_whence: */
/**          How to interpret l_start: SEEK_SET, SEEK_CUR, SEEK_END */
/**    - l_start: Starting offset for lock */
/**    - l_len: # of bytes to lock */


/** F_SETLKW (struct flock *) */
/** Acquire a lock (when l_type is F_RDLCK or F_WRLCK) or release a lock (when
  * l_type is F_UNLCK) on the bytes specified by the l_whence, l_start, and l_len
  * fields of lock. If a conflicting lock is held on the file, then wait for that
  * lock to be released. If a signal is caught while waiting, then the call is
  * interrupted and (after the signal handler has returned) returns immediately
  * (with return value -1 and errno set to EINTR; see signal(7)). */

// fcntl_setlk


