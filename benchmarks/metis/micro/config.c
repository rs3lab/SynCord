#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <assert.h>
#include <inttypes.h>

#define HT_LINK_GLOBAL 0x150

#define HT_LINK_GLOBAL_FORCE_ERR_TYPE_OFF 5
#define HT_LINK_GLOBAL_FORCE_ERR_TYPE_MASK (3 << HT_LINK_GLOBAL_FORCE_ERR_TYPE_OFF)

#define HT_LINK_GLOBAL_FORCE_ERR_GET_TYPE(v)   \
	((v & HT_LINK_GLOBAL_FORCE_ERR_TYPE_MASK) >> HT_LINK_GLOBAL_FORCE_ERR_TYPE_OFF)

#define HT_LINK_GLOBAL_FORCE_ERR_ALL 0
#define HT_LINK_GLOBAL_FORCE_ERR_CMD_ONLY 1
#define HT_LINK_GLOBAL_FORCE_ERR_DATA_FIRST 2
#define HT_LINK_GLOBAL_FORCE_ERR_DATA_LAST 3


static uint32_t
read_pci_conf(char *path, int off)
{
    int fd = open(path, O_RDONLY);
    assert(fd >= 0);
    assert(lseek(fd, off, SEEK_SET) == HT_LINK_GLOBAL);
    uint32_t v = 0;
    assert(read(fd, &v, 4) == 4);
    close(fd);
    return v;
}

static void
write_pci_conf(char *path, int off, uint32_t newV)
{
    int fd = open(path, O_WRONLY);
    assert(fd >= 0);
    assert(lseek(fd, off, SEEK_SET) == HT_LINK_GLOBAL);
    assert(write(fd, &newV, 4) == 4);
    close(fd);
}

static void
set_ht_err_type(char *path, int type)
{
    uint32_t oldV = read_pci_conf(path, HT_LINK_GLOBAL);
    printf("0x%08x, type is 0x%x\n", oldV, HT_LINK_GLOBAL_FORCE_ERR_GET_TYPE(oldV));
    uint32_t newV = (oldV & (~HT_LINK_GLOBAL_FORCE_ERR_TYPE_MASK)) |
                    (type << HT_LINK_GLOBAL_FORCE_ERR_TYPE_OFF);
    printf("0x%08x, type is 0x%x\n", newV, HT_LINK_GLOBAL_FORCE_ERR_GET_TYPE(newV));
    write_pci_conf(path, HT_LINK_GLOBAL, newV);
}

int 
main(int argc, char** argv)
{
    char *path = "/sys/devices/pci0000:00/0000:00:18.0/config";
    set_ht_err_type(path, HT_LINK_GLOBAL_FORCE_ERR_ALL);
    //set_ht_err_type(path, HT_LINK_GLOBAL_FORCE_ERR_CMD_ONLY);
    //set_ht_err_type(path, HT_LINK_GLOBAL_FORCE_ERR_DATA_FIRST);
    //set_ht_err_type(path, HT_LINK_GLOBAL_FORCE_ERR_DATA_LAST);
}
