#!/bin/bash
# Search for non standard permissions
#
# 2018/08/13: First composed by genki
script_name=$(basename $0)

# Parse arguments
[ -z "$1" ] && { echo "Usage: $script_name ROOT_DIR" ; exit ; }
root_dir=$1

# stat format (permission-uid-gid-filename)
format='%a %u %g %n'

echo "Root: $root_dir..."

#stat everything under root
find "$root_dir" -exec stat --format "$format" {} \; | while read line
do
    array=($line)
    permission=${array[0]}
    perm_n_bit=${#permission}
    if [ $perm_n_bit -eq 3 ]
    then
        owner_permission=${array[0]:0:1}
        group_permission=${array[0]:1:1}
        world_permission=${array[0]:2:2}
    elif [ $perm_n_bit -eq 4 ]
    then
        set_permission=${array[0]:0:1}
        owner_permission=${array[0]:1:1}
        group_permission=${array[0]:2:2}
        world_permission=${array[0]:3:3}
    fi
    uid=${array[1]}
    gid=${array[2]}
    filename=${array[3]}
    if [ $owner_permission -lt 6 ] || [ "$uid" != '500' ] || [ "$gid" != '500' ]
    then
        echo "$permission $uid $gid $filename"
    fi
done
