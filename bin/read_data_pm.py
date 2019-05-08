#!/usr/bin/env python
# use as little libraries as possible
# read data.pm informations; implement equivalent functions
import re
import os
import sys
import subprocess
#import threading
if sys.version_info.major == 3:
    import builtins

DATAPM = '/mnt/lustre/scriptsForClusterNew/data.pm'
# include and excludes; since it is a bit cumbersome to implement
#include = [ '[0-9]*' ] # I don't want to include this one since it causes problem with numbered directory names
include  = []
exclude = [ '*rubbish*', 'reblock', 'core', 'gamess.F*', '*.pid', 'mpd.hosts', '[0-9][0-9]*', '[0-9]_*' ]

# Python 2--3 compatibility
def input(*args, **kwargs):
    if sys.version_info.major == 3:
        return builtins.input(*args, **kwargs)
    else:
        return raw_input(*args, **kwargs)

def hash_generator(hlist):
    extracted_hashes = {}
    extracted_hashes[hlist[0]] = {}
    if len(hlist) > 2:
        extracted_hashes[hlist[0]] = hash_generator(hlist[1:])
    else:
        extracted_hashes[hlist[0]] = hlist[1]
    return extracted_hashes

def update_hash_of_hash(big, insert):
    bigkey = big.keys()
    smallkey = insert.keys()
    intersects = list(set(bigkey).intersection(smallkey))
    for inter in intersects:
        if intersects and isinstance(big[inter], dict) and isinstance(insert[inter], dict):
            update_hash_of_hash(big[inter], insert[inter])
            return big
    #print("INSERT {} {}".format('', insert))
    big.update(insert)
    return big

def read_perl_module_hashes(pm_filename):
    pm_hash = {}
    with open (pm_filename, 'r') as pm_fh:
        for line in pm_fh:
            # look for hash lines
            if re.search(r'^\$[a-zA-Z0-9_]+\{[a-zA-Z0-9_]+}', line) and not re.match('#', line):
                hlist = [ x.strip('\'').strip('$')
                        for x in re.split(r'[{}]+', re.sub(r'\s*\=\s*', '', line.strip().rstrip(';'))) ]
                #print("DET {}".format(hlist))
                update_hash_of_hash(pm_hash, hash_generator(hlist))
    return pm_hash

#TODO; fancier pattern here
def rw_spec_file(spec_filename):
    try:
        with open(spec_filename, 'r') as spec_file:
            lines = spec_file.readlines()
            assert len(lines) == 1
            print(lines[0].strip())
            spec = lines[0].strip()
    except IOError:
        spec = input('input {}\n'.format(spec_filename))
        with open(spec_filename, 'w') as spec_file:
            spec_file.write(spec)
    return spec

def get_uname():
    return rw_spec_file('UserName')
def get_jname():
    return rw_spec_file('JobName')

def input_until_correct(text, fn):
    while(True):
        answer = input(text)
        if fn(answer):
            return answer

def specify_cluster():
    sub_files = [ f for f in os.listdir('.')
            if os.path.isfile(f) and re.search(r'[a-zA-Z0-9]+\.jss*', f) ]
    if len(sub_files) > 0:
        if len(sub_files) == 1:
            sub_file = sub_files[0]
        else:
            sub_file = input_until_correct('choose one .jss_file: {}\n'.format(' '.join(sub_files)), os.path.exists)
        assert len(sub_file.split('.')) > 1
        cluster = sub_file.split('.')[0]
    else:
        datapm = read_perl_module_hashes(DATAPM)
        valid  = [ {k: v} for k, v in datapm['clusters'].items() if v['type'] == 'calculation' or v['type'] == 'backbone' ]
        keys = sorted([ list(k)[0] for k in valid ]) # for better clarity
        cluster = input_until_correct(', '.join(keys) + '\n', lambda x: x in keys)
        print(cluster)
    return cluster

#TODO: work in progress
def get_command_outputs(command, ip, sh='ssh', port=22, to=35):
    process = subprocess.Popen([sh, '-p', str(port), ip, command], stdout=subprocess.PIPE)
    return cmdpipe.stdout

def c2path(c1, c2, uname):
    try:
        with open('JobDir', 'r') as jobdir_fh:
            lines = jobdir_fh.readlines()
            assert len(lines) == 1
            return lines[0].strip()
    except IOError:
        return os.path.join(c2['base_dir'].replace('USER', uname), os.getcwd().replace(c1['base_dir'], '').lstrip('/'), '')

def c2ip(c2, uname):
    return c2['ip_address'].replace('USER', uname)
