#!/usr/bin/perl
#
# this script prints out a random line from stdin or any files provided on the
# command line.  this is one of my favorite scripts because its just so perl-y.
# it also uses a nice 0(1) space algorithm instead of loading everything into
# memory and then choosing a line.  try 'ls | rl' to see this script in action.

while(<>){if(!int rand(++$n)){$l=$_}};print $l;
