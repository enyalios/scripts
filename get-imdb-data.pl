#!/usr/bin/perl

use strict;
use warnings;

sub uniq {
    my %seen;
    return grep { !$seen{$_}++ } @_;
}

# find the list of the 4000 most popular celebrities
my $count = 0;
my @celebs;
while($count < 40) {
    my $start = 100 * $count + 1;
    my $data = `wget -qO - 'https://www.imdb.com/search/name?gender=male,female&count=100&start=$start&ref_=rlm'`;
    $data =~ s/\n//g;
    push @celebs, $_ for $data =~ /<a href="\/name\/nm\d+"> ([^<]*?)<\/a>/g;
    $count++;
    sleep 1;
}

# get the input data from imdb
my @ratings = `wget -qO - https://datasets.imdbws.com/title.ratings.tsv.gz | gzip -cd`;
my @titles = `wget -qO - https://datasets.imdbws.com/title.basics.tsv.gz | gzip -cd`;
shift @ratings;
shift @titles;

# generate a sorted list of movies/shows with enough votes in their ratings
my @ids;
for(@ratings) {
    my @fields = split "\t", $_;
    push @ids, $fields[0] if $fields[2] > 1000;
}

# filter @titles by @ids and put matching movies into @movies
# and tv shows into in @tv
my (@movies, @tv);
for(@titles) {
    last unless @ids;
    my @fields = split "\t", $_;
    if($ids[0] eq $fields[0]) {
        push @movies, $fields[2] if $fields[1] =~ /^(movie|tvMovie|video)$/;
        push @tv, $fields[2] if $fields[1] =~ /^(tvSeries|tvMiniSeries)$/;
        shift @ids;
    }
}

open my $fh, ">", "imdb.list" or die;
print $fh "$_\n" for uniq sort @movies, @tv, @celebs;
close $fh or die;

open $fh, ">", "movies.list" or die;
print $fh "$_\n" for uniq sort @movies;
close $fh or die;

open $fh, ">", "tv.list" or die;
print $fh "$_\n" for uniq sort @tv;
close $fh or die;
