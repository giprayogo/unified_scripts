#!/usr/bin/env python
# 2019/04/23: pass-through all other arguments as rsync arguments
# when?: converted to python (from perl)

import imp
readpm = imp.load_source('read_data_pm', '/mnt/lustre/scriptsForClusterNew/.read_data_pm.py')

import argparse
import os
import subprocess

# manually adding 'rsync_arguments'
parser = argparse.ArgumentParser(usage='%(prog)s [-h] [--files [FILES [FILES ...]]] [--cluster CLUSTER]\
        \n[--username USERNAME] [--source SOURCE] [RSYNC_ARGUMENTS]')
# for individual files/dir
parser.add_argument('--files', '-f', nargs='*')
# optional info if not supplied by *.jss, UserName, or Jobdir
parser.add_argument('--cluster', '-c')
parser.add_argument('--username', '-u')
parser.add_argument('--source-dir', '-s')
parser.add_argument('--no-delete', '-n', action='store_true')
args, rsync_args = parser.parse_known_args()

uname = args.username if args.username else readpm.get_uname()
cname = args.cluster if args.cluster else readpm.specify_cluster()

datapm = readpm.read_perl_module_hashes(readpm.DATAPM)
c1 = datapm['clusters']['unified']
c2 = datapm['clusters'][cname]

def build_command(a, b):
    # output: [ a b1 a b2 ... ] from f(a, [ b1 b2 ... ])
    return [ x for y in [[a, x] for x in b] for x in y ]

# add includes and excludes, starting with data.pm defaults
command = ['rsync', '-av', '--progress', '--delete', c2['rsync_option']]
command.extend(build_command('--exclude', readpm.exclude))
command.extend(build_command('--include', readpm.include))

# rsync pass-through
command.extend(rsync_args)

path = args.source_dir if args.source_dir else readpm.c2path(c1, c2, uname)
files = args.files if args.files else [path]
command.extend([ '{}:{}'.format(readpm.c2ip(c2, uname), os.path.join(path, x)) for x in files ])
command.append(os.getcwd())

if args.no_delete:
    command = [ x for x in command if x != '--delete' ]
print(subprocess.list2cmdline(command))
subprocess.call(filter(None, command))
