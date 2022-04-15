#define _GNU_SOURCE
#include <assert.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define SYS_rename2 436

typedef struct {
	volatile int *stop;
	const char *src;
	const char *dst_dirty;
	const char *dst;
	int id;
	pthread_t thread;

	uint64_t lock_hold;
	int runs;
} task_t;

static void rand_string(char *str, size_t size) {
	const char charset[] =
		"1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
	if (size) {
		--size;
		for (size_t n = 0; n < size; n++) {
			int key = rand() % (int)(sizeof(charset) - 1);
			str[n] = charset[key];
		}
		str[size] = '\0';
	}
}

uint64_t rename_prog(char *src, char *dst){
	uint64_t hold_time = 0;
	int fd = 0, rc = 0;

	/* Create the file */
	fd = open(src, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (fd < 0) {
		fprintf(stderr, "bully open source=%s: %s", src, strerror(errno));
		exit(1);
	}
	close(fd);

	/* Rename the file */
	rc = syscall(SYS_rename2, src, dst, &hold_time);
	if (rc < 0) {
		fprintf(stderr, "bully rename source=%s, dest=%s: %s\n", src,
				dst, strerror(errno));
		exit(1);
	}

	/* Unlink the file */
	rc = unlink(dst);
	if (rc < 0) {
		fprintf(stderr, "bully unlink dest=%s: %s\n", dst,
				strerror(errno));
		exit(1);
	}

	return hold_time;
}

void *bully(void *arg) {
	task_t *task = (task_t *)arg;
	uint64_t lock_hold = 0;

	cpu_set_t mask;
	CPU_SET(task->id, &mask);

	if(pthread_setaffinity_np(pthread_self(), sizeof(mask), &mask) < 0){
		perror("pthread_setaffinity_np");
	}

	while (!*task->stop) {
		char filename[37];
		char src[512];
		char dst[512];

		rand_string(filename, 37);
		snprintf(src, sizeof(src), "%s/%s", task->src, filename);
		snprintf(dst, sizeof(dst), "%s/%s", task->dst_dirty, filename);

		lock_hold += rename_prog(src, dst);
		task->runs++;
	}

	task->lock_hold = lock_hold;

	return 0;
}

void *victim(void *arg) {
	task_t *task = (task_t *)arg;
	uint64_t lock_hold = 0;

	cpu_set_t mask;
	CPU_SET(task->id, &mask);

	if(pthread_setaffinity_np(pthread_self(), sizeof(mask), &mask) < 0){
		perror("pthread_setaffinity_np");
	}

	while (!*task->stop) {
		char filename[37];
		char src[512];
		char dst[512];

		rand_string(filename, 37);
		snprintf(src, sizeof(src), "%s/%s", task->src, filename);
		snprintf(dst, sizeof(dst), "%s/%s", task->dst, filename);

		lock_hold += rename_prog(src, dst);
		task->runs++;
	}

	task->lock_hold = lock_hold;

	return 0;
}

int main(int argc, char **argv) {

	if (argc != 7) {
		fprintf(stderr, "Usage: %s src dst_dirty dst duration num_bully num_victim\n",
				argv[0]);
		return 1;
	}

	srand(time(0));
	const char *src = argv[1];
	const char *dst_dirty = argv[2];
	const char *dst = argv[3];
	const int duration = atoi(argv[4]);
	const int bullies = atoi(argv[5]);
	const int victims = atoi(argv[6]);
	int stop = 0;

	assert(src);
	assert(dst_dirty);
	assert(dst);
	assert(duration > 0);
	assert(bullies >= 0);
	assert(victims >= 0);

	const int task_n = bullies + victims;

	task_t *tasks = malloc(sizeof(task_t) * task_n);

	for (int i = 0; i < task_n; ++i) {
		tasks[i].stop = &stop;
		tasks[i].src = src;
		tasks[i].dst_dirty = dst_dirty;
		tasks[i].dst = dst;
		tasks[i].id= i;
		tasks[i].lock_hold = 0;
		tasks[i].runs = 0;
	}

	for (int i = 0; i < task_n; ++i) {
		if (i % 2 == 0) {
			pthread_create(&tasks[i].thread, NULL, bully, &tasks[i]);
		} else {
			pthread_create(&tasks[i].thread, NULL, victim, &tasks[i]);
		}
	}

	sleep(duration);
	stop = 1;

	for (int i = 0; i < task_n; ++i) {
		pthread_join(tasks[i].thread, NULL);
	}

	for (int i = 0; i < task_n; i+=2) {
			printf("[b] task %d: lock_hold=%lu, runs=%d\n", i, tasks[i].lock_hold, tasks[i].runs);
	}

	for (int i = 1; i < task_n; i+=2) {
			printf("[v] task %d: lock_hold=%lu, runs=%d\n", i, tasks[i].lock_hold, tasks[i].runs);
	}

	// compute the average for the bully group and the victim group, to make the
	// fairness index more sensitive
	double bully_lock_hold = 0.f, victim_lock_hold = 0.f;
	int bully_runs = 0, victim_runs = 0;

	for (int i = 0; i < task_n; ++i) {
		if (i%2 == 0){
			bully_lock_hold += (double)tasks[i].lock_hold;
			bully_runs += tasks[i].runs;
		}
		else{
			victim_lock_hold += (double)tasks[i].lock_hold;
			victim_runs += tasks[i].runs;
		}
	}

	//compute avg holding time
	const double bully_avg = bully_lock_hold / bullies;
	const double victim_avg = victim_lock_hold / victims;

	// also compute the ratio
	const double bully_ratio = bully_avg / (bully_avg + victim_avg);
	const double victim_ratio = victim_avg / (bully_avg + victim_avg);

	const double numerator = (bully_avg + victim_avg) * (bully_avg + victim_avg);
	const double denominator =
		((bully_avg * bully_avg) + (victim_avg * victim_avg)) * 2.f;
	double fairness = numerator / denominator;

	printf("fairness=%f\n", fairness);

	printf("Ops/sec: %f\n", (double)(bully_runs + victim_runs)/(double)duration);
	printf("Bully  Ops/sec: %f\n", (double)bully_runs/(double)duration);
	printf("Victim Ops/sec: %f\n", (double)victim_runs/(double)duration);

	/** printf("TOTAL LOCK HOLD TIME\n"); */
	/** printf("  bully  : %f  (%f %)\n", bully_avg, bully_ratio); */
	/** printf("  victim : %f  (%f %)\n", victim_avg, victim_ratio); */
    /**  */
	/** printf("RUNS\n"); */
	/** printf("  bully  : %d\n", bully_runs); */
	/** printf("  victim : %d\n", victim_runs); */


	free(tasks);

	return 0;
}
