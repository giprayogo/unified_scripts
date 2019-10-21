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
def open_rw(filename):
    """ Read lab-script-style single-line files;
        assert that they are indeed single-lined;
        Create file if not already exist """
    if filename in os.listdir('.'):
        with open(filename, 'r') as fh:
            lines = fh.readlines()
            assert len(lines) == 1
            print(lines[0].strip())
            content = lines[0].strip()
    else:
        content = input('input {}\n'.format(filename))
        with open(filename, 'w') as fh:
            fh.write(content)
    return content

def get_uname(cname=None):
    """ Read UserName file or write it if it does not exist;.
        Will not attempt to create cluster-specific UserName.CLUSTER file;
        Such file has to be created manually """
    #TODO: restructurize
    if cname:
        if 'UserName.'+cname in os.listdir('.'):
            with open('UserName.'+cname, 'r') as fh:
                lines = fh.readlines()
                assert len(lines) == 1
                print(lines[0].strip())
                return lines[0].strip()
        else:
            return open_rw('UserName')
    else:
        return open_rw('UserName')

def get_jname():
    return open_rw('JobName')

# *args and **kwargs are for supplying ADDITIONAL argument to fn
# the first argument is always the user input
def input_until_correct(text, fn, *args, **kwargs):
    while(True):
        answer = input(text)
        if fn(answer, *args, **kwargs):
            return answer

def specify_cluster():
    sub_files = [ f for f in os.listdir('.')
            if os.path.isfile(f) and re.search(r'[a-zA-Z0-9]+\.jss*', f) ]
    choices = list(set([ x.split('.')[0] for x in sub_files ]))
    if len(choices) > 0:
        if len(choices) == 1:
            sub_file = sub_files[0]
        else:
            prompt = ' '.join([ '{}:{}'.format(x, y) for x,y in enumerate(sub_files) ])
            sub_file_index = int(input_until_correct('choose one *.jss_file: {}\n'.format(prompt),
                lambda x,y: x in y, list(map(str, range(0, len(sub_files)))) ))
            sub_file = sub_files[sub_file_index]
        assert len(sub_file.split('.')) > 1
        cluster = sub_file.split('.')[0]
    else:
        datapm = read_perl_module_hashes(DATAPM)
        valid  = [ {k: v} for k, v in datapm['clusters'].items() if v['type'] == 'calculation' or v['type'] == 'backbone' ]
        keys = sorted([ list(k)[0] for k in valid ]) # for better clarity
        cluster = input_until_correct(', '.join(keys) + '\n', lambda x,y: x in y, keys)
        print(cluster)
    return cluster

#TODO: work in progress
def get_command_outputs(command, ip, sh='ssh', port=22, to=35):
    process = subprocess.Popen([sh, '-p', str(port), ip, command], stdout=subprocess.PIPE)
    return process.stdout

# "cluster 2" derivations
def c2path(c1, c2, uname, cname):
    """ return toss/fetch path from c1 to c2, given the username
    will read JobDir file if it is given """
    #try: # first try to see if there are any cluster-specific JobDir; JobDir.CLUSTERNAME
    filenames = os.listdir('.')
    if any([ x for x in filenames if 'JobDir' in x ]):
        if 'JobDir.'+cname in filenames:
            jobdir = 'JobDir.'+cname
        else:
            jobdir = 'JobDir'

    # keep try-except for now; better alternative in the future
    try:
        with open(jobdir, 'r') as fh:
            lines = fh.readlines()
            assert len(lines) == 1
            return lines[0].strip()
    except IOError:
            return os.path.join(c2['base_dir'].replace('USER', uname), os.getcwd().replace(c1['base_dir'], '').lstrip('/'), '')

def c2ip(c2, uname):
    """ return complete ip address for c2 with substituted username """
    return c2['ip_address'].replace('USER', uname)

def cat_iffile(filename):
    """ return content of a file if it is an existing filename in current directory """
    if filename in os.listdir('.'):
        with open(filename, 'r') as _:
            lines = _.readlines()
            assert len(lines) == 1
        return lines[0]
    else:
        return filename
