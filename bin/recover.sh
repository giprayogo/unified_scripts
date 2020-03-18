#!/bin/bash
# continue aborted/frozen ccollect backup, without ccollect
# using exact rsync command also used by ccollect
# update: nope since it's getting the same problem. using slower direct sync
ccollect_source="$1"
interval="${2:-daily}"
[ -z "$1" ] && { echo "Usage: ${0##*/} CCOLLECT_SOURCE"; exit; }
echo interval $interval 
# ccollect's
from=$(cat ${CCOLLECT_CONF}/sources/${ccollect_source}/source)
destination=$(cat ${CCOLLECT_CONF}/sources/${ccollect_source}/destination)

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
echo syncing $syncing
if [ ! -z "$link_from" ]
then
	[ ! -z "$from" ] && [ ! -z "$to" ] && [ -z "$syncing" ] && [ -z "$ccollect" ] && { echo can work meh; rsync --archive --delete --numeric-ids --delete-excluded --sparse --stats -vv --link-dest="$link_from/$from/" "$from/" "$to/$from/"; } || echo Failed.
else
	[ ! -z "$from" ] && [ ! -z "$to" ] && [ -z "$syncing" ] && [ -z "$ccollect" ] && { echo can work meh; rsync --archive --delete --numeric-ids --delete-excluded --sparse --stats -vv "$from/" "$to/$from/"; } || echo Failed.
fi
