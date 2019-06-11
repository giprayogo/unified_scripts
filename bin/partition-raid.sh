#!/bin/bash
# partition all drives in preparation for raid
# leave 100MiB empty space for compatibilities between different brands
# reference: https://wiki.archlinux.org/index.php/RAID#Partition_the_devices

for device in "$@"; do
 part_number=''
 first_sector=''
 last_sector='-100M'
 part_type='fd00'
 printf "n\n$part_number\n$first_sector\n$last_sector\n$part_type\nw\ny\n" | sudo gdisk "$device"
done
