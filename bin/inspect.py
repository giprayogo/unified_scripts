#!/usr/bin/env python
# inspect, converted to python

import datapm
import re
import os

separator = ''
shoutno    = '{}False ----------------------------- NO!!!!'.format(separator) # Error, immediately fix
shoutnoyes = '{}False - - - - - - - - - - - - - - - NO...!'.format(separator) # Warning, prepare to fix
shoutyes   = '{}True'.format(separator)
shoutsync = '{}Rsync'.format(separator) # Used for collect

print('+++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
print('                                                      \n')
print('*01/External accesses and Crond deamon ---------------\n')

rt01_name      = 'router01'
rt01_ipaddr    = '192.168.0.92'
rt01_chkitems  = 'alive fs_err'

rt02_name      = 'router02'
rt02_ipaddr    = '192.168.0.221'
rt02_chkitems  = 'alive fs_err'

uni04_name     = 'unified04'
uni04_ipaddr   = '192.168.0.5'
uni04_chkitems = 'alive crond fs_err'

uni05_name     = 'unified05'
uni05_ipaddr   = '192.168.0.220'
uni05_chkitems = 'alive fs_err'

uni06_name     = 'unified06'
uni06_ipaddr   = '192.168.0.219'
uni06_chkitems = 'alive cron_ubuntu fs_err'

uni07_name     = 'unified07'
uni07_ipaddr   = '192.168.0.7'
uni07_chkitems = 'alive cron_ubuntu fs_err'

uni10_name     = 'unified10'
uni10_ipaddr   = '192.168.0.10'
uni10_chkitems = 'alive cron_ubuntu fs_err'

you03_name     = 'youmono03'
you03_ipaddr   = '192.168.0.218'
you03_chkitems = 'alive crond fs_err'

you04_name     = 'youmono04'
you04_ipaddr   = '192.168.0.233'
you04_chkitems = 'alive fs_err'

deadOrAlive(rt01_name, rt01_ipaddr, rt01_chkitems , 'ssh')
deadOrAlive(rt02_name, rt02_ipaddr, rt02_chkitems , 'ssh')
deadOrAlive(uni07_name, uni07_ipaddr, uni07_chkitems, 'ssh')
deadOrAlive(uni10_name, uni10_ipaddr, uni10_chkitems, 'ssh')
deadOrAlive(you03_name, you03_ipaddr, you03_chkitems, 'ssh')
deadOrAlive(you04_name, you04_ipaddr, you04_chkitems, 'ssh')

###################################################################
print('\n*02/File Servers (unified) ---------------------------\n')
###################################################################
unified_file_servers = [
    {
        'name'      : 'uNFS_wrk',
        'ip'        : '192.168.0.237',
        'chk_items' : 'alive crond fs_err',
        'hdd' : [
                '/mnt/hdd',
                '/mnt/hdd2',
                '/mnt/hdd3',
        ],
    },
    {
        'name'      : 'uNFS_wrk2',
        'ip'        : '192.168.0.239',
        'chk_items' : 'alive crond fs_err',
        'hdd' : [
                '/mnt/hdd4',
        ],
    },
    {
        'name'      : 'uNFSs_stb',
        'ip'        : '192.168.0.238',
        'chk_items' : 'alive cron_ubuntu fs_err',
        'hdd' : [
                '/mnt/hdd',
                '/mnt/hdd2',
                '/mnt/hdd3',
        ],
    },
    {
        'name'      : 'uNFSs_stb2',
        'ip'        : '192.168.0.240',
        'chk_items' : 'alive crond fs_err',
        'hdd' : [
                '/mnt/hdd4',
        ],
    },
]

for server in unified_file_servers:
    ip = server['ip']
    if deadOrAlive(server['name'], ip, server['chk_items']):
        for hdd in server['hdd']:
            checkVolume(ip, hdd)
            checkW4(ip, hdd)

####################################################################
print('\n*03/File Servers (youmono) ---------------------------\n')
####################################################################
youmono_file_servers = [
    {
        'name'      : 'yNFS_wrk',
        'ip'        : '192.168.0.8',
        'chk_items' : 'alive crond fs_err',
        'hdd' : [
                '/mnt/6t03', #work
                '/mnt/2t01',
        ],
    },
    {
        'name'      : 'yNFSs_stb',
        'ip'        : '192.168.0.9',
        'chk_items' : 'alive crond fs_err',
        'hdd' : [
                '/mnt/6t04', #work
                '/mnt/3t02',
        ],
    },
]

for server in youmono_file_servers:
    if deadOrAlive(server->{'name'}, server['ip'], server['chk_items']):
        for hdd in server['hdd']:
            checkVolume(server['ip'], hdd)
            checkW4(server['ip'], hdd)

###################################################################
print('\n*04/Collect Servers ----------------------------------\n')
###################################################################
collect_servers = [
    {
        'name'      : 'collectSH02',
        'ip'        : '192.168.0.231',
        'chk_items' : 'alive cron_ubuntu fs_err',
        'box' : [
            {
                'destination' : '/etc/ccollect/sources/collectsh1/destination',
                'source'      : '/etc/ccollect/sources/collectsh1/source',
            },
            {
                'destination' : '/etc/ccollect/sources/collectsh2/destination',
                'source'      : '/etc/ccollect/sources/collectsh2/source',
            },
            {
                'destination' : '/etc/ccollect/sources/collectsh3/destination',
                'source'      : '/etc/ccollect/sources/collectsh3/source',
            },
        ],
    },
    {
        'name'      : 'collectSH03',
        'ip'        : '192.168.0.232',
        'chk_items' : 'alive crond fs_err',
        'box' : [
            {
                'destination' : '/etc/ccollect/sources/collectsh4/destination',
                'source'      : '/etc/ccollect/sources/collectsh4/source',
            },
        ],
    },
    {
        'name'      : 'collectLL',
        'ip'        : '192.168.0.12',
        'chk_items' : 'alive cron_ubuntu',
        'box' : [
            {
                'destination' : '/etc/ccollect/sources/collectll/destination',
                'source'      : '/etc/ccollect/sources/collectll/source',
            },
            {
                'destination' : '/etc/ccollect/sources/collectll2/destination',
                'source'      : '/etc/ccollect/sources/collectll2/source',
            },
            {
                'destination' : '/etc/ccollect/sources/collectll3/destination',
                'source'      : '/etc/ccollect/sources/collectll3/source',
            },
            {
                'destination' : '/etc/ccollect/sources/collectll4/destination',
                'source'      : '/etc/ccollect/sources/collectll4/source',
            },
        ],
    },
]

for server in collect_servers:
    if deadOrAlive(server['name'], server['ip'], server['chk_items']):
        for box in server['box']:
            destination, latest, source = getBackupInfo(server['ip'], box['destination'], box['source'])
            source = re.sub(b'[0-9.]+\:', source)
            checkVolume(server['ip'], destination)
            checkW4(server['ip'], os.path.join(destination, latest, source), destination)

###################################################################
print "\n*05/Archive Servers ----------------------------------\n"
###################################################################
archive_servers = [
    {
        'name' : 'arch02',
        'ip' : '192.168.0.3',
    },
    {
        'name' : 'arch03',
        'ip' : '192.168.0.13',
    },
    {
        'name' : 'arch04',
        'ip' : '192.168.0.11',
    },
]

for server in archive_servers:
    #datapm.displayDoa(server['name'}, &data::deadOrAlive(server['ip']))
    checkVolume(server['ip'], '/mnt/alpha')

print('                                                      \n')
print('++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')

def deadOrAlive(name, ipaddr, chk_items, shell='ssh', port):
    alive_flag = shoutno
    crond_flag = shoutno
    is_alive = 0
    error_fs
    # TODO: more pythonic all the way
    if 'alive' in chk_items:
        lines1 = datapm.getCommandOutputs('ls /', ipaddr, shell, port)
        for line in lines1:
            if 'root' in line:
                alive_flag = shoutyes
                is_alive = True
	        break	
    # TODO: auto detect and retry
    if 'crond' in chk_items:
        lines2 = datapm.getCommandOutputs('systemctl status crond', ipaddr, shell, port)  
        for line in lines2:
            if 'running' in line:
                crond_flag = shoutyes
                break
    if 'cron_ubuntu' in chk_items:
        # @lines2     = &data::getCommandOutputs('service cron status', $ipaddr, $shell, $port)  
	     @lines2     = &data::getCommandOutputs('systemctl status cron', $ipaddr, $shell, $port)  
	    foreach(@lines2){
	        if(/running/){
	    	    $crond_flag = $shoutyes
	    	    last
	        }
	    }
    }
    if 'fs_err' in chk_items:
        date = datetime.date.today().strftime('%b%_d')
        os.write(2, date)
        dmesg_string = '\n'.join(datapm.getCommandOutputs('dmesg -e', ipaddr, shell, port))
        dmesg_string =~ /.*?($date.*)/s
        @today_dmesg = $1? split(/\n/, $1) : ''
        foreach(@today_dmesg) {
            # we only have ext4 drives
            if ($_ =~ 'EXT4-fs error') {
                $_ =~ /.*device (sd[a-z])\).*/
                #print $1 ?  "#$1\n" : $_
                $error_fs{"$1"} = 1 if ($1)
            }
        }
    }
    space = '                     '
    print('\n##$name##\n')
    if 'alive' in chk_items:
        print('Node is alive                $space $alive_flag\n')
    if 'cron' in chk_items:
        print('Crond is Working             $space $crond_flag\n')
    if 'fs_err' in chk_items:
        for keys in error_fs.keys():
            print('File system errors on /dev/$_ $space $shoutno\n')
    return is_alive

def getBackupInfo {
     $ipaddr   = $_[0]
     $dist     = $_[1]
     $dsst     = $_[2]
     $shell    = $_[3] // 'ssh'
     $port     = $_[4]
     $backup = 'daily.0'
     @lines
     $box
     $source

    @lines = &data::getCommandOutputs("cat $dist", $ipaddr, $shell, $port)
    $box = $lines[0] chomp $box
    @lines = &data::getCommandOutputs("cat $dsst", $ipaddr, $shell, $port)
    $source = $lines[0] chomp $source
    print STDERR "$box\n"
    foreach (&data::getCommandOutputs("ls -1 $box/", $ipaddr, $shell, $port)) {
        #print STDERR "$_\n"
	$backup =~ /[a-z]+\.([0-9]+)/
        #print STDERR "$1\n"
	 $tmp = $1 ? $1 : 0
        #print "\$tmp = $tmp\n"
        #$_ =~ /[a-z]+\.([0-9]+)\-/ #\- not necessary
	$_ =~ /[a-z]+\.([0-9]+)/
         $next = $1 ? $1 : 0 #In case we have non=daily.xxx directory names
	$backup = $_ if ($tmp < $next)
    }
    chomp $backup
    print "    latest BU = $backup\n"
    return ($box, $backup, $source)
}

def checkVolume(ipaddr, mnt_dir, rsync_dir=None, chk_rsync=True, shell='ssh', port=22):
    if rsync_dir is None:
        rsync_dir = mnt_dir

    capacity = 0
    used     = ''
    percent  = ''

    for line in datapm.getCommandOutputs('df', ipaddr, shell, port):
        if (!/\s$mnt_dir\s*\Z/):
	    continue
        w = line.split
        capacity = w[-4]
	used     = w[-3]
	percent  = w[-1]
	percent = percent.replace('%', '')
    flag
    if percent != '':
        if percent == 100:
            flag = shoutno + ' (100%!!!)'
        else:
            flag = 'OK' if ($percent < 90) else $shoutnoyes + ' (due to>90%)'
    else:
        flag = shoutno + ' (not mounted?)'

    rsyncing = datapm.get_command_outputs('ps -ef | grep -E \'rsync.+$rsync_dir( |/)\'', ipaddr, shell, port)
    if chk_rsync && rsyncing:
        w = re.split(b'\s+', rsyncing[0])
        start_rsync = w[4]
        fullshout = shoutsync + ' (' + $start_rsync + ')'
        substr(flag, 0, length(fullshout)) = fullshout
    print('    $mnt_dir: \n')
    print('        volume = {:11} / {:11} ({:3})   {}\n'.format(used, capacity, percent, flag))

#TODO: fix W4dir
def checkW4(ipaddr, W4dir, dir_rsyny=W4dir, chk_rsync=True, shell='ssh', port):
    existence_flag = shoutno
    consistency_flag = shoutno
    $dayOfw4 = ''
    $today      = `date "+%Y%m%d"` chomp $today
    $yesterday  = `date -d '1 day ago' "+%Y%m%d"` chomp $yesterday
    $twodaysago = `date -d '2 day ago' "+%Y%m%d"` chomp $twodaysago
    @lines = &data::getCommandOutputs('ls -l --time-style=+%Y%m%d '.catfile($W4dir,'toBeSync'), $ipaddr, $shell, $port)
    foreach (@lines) {
        if (/wwww/) {
	        $existence_flag = $shoutyes
             @w = split
            $dayOfw4 = $w[5]
	        if ($dayOfw4 eq $today || $dayOfw4 eq $yesterday || $dayOfw4 eq $twodaysago) {
		        $consistency_flag = $shoutyes
	        }
            #print "        $today\-$yesterday\n"
        }
    }
    @rsyncing = &data::getCommandOutputs("ps -ef | grep -E 'rsync.+$dir_rsync( |/)'", $ipaddr, $shell, $port)
    if ($chk_rsync && @rsyncing) {
         @w = split(/\s+/, $rsyncing[0])
         $start_rsync = $w[4]
         $fullshout = $shoutsync.' ('.$start_rsync.')'
        substr($consistency_flag, 0, length($fullshout)) = $fullshout
        substr($existence_flag, 0, length($fullshout))  = $fullshout
    }
    $space = '                      '
    printf "        wwww existence $space      $existence_flag\n"
    printf "        wwww date (%8s)$space $consistency_flag\n",$dayOfw4
}
