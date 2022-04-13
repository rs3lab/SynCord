SCL Bench
=========

# Preparation

1. Turn off directory index feature

	```
	$ tune2fs -O ^dir_index /dev/sda1	# Turn off
	$ tune2fs -l /dev/sda1				# Check
	```

2. Make three directories (src, dst, dst_dirty).
src and dst is empty, while dst_dirty has a million empty files.

```
	$ python3 script.py
```

# Run

1. Run the benchmark

```
	$ ./benchmark src dst_dirty dst 30 30 30 > result
```


