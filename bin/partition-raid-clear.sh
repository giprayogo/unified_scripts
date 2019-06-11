#!/bin/bash
# partition all drives in preparation for raid
# leave 100MiB empty space for compatibilities between different brands
# reference: https://wiki.archlinux.org/index.php/RAID#Partition_the_devices

for device in "$@"; do
 sudo mdadm --misc --zero-superblock "$device"
 printf "d\nw\ny\n" | sudo gdisk "$device"
done
