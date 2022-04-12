echo 0 > /sys/kernel/livepatch/livepatch_concord/enabled
rm /sys/fs/bpf/*
sleep 5
sudo rmmod livepatch_concord
