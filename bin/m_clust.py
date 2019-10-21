#!/usr/bin/env python

############################################
#
#   Login to supercomputer and cd to current work directory
#   Apr11  ; greatly simplified by using read_pm functions
#   Apr4   ; add option for custom ip addr
#   Mar19  ; translated to python by genki
#   next logs will be on the git commits
#
############################################

import argparse
import os
import subprocess

import read_data_pm as readpm

parser = argparse.ArgumentParser()
parser.add_argument('--cluster', '-c', type=str)
parser.add_argument('--username', '-u', type=str)
parser.add_argument('--dir', '-d', type=str)
parser.add_argument('--ip', '-i', type=str)
parser.add_argument('--shell', '-s', type=str, choices=['tcsh', 'bash'], default='tcsh')
args = parser.parse_args()

cname = args.cluster if args.cluster else readpm.specify_cluster()
uname = args.username if args.username else readpm.get_uname(cname)

datapm = readpm.read_perl_module_hashes(readpm.DATAPM)
c1 = datapm['clusters']['unified']
c2 = datapm['clusters'][cname]

path = args.dir if args.dir else readpm.c2path(c1, c2, uname, cname)

sshcd = [ 'ssh', '-t', readpm.c2ip(c2, uname), 'cd {}; {}'.format(path, args.shell) ]
print(' '.join(sshcd))
subprocess.call(sshcd)
