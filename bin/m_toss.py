#!/usr/bin/env python
import os
import subprocess
import re

import read_data_pm as readpm

class Param():
    def __init__(self, cname=None, appli=None, qclass=None, cores=None, identifier=None, cpns=None, time=None):
        self.cname = cname
        self.appli = appli
        self.qclass = qclass
        self.cores = cores
        if identifier != 'jss':
            self.identifier = identifier
        self.cpns = cpns
        self.time = self.time

    def __str__(self):
        return '.'.join(filter(None([self.cname, self.appli, self.qclass, self.cores, self.identifier, 'jss'])))

    def __repr__(self):
        return '.'.join([self.cname, self.appli, self.qclass, self.cores, self.identifier, self.cpns, self.time])

    def __eq__(self, other):
        if isinstance(other, Param):
            # how to define this array of applis
            # just use string compare in (ugly I know)
            if self.qclass == other.qclass and self.cores == other.cores and self.identifier == other.identifier
            ( self.appli in other.appli or other.appli in self.apli):
                return True
        return False

def create_jss(requested_parameter, jss_dir=os.path.join(os.environ['CLUSTER_SCRIPTS_TOP'], 'jobSubScripts')):
    def table_lookup(filename, parameter):
        with open(filename, 'r') as data_fh:
            lines = data_fh.readlines()

            # get the keys
            # because 'class' is a python keyword, change class -> qclass
            keys = [ x.lower() for x in lines[0].split() if x.lower() != 'class' else 'qclass' ]

            # also skip '------' (lines[1])
            data_lines = lines[2:]

            for line in data_lines:
                cols =  [ l.lower() for l in line.split() ]
                if not cols:
                    continue
                # don't forget to check if zipping identifier to none
                available_parameter = Param(**{ key.lower(): value for key, value in zip(keys, line.split()) })
                print(repr(available_parameter)
                if available_parameter == parameter:
                    available_parameter.appli = parameter.appli
                    return available_parameter

            # TODO: if not found, read qc and ask if user want to make a new one
            # basically see if the input value is within the range on qc
            # qc = readpm.read_perl_module_hashes('/mnt/lustre/bin2/qc')
            raise Exception
        #endwith
    #enddef

    def construct_jss(jss_template, parameter):
        with open(jss_template, 'r') as template_fh:
            jss = template_fh.read()
            if '#VERSION' in content:
                version = readpm.input_until_correct(
                    'The available versions are {}\n'.format(' '.join(line.split()[1:])),
                    lambda x: x in line.split()[1:])
                jss = jss.replace('VERSION', version)
            for key in vars(parameter).keys():
                jss.replace(key.upper(), parameter.key.upper())
            jss.replace('JOBNAME', jname)
            return jss
        #endwith
    #enddef

    config_table = os.path.join(jss_dir, '{}.data'.format(requested_parameter.cname))
    jss_template = os.path.join(jss_dir, '{}.{}'.format(requested_parameter.cname, requested_parameter.appli))

    print(str(requested_parameter))

    final_parameter = table_lookup(config_table, requested_parameter)
    sub_filename = str(final_parameter)
    exit()

    # can this be done without side-effect (instead of writing here, return string to be written as file) ?
    with open(sub_filename, 'w') as sub_fh:
        sub_fh.write(construct_jss(jss_template, final_parameter))
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
