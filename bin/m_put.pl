#!/usr/bin/perl
#############################################
#
#   25Oct18  ;  Implement dry run option
#   25Apr18  ;  Allow to specify custom destination, general cleanup
#               Add include and exclude
#   05Feb18  ;  Add 'help' option
#   03Feb18  ;  Finished new parsing
#   30Jan18  ;  update: not a fan of how both scripts work (aput mindlessly use *jss where it does not exists, data::specifyCluster(), put does not check for arguments
#               solution: make it an independent script that works more like rsync but fitted for clusters and use data.pm's data
#   30Jan18  ;  This is more like a subsitute to aput.pl (but with multiple files capability)
#               Therefore make it more like aput (name, behaviour, and minimal diff)
#               Except for last part, where put.pl's rsync is superior
#   11Jan18  ;  Forked by genki
#               Added function to transfer individual files when supplied
#   24Aug15  ;  First composed by ichibha
#
############################################
#TODO: pass rsync options directly to rsync

use Cwd;
use lib $ENV{CLUSTER_SCRIPTS_TOP}; 
use data;
use Getopt::Long;
use File::Basename;
use File::Spec::Functions 'catfile';
#use warnings;
$0=basename($0);

my $delete = 0;
my $help = 0;
my $dry_run = 0;
GetOptions( 'cluster=s' => \my $cname,
            'username=s' => \my $uname,
            'exclude=s' => \my @excludes,
            'include=s' => \my @includes,
            'destination=s' => \my $dest,
            'help' => sub { $help = 1 },
            'delete' => sub { $delete = 1 },
            'dry-run' => sub { $dry_run = 1},
) or die "$0: Invalid arguments\n"; die "Usage: $0 [OPTION]... [FILE]...\n" if $help;
$cname = defined $cname ? $cname : &data::specifyCluster();
$cname = $cname eq '' ? &data::inputCluster() : $cname;
$rsyncopt = $delete ? '--delete' : '';
if ($uname eq '') {
  &data::getUserName();
  $uname = $data::userName;
}

my $c1dir = $data::clusters{unified}{base_dir};
my $c2dir = $data::clusters{$cname}{base_dir};
my $c2ip   = $data::clusters{$cname}{ip_address}; $c2ip =~ s/USER/$uname/;
my $c2rsyncopt = $data::clusters{$cname}{rsync_option};
my $c2sshopt  = $data::clusters{$cname}{ssh_option};
my $cwd = Cwd::getcwd().'/';

my $path;
if (defined $dest) {
  $path = $dest;
} else {
  my $base = $cwd;
  $base =~ s/$c1dir//;
#  $base =~ s/$c1dir2//;
  $path = "$c2dir$base";
  $path =~ s/USER/$uname/;
}

my @files = @ARGV;
my $files = @files ? '' : $cwd;
foreach my $filename (@files) {
  die "$0: $filename: No such file\n" unless -e $filename;
  $files .= " ".catfile($cwd,$filename);
}

my $rsyncin = '';
my $rsyncex = '';
foreach my $include (@includes) {
  $rsyncin = $rsyncin." --include=\"$include\" ";
}
foreach my $exclude (@excludes) {
  $rsyncex = $rsyncex." --exclude=\"$exclude\" ";
}

my $ssh = "ssh $c2sshopt $c2ip 'mkdir -p $path'";
my $rsync = "rsync -avz --progress $data::exclude $data::include $rsyncin $rsyncex $rsyncopt $c2rsyncopt $files $c2ip\:$path";

print $ssh."\n";
print $rsync."\n";
unless ($dry_run) {
    system $ssh;
    system $rsync;
}
