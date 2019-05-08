#!/usr/bin/perl
#
#   Script to create JobDir files in current directory (to allow changing of directory structure when using unified system)
#   (01/11/2018) : remove multiple dir capability (useless)
#   (30/06/2018) : First written by genki
#
#
use Cwd;
use lib $ENV{CLUSTER_SCRIPTS_TOP};
use data;
use Getopt::Long;
use File::Basename;
use File::Spec::Functions 'catfile';
use warnings;
use strict;
$0=basename($0);

my $help = 0;
GetOptions( 'cluster=s' => \my $cname,
            'username=s' => \my $uname,
            'help' => sub { $help = 1 },
) or die "$0: Invalid arguments\n"; die "Usage: $0 [OPTION]... [JOBDIR]...\n" if $help;
#my @dirs = @ARGV ? @ARGV : '.';

$cname = defined $cname ? $cname : &data::specifyCluster();
$cname = $cname eq '' ? &data::inputCluster() : $cname;
if (! defined $uname) {
  &data::getUserName();
  $uname = $data::userName;
}

my $c1dir = $data::clusters{unified}{base_dir};
my $c2dir = $data::clusters{$cname}{base_dir};
my $c2ip   = $data::clusters{$cname}{ip_address}; $c2ip =~ s/USER/$uname/g;
my $c2pbs  = $data::clusters{$cname}{pbs_dir};
my $c2sub  = $data::clusters{$cname}{submit};
my $c2sshopt = $data::clusters{$cname}{ssh_option};
my $cwd = Cwd::getcwd();

my $path = $ARGV[1] ? $ARGV[1] : $cwd.'/';
my $jobdir = catfile($path,'JobDir');
my $cluster_path;
if (-s $jobdir) {
  open JOBDIR, "< $jobdir";
  $cluster_path = <JOBDIR>; chomp $cluster_path;
  close JOBDIR;
  print "JobDir exists: $cluster_path\n";
} else {
  my $base = $path;
  $base =~ s/$c1dir//;
  $cluster_path = "$c2dir$base";
  $cluster_path =~ s/USER/$uname/;
  open JOBDIR, "> $jobdir";
  print JOBDIR $cluster_path."\n";
  close JOBDIR;
  print "JobDir created: $cluster_path\n";
}
