#!/usr/bin/env python
# 2019/04/23: pass through rsync arguments
# when?: converted to python

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
parser.add_argument('--destination', '-s')
parser.add_argument('--no-delete', '-n', action='store_true')
args, rsync_args = parser.parse_known_args()

cname = args.cluster if args.cluster else readpm.specify_cluster()
uname = args.username if args.username else readpm.get_uname(cname)

datapm = readpm.read_perl_module_hashes(readpm.DATAPM)
c1 = datapm['clusters']['unified']
c2 = datapm['clusters'][cname]

def build_command(key, arg):
    # output: [ a b1 a b2 ... ] from f(a, [ b1 b2 ... ])
    return [ x for y in [[key, x] for x in arg] for x in y ]

# add includes and excludes, starting with data.pm defaults
command = list(filter(None, ['rsync', '-avz', '--progress', c2['rsync_option']]))
command.extend(build_command('--exclude', readpm.exclude))
command.extend(build_command('--include', readpm.include))

# rsync pass-through
command.extend(rsync_args)

path = args.destination if args.destination else readpm.c2path(c1, c2, uname, cname)
files = args.files if args.files else [ os.path.join(os.getcwd(), '') ]
command.extend([ x for x in files ])
command.extend([ '{}:{}'.format(readpm.c2ip(c2, uname), os.path.join(path, '')) ])

mkdir = list(filter(None, [ 'ssh', c2['ssh_option'], readpm.c2ip(c2, uname), 'mkdir -p {}'.format(path) ]))

if args.no_delete:
    command = [ x for x in command if x != '--delete' ]
if not '--dry-run' in rsync_args:
    print(subprocess.list2cmdline(mkdir))
    subprocess.call(mkdir)
print(subprocess.list2cmdline(command))
subprocess.call(command)
