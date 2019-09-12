#!/usr/bin/perl
# ############################################
#
#   14Mar19  ;  Allow to manually specify jobname as argument (postponed)
#   25Oct18  ;  Implement dry run and jobdir option
#   14Jun18  ;  Fix indentations and general readability in old part of the code
#   25Apr18  ;  Tweaks and variable renaming (depart from previous confusing scheme)
#               Now read JobDir if available
#   10Apr18  ;  remove enhanced '-e' option
#   02Apr18  ;  add enhanced '-e' option
#               Append 'touch COMPLETED' at the end of sub file when -e option is added
#               remove 'COMPLETED' file at toss when -e option is used
#   14Feb18  ;  Put target directory to a (?) file
#   05Feb18  ;  Fix shown script name
#   03Feb18  ;  Add option to not delete the files (for continuing partial-fetcheds)
#   30Jan18  ;  Designate new extension '.jssc' for custom jss, to allow different handling of it
#               New format: MACHINE.(anything you want).jssc
#   29Jan18  ;  Prevent deletion of other jss while creating jss (surprisingly BAD behaviour here)
#   26Jan18  ;  Prevent deleting jss when incorrectly inputting arguments
#   12Jan18  ;  Forked by genki
#   23Jan18  ;  Do not delete jss when no matching MACHINE/.../IDENTIFIER found
#               Added functionality to skip jss making,
#               allowing the use of custom jss (by using jss file as argument)
#               Note that for compatibility with the normal workflow using other scripts,
#               jss file name should be in the format of MACHINE.(anything you want).jss
#   24Aug15  ;  First composed by ichibha
#
############################################

use Cwd;
use lib $ENV{CLUSTER_SCRIPTS_TOP};
use data;
use Getopt::Long;# qw(:config permute);
use File::Basename;
#use POSIX qw(SIGINT);
$0=basename($0);

my $a = '';
# TODO: generalize
#sub processArg {
#    $a = $_;
#    @w = split '\.', $a;
#}
GetOptions(
    'no-delete'   => sub { $no_delete = 1 },
    'dry-run'     => sub { $dry_run   = 1 },
    'jobdir' => sub { $make_jobdir = 1 },
) or die "$0: Invalid arguments\n";
$tosssyncopt = $no_delete ? '' : '--delete';
#    'name' => \my $jname,
#    '<>' => \&processArg,

my $a = $ARGV[0];
if($a eq ''){
    print "USAGE: $0 MACHINE.APPLI.CLASS.CORES(.IDENITFIER) or MACHINE.(anything).jssc\n";
    exit 0;
}



### making jss ###
&data::getUserName();
$uname = $data::userName;
&data::getJobName() ;
$jname = defined $jname? $jname: $data::jobName ;
open UNAME, '> UserName';
print UNAME "$uname\n";
close UNAME;

@w = split '\.', $a;
$cname = $w[0];
$appli = $w[1];
$class = $w[2];
$cores = $w[3];
$identifier = $w[4];
if ($a =~ /.jssc/) { #Use argument as -custom- job script whenever exists
    die "$0: $a: No such file\n" unless -e $a;
    $jssfile = $a;
    chomp $jssfile;
} else {
    if ($identifier =~ /jss/) {
        $identifier = '';
    }

    $dataf = $ENV{CLUSTER_SCRIPTS_TOP}.'/jobSubScripts/'.$cname.'.data';
    die "$0: $dataf: No such file\n" unless -e $dataf;
    $tempf = $ENV{CLUSTER_SCRIPTS_TOP}.'/jobSubScripts/'.$cname.'.'.$appli;
    die "$0: $tempf: No such file\n" unless -e $tempf;

    open  DATA ,"< $dataf";
    $_ = <DATA>;
    @keys = split;
    while (<DATA>) {
        chomp;
        @w = split;
        if ( $w[0] =~ /$class/i && $w[1] == $cores
    	  && $w[$#keys] eq $identifier
          && $class ne '' && $cores ne '' && $appli ne ''
    	  && $w[$#keys-1] =~ /$appli/i ) {
    	    for ($i=0;$i<=$#w;$i++) {
    	        $para{$keys[$i]} = $w[$i];
    	    }
    	    last;
        }
        die "$0: No matching MACHINE/APPLI/CLASS/CORES/IDENITFIER found (check with chk.pl)\n" if eof;
    }
    close DATA;

    system("rm *.jss\n");
    if ($para{IDENTIFIER} eq '') {
        $jssfile = "$cname\.$appli\.$para{CLASS}\.$para{CORES}\.jss";
    } else {
        $jssfile = "$cname\.$appli\.$para{CLASS}\.$para{CORES}\.$para{IDENTIFIER}\.jss";
    }

    open TEMP, "< $tempf";
    open JSS,  "> $jssfile";
    while (<TEMP>) {
        if (/\A#VERSION/) {
    	    print JSS $_;
    	    chomp;
    	    @w = split;
    	    print "The available versions are";
    	    for ($i=1;$i<=$#w;$i++) {
    	        print " $w[$i]";
    	    }
    	    print "\n";
    	    $version = `cat version`;
    	    chomp $version;
    	    if ($version ne '') {
    	        print "The version $version is detected\n";
    	    } else {
    	        print "please input the version\n";
    	        $version =  <STDIN>;
    	        chomp $version;
    	    }
    	    for ($i=1;$i<=$#w;$i++) {
    	        if ($version == $w[$i]) {
    	    	    print "Ver. $version is available.\n";
    	    	    last;
    	        }
    	        if ($i == $#w) {
    	    	    die "Ver. $version is not found.";
    	        }
    	    }
    	    system "echo $version > version";
    	    $_ = <TEMP>;
    	    $_ =~ s/VERSION/$version/g;
        }
        foreach $key (@keys){
    	    $_ =~ s/$key/$para{$key}/g;
        }
            $_ =~ s/JOBNAME/$jname/;
        print JSS $_;
    }
    close TEMP;
    close JSS;
}
### version ###



##### qsub part
if($cname =~ /mkei/) {
    system 'unlink casino';
    system 'unlink shm_casino';
    system 'unlink espresso';
    system 'ln -s /home/hp150271/k03110/applications/v213pl662/bin_qmc/kei/opt/casino casino';
    system 'ln -s /home/hp150271/k03110/applications/v213pl662/bin_qmc/kei/Shm/opt/casino shm_casino';
} elsif ($cname =~ /ekei/) {
    system 'unlink casino';
    system 'unlink shm_casino';
    system 'unlink espresso';
    system 'ln -s /home/hp160251/k03241/applications/v213pl662/bin_qmc/kei/opt/casino casino';
    system 'ln -s /home/hp160251/k03241/applications/v213pl662/bin_qmc/kei/Shm/opt/casino shm_casino';
}

# data.pm data
my $c1dir = $data::clusters{unified}{base_dir};
my $c2dir = $data::clusters{$cname}{base_dir};
my $c2ip   = $data::clusters{$cname}{ip_address}; $c2ip   =~ s/USER/$uname/g;
my $c2pbs  = $data::clusters{$cname}{pbs_dir};
my $c2sub  = $data::clusters{$cname}{submit};
my $c2sshopt = $data::clusters{$cname}{ssh_option};
my %cluster = %{$data::clusters{$cname}};
print %cluster{'pbs_dir'};
my $cwd = Cwd::getcwd().'/';

# related to JobDir file
my $path;
if (-s 'JobDir') {
    open JOBDIR, "< JobDir";
    $path = <JOBDIR>; chomp $path;
    print "Path in JobDir: $path\n";
    close JOBDIR;
} else {
    my $base = $cwd;
    $base =~ s/$c1dir//;
    $path = "$c2dir$base";
    $path =~ s/USER/$uname/;
    if ($make_jobdir && not $dry_run) {
        open JOBDIR, "> JobDir";
        print JOBDIR $path."\n";
        close JOBDIR;
    }
}

# if dry run, do nothing
if ($dry_run) {
    my $put = "$ENV{CLUSTER_SCRIPTS_TOP}/m_put --dry-run -c $cname --dest $path";
    system "$put $tosssyncopt";
} else {
    my $put = "$ENV{CLUSTER_SCRIPTS_TOP}/m_put -c $cname --dest $path";
    system "$put $tosssyncopt";
    #my $jobnum = `ssh $c2sshopt $c2ip "cd $path ; $c2pbs$c2sub -N $jname $jssfile"`; #pending
    my $jobnum = `ssh $c2sshopt $c2ip "cd $path ; $c2pbs$c2sub $jssfile"`;
    open JOBNUM, "> JobNumber";
    print JOBNUM $jobnum;
    close JOBNUM;
    if (-s 'JobDir') {
        system "$put JobNumber JobDir";
    } else {
        system "$put JobNumber";
    }
}
