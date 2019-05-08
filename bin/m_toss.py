#!/usr/bin/env python
# toss.pl; reworked with python; experimental ; use minimal libraries
# 2019/04/23: pass rsync arguments; delegate JobDir making to m_jobdir
# 2019/03/08 ; first work

import read_data_pm as readpm

import os
import subprocess
import re

# TODO: for auto sub thing; design not finalized
# from threading import Timer
# secs = 3600
# auto = Timer(secs, function)

def build_lol(filename):
    with open(filename, 'r') as fh:
        return [ x.split() for x in fh.readlines() ]

class Param():
    def __init__(self, cname=None, appli=None, qclass=None, cores=None, identifier=None):
        self.cname = cname
        self.appli = appli
        self.qclass = qclass
        self.cores = cores
        if identifier != 'jss':
            self.identifier = identifier

    def __str__(self):
        return '.'.join([self.cname, self.appli, self.qclass, self.cores, 'jss'])

# TODO: rewrite in pythonic way
# also I don't like how this function has a lot of side effects (writing files), can we split/rewirte?
# and then also the dual dictionary thing which seems unnecessary
def create_jss(parameter):
    #print([cname, appli, qclass, cores, identifier])

    jss_dir = os.path.join(os.environ['CLUSTER_SCRIPTS_TOP'], 'jobSubScripts')
    config_table = os.path.join(jss_dir, '{}.data'.format(parameter.cname))
    jss_template = os.path.join(jss_dir, '{}.{}'.format(parameter.cname, parameter.appli))

    # TODO: be more pythonic
    found = False
    para = {}

    # still translated from original
    # seemingly this part only verify and nothing else
    # lookup AND getting cpns
    # can be compacted/omitted ?
    # especially if we can combine with qc
    with open(filename, 'r') as data_fh:
        lines = data_fh.readlines()

        # get the keys
        header_line = lines[0]
        keys = [ c.lower() for c in header_line.split() ]
        #para = { key: None for key in header_line.split() }

        # skip '------' (lines[1])

        # verify data
        data_lines = lines[2:]

        # helper, will be deleted
        # cols[1] : cores
        # cols[6] : identifier
        # cols[5] : appli
        # cols[0] : qclass
        for line in data_lines:
            cols =  [ l.lower() for l in line.split() ]
            if not cols:
                continue
            #print(cols)
            if parameter.identifier:
                if parameter.qclass == cols[0] and cols[1] == parameter.cores and cols[6] == parameter.identifier and parameter.appli in cols[5].split('/'):
                    for i, col in enumerate(cols):
                        para[keys[i]] = cols[i]
                        found = True
            else:
                if parameter.qclass == cols[0] and cols[1] == parameter.cores and parameter.appli in cols[5].split('/'):
                    for i, col in enumerate(cols):
                        para[keys[i]] = cols[i]
                        found = True

    assert found
    exit()

    sub_filename = str(parameter)

    # writing function
    # can this be done without side-effect (instead of writing, return string to be written as file) ?
    with open(jss_template, 'r') as template_fh, open(sub_filename, 'w') as sub_fh:
        for line in template_fh:
            if '#VERSION' in line:
                version = readpm.input_until_correct(
                        'The available versions are {}\n'.format(' '.join(line.split()[1:])),
                        lambda x: x in line.split()[1:])
                line = line.replace('VERSION', version)

            # TODO: pythonic
            for key in para.keys():
                line.replace(key.upper(), para[key].upper())
            line.replace('JOBNAME', jname)
            sub_fh.write(line)
    return sub_filename

# functions related to the k-computer? I don't know if these are still relevant
def unlink(link):
    print(' '.join(['unlink', link]))
    #subprocess.call(['unlink', link])
def link(filename, link):
    print(' '.join(['ln', '-s', filename, link]))
    #subprocess.call(['ln', '-s', filename, link])

if __name__ == '__main__':
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('param',
            help='Toss parameter (see chk.pl), in this format: MACHINE.APPLI.CLASS.CORES(.IDENITFIER) or MACHINE.(anything).jssc',
            metavar='SPEC')
    parser.add_argument('--make-jobdir', action='store_true')
    parser.add_argument('--no-delete', action='store_true')
    args, rsync_args = parser.parse_known_args()
    tosssyncopt = '--delete' if not args.no_delete else ''

    # read perl module
    datapm = readpm.read_perl_module_hashes('/mnt/lustre/scriptsForClusterNew/data.pm')
    # planned feature to be able to add new entry to chk.pl
    # basically see if the input value is within the range on qc
    qc = readpm.read_perl_module_hashes('/mnt/lustre/bin2/qc')

    uname = readpm.get_uname()
    jname = readpm.get_jname()

    # TODO: comparing with template is perhaps better?
    # rule 1: always re-submit modified files regardless what;
    # rule 2: do not delete modified job scripts
    # pseudo code:
    # make temp_job_script
    # if parameter is a file and exist and different from temp
    #   toss with file; rm temp
    # else
    #   toss using temp
    #   delete previous modifications
    # deletion should only be done if wanted
    # subprocess.call(['rm', '*.jss'])
    # print('rm *.jss')

    parameter = Param(*[ s.lower()  for s in args.param.split('.') ])

    job_script = args.param if re.match(r'[A-Za-z0-9]*.jssc', args.param) else create_jss(parameter)
    exit()

    # it's here because we have to define the cluster name first
    cname = readpm.specify_cluster()

    # k supercomputer stuffs, are these relevant?
    if 'mkei' in cname:
        unlink('casino')
        unlink('shm_casino')
        unlink('espresso')
        link('ln -s /home/hp150271/k03110/applications/v213pl662/bin_qmc/kei/opt/casino', 'casino')
        link('ln -s /home/hp150271/k03110/applications/v213pl662/bin_qmc/kei/Shm/opt/casino', 'shm_casino')
    elif 'ekei' in cname:
        unlink('casino')
        unlink('shm_casino')
        unlink('espresso')
        link('ln -s /home/hp160251/k03241/applications/v213pl662/bin_qmc/kei/opt/casino', 'casino')
        link('ln -s /home/hp160251/k03241/applications/v213pl662/bin_qmc/kei/Shm/opt/casino', 'shm_casino')

    # data.pm data
    c1 = datapm['clusters']['unified']
    c2 = datapm['clusters'][cname]
    print(c1['pbs_dir'])

    # related to JobDir file
    # TODO: perhaps we can do without calling? need to restructure m_jobdir
    if args.make_jobdir:
        subprocess.call('m_jobdir.pl')

    # put the files
    put = [ os.path.join(os.environ['CLUSTER_SCRIPTS_TOP'], 'm_put.pl'), '-c', cname, '--dest', path, tosssyncopt ]
    put.extend(rsync_args)
    print(subprocess.list2cmdline(put))
    #subprocess.call(put)

    # qsub and save the job number
    get_jobnumber = [ 'ssh', c2['ssh_option'], readpm.c2ip(c2, uname), '\"cd {} ; {} {}\"'.format(path, os,path.join(c2['pbs_dir'], c2['submit']), job_script) ]
    print(subprocess.list2cmdline(get_jobnumber))
    with open('JobNumber', 'w') as jobnumber:
        lines = readpm.get_command_outputs(ret_jn_cmd, readpm.c2ip(c2, uname))
        assert len(lines) == 1
        jobnumber.write(lines[0])

    # don't forget to put it too
    put_jobnumber = [ put, 'JobNumber' ]
    print(subprocess.list2cmdline(put_jobnumber))
    #subprocess.call(put_jobnumber)
