#!/usr/bin/perl

############################################
#
#   24Aug26  ;  First composed by ichibha
#   1Aug17   ;  Forked by genki
#               Replaced the location of kill IF within autorunning sleep loop (MUCH safer)
#               Added indicator files to mark the script's current state
#
############################################

use Cwd;
use lib $ENV{CLUSTER_SCRIPTS_TOP};;
use data;

$toss = $ENV{CLUSTER_SCRIPTS_TOP}.'/toss.pl';
$fetch = $ENV{CLUSTER_SCRIPTS_TOP}.'/fetch.pl';
$qdel = $ENV{CLUSTER_SCRIPTS_TOP}.'/qdel.pl';
$qa   = $ENV{CLUSTER_SCRIPTS_TOP}.'/qa.pl';
$ENV{CLUSTER_SCRIPTS_TOP};

open DAT, '< autorunner.dat';
while (<DAT>){
    if(/number\sof\sbegin/){
	@w = split;
	$begin = $w[$#w];
    } elsif (/number\sof\send/) {
	@w = split;
	$end = $w[$#w];
    } elsif (/queue\sclass/) {
	@w = split;
	$queue = $w[$#w];
    } elsif (/script/) {
	@w = split;
	$script = $w[$#w];
    } elsif (/interval/) {
	@w = split;
	$interval = $w[$#w];
    }
}
close DAT;

@w = split /\./, $queue;
$machine = $w[0];

print "begin    = $begin\n";
print "end      = $end\n";
print "queue    = $queue\n";
print "script   = $script\n";
print "machine  = $machine\n";
print "interval = $interval";

system "touch AUTO_RUNNING";
system "rm AUTO_STOPPED";
system "rm AUTO_COMPLETED";

$begin--;
$count=$begin;

while(){
    if( !(-e 'AUTO_RUNNING') ) {
        print "running is not found, so it stops.\n";
        system "touch AUTO_STOPPED";
	# system $qdel;
	exit;
    }
    $number = `cat JobNumber`;
    chomp $number;
    print `$qa $machine | grep -c $number`."\n";
    if (`$qa $machine | grep -c $number` > 0 ){
	print "sleap $interval seconds...\n";
	sleep $interval;
	next;
    }
    if($count != $begin){
	system "$fetch";
	system "./$script $count";
	if($count == $end){
            system "rm AUTO_RUNNING";
            system "touch AUTO_COMPLETED";
	    last;
	}
    }
    system "rm JobNumber";
    system "$toss $queue";
    print "sleap $interval seconds...\n";
    sleep $interval;
    $count++;
}
