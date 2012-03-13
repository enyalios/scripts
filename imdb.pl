#!/usr/bin/perl

use strict;
use warnings;
use LWP::Simple;
use Getopt::Std;
use HTML::Entities;

sub getMovieList {
    my $_ = get "http://www.imdb.com/find?q=$_[0]";
    my ($number, $title, $year, $type);
    if(/<meta property="og:url" content="http:\/\/www.imdb.com\/title\/tt(\d+)\/" \/>/) {
        # this is a single movie page
        $number = $1;
        ($title, $year) = &get_title_and_year_from_page($_);
        print "$number:$title ($year)\n";
    } else {
        # this is a search results page
        s/[\s\S]*?^(.*?Displaying \d+ Results?)/$1/m;

        # figure out which sections were returned
        my ($popular_results, $exact_results, $partial_results);
        $popular_results = $exact_results = $partial_results = "";
        $popular_results = $1 if /<b>Popular Titles<\/b>(.*?)<\/table>/s;
        $exact_results = $1 if /<b>Titles \(Exact Matches\)<\/b>(.*?)<\/table>/s;
        $partial_results = $1 if /<b>Titles \(Partial Matches\)<\/b>(.*?)<\/table>/s;

        # use these two if the exist
        my $data = $popular_results . $exact_results;
        # otherwise fall back to partial results
        $data = $partial_results if $data eq "";
        for($data =~ /<tr>(.*?)<\/tr>/g) {
            next unless /<a href="\/title\/tt(\d+)\/.*\">(.+)<\/a> \((\d+)\/?[a-z]*\)(?: (?:<small>)?\((.+?)\))?/i;
            ($number, $title, $year, $type) = ($1, $2, $3, $4);
            decode_entities($title);
            $type = (defined $type)?" $type":"";
            print "$number:$title ($year)$type\n";
        }
    }
}

sub getMovieData {
    $_ = get "http://www.imdb.com/title/tt$_[0]/";

    my ($title, $year, $release, $director, $plot, $userrating, $movierating, $runtime, $writer, $cast, $genres, $countries);
    my $name_link_pat = qr'<a [^>]*href="/name/[^"]*"[^>]*>([^<]*)</a>'m;
    
    ($title, $year) = &get_title_and_year_from_page($_);

    $release = $1 if /Release Date:<\/h4>\s*<time itemprop="datePublished" datetime="(\d\d\d\d-\d\d-\d\d)">/;
    $director = join(",", ($1 =~ m/$name_link_pat/g)) if /Directors?:\s*<\/h4>(.*?)<\/div>/s;
    $plot = $1 if /<p itemprop="description">\s*(.*?)\s*<\/p>/;
    $userrating = $1 if /<span itemprop="ratingValue">([\d.]*)<\/span>/;
    $movierating = $1 if /<span itemprop="contentRating">(.*?)<\/span>/;
    $runtime = $1 if /<time itemprop="duration" datetime="[^"]*">(.*?) min<\/time>/;
    $writer = join(",", ($1 =~ m/$name_link_pat/g)) if /Writers?:\s*<\/h4>(.*?)<\/div>/s;
    $cast = join(",", ($1 =~ m/$name_link_pat/g)) if /<table class="cast_list">(.*?)<\/table>/s;
    $genres = join(",", ($1 =~ m/href="\/genre\/[^"]*"[^>]*>([^<]*)<\/a>/g)) if /Genres:\s*<\/h4>(.*?)<\/div>/s;
    $countries = join(",", ($1 =~ m/href="\/country\/[^"]*"[^>]*>([^<]*)<\/a>/g)) if /Country:\s*<\/h4>(.*?)<\/div>/s;

    no warnings 'uninitialized';
    print "Title:$title\n";
    print "Year:$year\n";
    print "ReleaseDate:$release\n";
    print "Director:$director\n";
    print "Plot:$plot\n";
    print "UserRating:$userrating\n";
    print "MovieRating:$movierating\n";
    print "Runtime:$runtime\n";
    print "Writers:$writer\n";
    print "Cast:$cast\n";
    print "Genres:$genres\n";
    print "Countries:$countries\n";
}

sub get_title_and_year_from_page {
    my ($title, $year);
    if($_[0] =~ /<title>(.*)<\/title>/) {
        $title = $1;
        $title =~ s/^(?:IMDb - )?(.*?)(?: - IMDb)?$/$1/;
        $year = $1 if $title =~ /^.*(.*?\d\d\d\d)/;
        $title =~ s/ \([^()]*\)$//;
        $title =~ s/&ndash;/-/g;
        decode_entities($title);
    }
    return $title, $year;
}

my %opts;
getopts('M:D:', \%opts);
if(defined $opts{M}) {
    &getMovieList($opts{M});
} elsif(defined $opts{D}) {
    &getMovieData($opts{D});
}
