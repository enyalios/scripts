#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/param/;

my $query = param("query");
my $data_dir = "/var/www/enyalios.net/data/";
my @hints;
my $results = 0;
print "Content-Type: text/html\n\n";

my %file = ( "p"  => "oracle",
             "c"  => "oracle",
             "cg" => "oracle",
             "m"  => "movies.list",
             "n"  => "movies.list",
             "pl" => "perl.list",
             "t"  => "tv.list" );

if($query =~ /^(p|c|cg|m|n|t|pl) (.+)/i) { # complete magic cards, movie titles, and tv shows
    my ($prefix, $search) = ($1, $2);
    $prefix =~ y/A-Z/a-z/;
    exit unless length $search > 2;
    open FILE, "<$data_dir/$file{$prefix}" or die;
    while(<FILE>) { push @hints, "$prefix $1" if /^(\Q$search\E.*)/i; }
    seek FILE, 0, 0;
    while(<FILE>) { push @hints, "$prefix $1" if /^(.+\Q$search\E.*)/i; }
} elsif($query =~ /^(w) (.+)/i) { # complete wikipedia articles
    my ($prefix, $search) = ($1, $2);
    $prefix =~ y/A-Z/a-z/;
    exit unless length $search > 2;
    my $file = $search;
    for($file) { s/^(..).*/$1/; y/A-Z/a-z/; y/a-z0-9/_/c; s/^(.)$/$1_/; }
    open FILE, "<$data_dir/wiki/$file" or die;
    while(<FILE>) { push @hints, "$prefix $1" if /^(\Q$search\E.*)/i; }
} else { # fall back to just completing on dictionary words
    $query =~ (/^(.* )?(.*)/i);
    my ($prefix, $search) = ($1, $2);
    exit unless length $query > 2;
    open FILE, "<$data_dir/words" or die;
    while(<FILE>) { push @hints, "$prefix$1" if /^(\Q$search\E.*)/i; }
}

for(@hints) { 
    last if $results++ >= 20;
    chomp;
    print "<div class=\"hint\"><a href=\"javascript:go('$_')\" class=\"hint\">$_</a></div>\n";
}
print scalar @hints, " results found<br/>\n" if @hints > 20;
