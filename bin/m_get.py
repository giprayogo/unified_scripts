#!/usr/bin/env python
# 2019/04/23: pass-through all other arguments as rsync arguments
# when?: converted to python (from perl)

import read_data_pm as readpm

import argparse
import os
import subprocess

parser = argparse.ArgumentParser(
        description='put files into clusters. can additionally accept rsync arguments')
# for individual files/dir
parser.add_argument('--files', '-f', nargs='*')
# optional info if not supplied by *.jss, UserName, or Jobdir
parser.add_argument('--cluster', '-c')
parser.add_argument('--username', '-u')
parser.add_argument('--source-dir', '-s')
parser.add_argument('--no-delete', '-n', action='store_true')
args, rsync_args = parser.parse_known_args()

datapm = readpm.read_perl_module_hashes(readpm.DATAPM)

# cluster have to be defined first for multi-user-cluster setting
if args.cluster:
    cname = args.cluster
else:
    cname = readpm.specify_cluster()
uname = args.username if args.username else readpm.get_uname(cname)

c1 = datapm['clusters']['unified']
c2 = datapm['clusters'][cname]

path = readpm.cat_iffile(args.source_dir) if args.source_dir else readpm.c2path(c1, c2, uname, cname)
files = args.files if args.files else [path]

def build_command(a, b):
    # output: [ a b1 a b2 ... ] from f(a, [ b1 b2 ... ])
    return [ x for y in [[a, x] for x in b] for x in y ]

# rsync pass-through
# make sure that the optional options pre-empt the data.pm defaults
# TODO: I don't like reading this part too
command = list(filter(None, ['rsync', '-av', '--progress', '--delete']))
command.extend(rsync_args)

# TODO: make something that is more elegant
if c2['rsync_option']:
    command.extend(c2['rsync_option'])

# rsync command building
# add includes and excludes, starting with data.pm defaults
#command = list(filter(None, ['rsync', '-av', '--progress', '--delete', c2['rsync_option']]))
command.extend(build_command('--exclude', readpm.exclude))
command.extend(build_command('--include', readpm.include))

command.extend([ '{}:{}'.format(readpm.c2ip(c2, uname), os.path.join(path, x)) for x in files ])
command.append(os.getcwd())

if args.no_delete:
    command = [ x for x in command if x != '--delete' ]
print(subprocess.list2cmdline(command))
subprocess.call(filter(None, command))
