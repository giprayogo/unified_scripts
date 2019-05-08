#!/usr/bin/env python
# 2019/04/23: pass through rsync arguments
# when?: converted to python
import imp
readpm = imp.load_source('read_data_pm', '/mnt/lustre/scriptsForClusterNew/.read_data_pm.py')

import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--files', '-f', nargs='*')
parser.add_argument('--cluster', '-c')
parser.add_argument('--username', '-u')
parser.add_argument('--destination', '-s')
args, rsync_args = parser.parse_known_args()

uname = args.username if args.username else readpm.get_uname()
cname = args.cluster if args.cluster else readpm.specify_cluster()

datapm = readpm.read_perl_module_hashes(readpm.DATAPM)
c1 = datapm['clusters']['unified']
c2 = datapm['clusters'][cname]

command = ['rsync', '-avz', '--progress', c2['rsync_option']]

def build_command(key, arg):
    # output: [ a b1 a b2 ... ] from f(a, [ b1 b2 ... ])
    return [ x for y in [[key, x] for x in arg] for x in y ]

command.extend(build_command('--exclude', readpm.exclude))
command.extend(build_command('--include', readpm.include))

path = args.destination if args.destination else readpm.c2path(c1, c2, uname)
files = args.files if args.files else [path]
command.extend(rsync_args)
command.append(os.getcwd())
command.extend([ '{}:{}'.format(readpm.c2ip(c2, uname), os.path.join(path, x)) for x in files ])

ssh = ['ssh', c2['ssh_option'], readpm.c2ip(c2, uname), 'mkdir -p {}'.format(path)]

print(subprocess.list2cmdline(ssh))
if not '--dry-run' in rsync_args:
    subprocess.call(ssh)
print(subprocess.list2cmdline(command))
subprocess.call(command)
