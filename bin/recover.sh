#!/bin/bash
# continue aborted/frozen ccollect backup, without ccollect
# using exact rsync command also used by ccollect
# update: nope since it's getting the same problem. using slower direct sync
ccollect_source="$1"
interval="${2:-daily}"
[ -z "$1" ] && { echo "Usage: ${0##*/} CCOLLECT_SOURCE"; exit; }
echo interval $interval
# ccollect's
source_file="${CCOLLECT_CONF}/sources/${ccollect_source}/source"
[ -e ${source_file} ] && from=$(cat ${source_file}) || { echo recover.sh: ${ccollect_source}: No such sources; exit; }
# rsync-ing from NFS share often freezes
# workaround by subsituting the mount point with ip:server_mount
# a little slower, but more reliable
from_ip=$(df | grep "$from" | awk '{print $1}')
destination=$(cat ${CCOLLECT_CONF}/sources/${ccollect_source}/destination)
rsync_options=$(cat ${CCOLLECT_CONF}/sources/${ccollect_source}/rsync_options | sed ':a;N;$!ba;s/\n/ /g')
echo rsync_options: $rsync_options

# deduce
dirlist=$(find "$destination"/ -maxdepth 1 -type d | sort)
to=$(echo "$dirlist" | grep ccollect-marker | tail -n 1 | sed 's/\.ccollect-marker//')
[ -z "$to" ] && to=$(echo "$dirlist" | grep $interval | tail -n 1)
link_from=$(echo "$dirlist" | grep $interval | grep -v "$to" | tail -n 1)
[ -z "$from" ] && [ -z "$to" ] && [ -z "$link_from" ] && { echo Failed.; exit; }

# only sync when ccollect is not running and the directories exist
#syncing="$(lsof -c3-999 "$from")"
syncing="$(ps -ef | grep rsync | grep -v grep | grep ${ccollect_source})"
ccollect="$(ps -ef | grep ccollect | grep -v grep | grep ${ccollect_source})"
echo from: $from
echo to: $to
echo syncing process: $syncing
echo ccollect process: $ccollect
if [ ! -z "$link_from" ]
then
	[ ! -z "$from" ] && [ ! -z "$to" ] && [ -z "$syncing" ] && [ -z "$ccollect" ] && { echo can work meh; rsync --archive --delete --numeric-ids --delete-excluded --sparse --stats -vv "$rsync_options" --link-dest="$link_from/$from/" "$from_ip/" "$to/$from/"; } || echo Failed.
else
	[ ! -z "$from" ] && [ ! -z "$to" ] && [ -z "$syncing" ] && [ -z "$ccollect" ] && { echo can work meh; rsync --archive --delete --numeric-ids --delete-excluded --sparse --stats -vv "$rsync_options" "$from_ip/" "$to/$from/"; } || echo Failed.
fi
