#!/usr/bin/perl

use strict;
use warnings;
use DBI;
require LWP::Simple;
use XML::Simple;
use Date::Parse;
use Encode;
use CGI ":standard";
use lib "/var/www/pod.enyalios.net/lib";
use HTML::TagFilter;
use Pod;

my $quiet = 0;
$quiet = 1 if defined $ARGV[0] && $ARGV[0] eq "-q";
$| = 1;
my $dbh = db_connect();
my $cgi = $< != 1000;
my $user = get_user($dbh) if $cgi;
my $insert_episode = $dbh->prepare("INSERT INTO episode VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)");
my $get_episodes = $dbh->prepare("SELECT title FROM episode WHERE channel_id = ?");
my $update_channel = $dbh->prepare("UPDATE channel SET link = ?, summary = ?, title = ? WHERE id = ?");
my $tf = new HTML::TagFilter;
$tf->clear_rules();
$tf->allow_tags({ a => { href => [] }, img => {src => [], height => [], width => []} });

print pod_header(), "<h3 id=\"status\">Loading episode data.  Please wait...</h3><pre>" if $cgi;

my @channels;
my $rss = param("rss") || "";
if($rss) {
    $dbh->do("INSERT OR IGNORE INTO channel (id, rss) VALUES (NULL, ?)", {}, $rss);
    @channels = @{$dbh->selectall_arrayref("SELECT id, rss FROM channel WHERE rss = ?", {Slice => {}}, $rss)};
    $dbh->do("INSERT OR IGNORE INTO subscribe VALUES (?, ?)", {}, $user, $channels[0]->{id});
} else {
    @channels = @{$dbh->selectall_arrayref("SELECT id, rss FROM channel", {Slice => {}})};
}

for my $channel (@channels) {
    my $tree = XMLin LWP::Simple::get($channel->{rss});
    unless($tree) {
        print "couldnt load $channel->{rss}\n";
        next;
    }
    my %episodes = map { $_, 1} @{$dbh->selectcol_arrayref($get_episodes, {}, $channel->{id})};

    print "Found ", scalar @{$tree->{channel}->{item}}, " episodes of $tree->{channel}->{title}\n" unless $quiet;
    $update_channel->execute(&clean($tree->{channel}->{link}),
        &clean($tree->{channel}->{description}),
        &clean($tree->{channel}->{title}),
        $channel->{id});

    for(@{$tree->{channel}->{item}}) {
        my $title = &clean($_->{title});
        next if $episodes{$title};
        next unless $_->{enclosure}->{url};
        my $length = 0;
        if($_->{"itunes:duration"} && $_->{"itunes:duration"} =~ /^(?:(\d+):)?(\d+):(\d+)$/) {
            $length += $1*3600 if defined $1;
            $length = $length + $2*60 + $3;
        } else {
            $length = &get_length_from_url($_->{enclosure}->{url});
        }
        print "  Inserting $tree->{channel}->{title} - $title\n" unless $quiet;
        $insert_episode->execute($channel->{id},
            $title,
            &clean($_->{link})||"",
            &clean($_->{description}),
            str2time(&clean($_->{pubDate})),
            &clean($_->{enclosure}->{url}),
            $length);
    }
}
print "</pre><script>document.getElementById(\"status\").innerHTML = \"All Done.\";</script><a href=\"subscribe.cgi\">Go Back</a>", end_html if $cgi;

sub get_length_from_url {
    my $url = $_[0];
    open(MIDENTIFY, "-|", qw"mplayer -noconfig all -cache-min 0 -vo null -ao null -frames 0 -identify -msglevel all=0", $url) or die;
    my $output = join "", <MIDENTIFY>;
    my $length = $1 if $output =~ /^ID_LENGTH=(\d+)/m;
    return $length;
}

sub clean {
    # this is a helper function that changes crazy unicode quotes and such
    # to their ascii equivilent as well as stripping out all html other
    # than 'img' and 'a' tags
    my $string = $_[0];
    $string = Encode::encode("UTF-8", $string);
    $string =~ s/\xe2\x80\x99/'/g;
    $string =~ s/\xe2\x80\x93/-/g;
    $string =~ s/\xe2\x80\xa6/.../g;
    $string =~ s/\xe2\x80\x9c/"/g;
    $string =~ s/\xe2\x80\x9d/"/g;
    $string =~ s/\xc2\xa0/ /g;
    $string =~ s/\xc2\xae/(r)/g;
    $string = Encode::encode("ascii", $string);
    $string =~ s/^\s+//;
    $string =~ s/\s+$//;
    $string = $tf->filter($string);
    return $string;
}
