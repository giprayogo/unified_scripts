#!/usr/bin/perl
#
# Script to check whether authorized_keys list was manually edited
# without using registerSSH
# (?/6/2018) : First written by genki
#
use strict;
use warnings;
use File::Spec::Functions 'catfile';
use Data::Dumper;

my $ssh_auth = '/home/maezono/.ssh/authorized_keys';
my $reg_auth_dir = '/mnt/lustre/scriptsForClusterNew/public_keys/';
my @users;

opendir(AUTH_DIR, $reg_auth_dir) or die $!;
while (readdir(AUTH_DIR)) {
  my $auth_file = catfile($reg_auth_dir,$_);
  if (-f $auth_file) {
    my %user;
    open(AUTH_FILE, $auth_file) or die $!;
    while(<AUTH_FILE>) {
      my @cols = split(/\s+\:\s+/, $_);
      if (/Name/) {
        $user{'name'} = $cols[1];
#        print $user{'name'};
      }
      if (/Public\ Key/) {
        $user{'key'} = $cols[1];
        #print $_;
      }
    }
    close(AUTH_FILE);
    push(@users,\%user);
  }
}
closedir(AUTH_DIR);
open(SSH_AUTH, $ssh_auth) or die $!;
AUTH:
while(<SSH_AUTH>) {
  my $auth_key = $_;
  USER:
  foreach my $user (@users) {
    my $user_name = defined %$user{'name'} ? %$user{'name'} : "no-name\n";
    my $user_key = defined %$user{'key'} ? %$user{'key'}
                   : do { print "Warning, no registered key for user $user_name"; next USER; };
    if ( $auth_key eq $user_key ) {
        #print "Authorized key for user $user_name";
      next AUTH;
    }
  }
  #print "Illegal non-registered key: $auth_key";
}
close(SSH_AUTH);
print Dumper(@users);
