#!/usr/bin/perl

use strict;
use warnings;
use CGI qw"request_method param";
use DBI;
use lib "/var/www/pod.enyalios.net/lib";
use Pod;

my $dbh = db_connect();
my $user = get_user($dbh);
my $channel = param("channel") || "";
my $episode = param("episode") || "";
my $time = param("time") || "";
my $length = param("length") || "";
my $toggle = param("toggle") || "";
my $action = param("action") || "";

print "Content-Type: text/html\n\n";
unless(request_method() eq "POST") {
    print "I only do work on POST.\n";
    exit;
}

if($action eq "sub") {
    if($toggle) {
        $dbh->do("INSERT OR IGNORE INTO subscribe VALUES (?, ?)", {}, $user, $channel);
        print "<a href=\"javascript:subscribe($channel,0)\"><i class=\"subbox fa fa-3x fa-check-square-o\"></i></a>"
    } else {
        $dbh->do("DELETE FROM subscribe WHERE user_id = ? AND channel_id = ?", {}, $user, $channel);
        print "<a href=\"javascript:subscribe($channel,1)\"><i class=\"subbox fa fa-3x fa-square-o\"></i></a>";
    }
    exit;
}

$dbh->do("INSERT OR IGNORE INTO state (user_id, channel_id, episode_id, resume, watched) VALUES (?, ?, ?, 0, 0)", {}, $user, $channel, $episode);
if($toggle) {
    $dbh->do("UPDATE state SET watched = (watched+1)%2 where user_id = ? AND channel_id = ? AND episode_id = ?", {}, $user, $channel, $episode);
    my $watched = $dbh->selectcol_arrayref("SELECT watched FROM state WHERE channel_id = ? AND episode_id = ?", {}, $channel, $episode);
    print $watched->[0]?"<i class=\"fa fa-lg fa-eye\"></i> Mark Unwatched":"<i class=\"fa fa-lg fa-eye-slash\"></i> Mark as Watched";
} else {
    $dbh->do("UPDATE state SET resume = ? WHERE channel_id = ? AND episode_id = ?", {}, $time-2, $channel, $episode);
    $dbh->do("UPDATE state SET watched = 1 WHERE channel_id = ? AND episode_id = ?", {}, $channel, $episode) if($length - $time < 30);
}
