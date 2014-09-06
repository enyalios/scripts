#!/usr/bin/perl

use strict;
use warnings;
use DBI;
use lib "/var/www/pod.enyalios.net/lib";
use Pod;

my $dbh = db_connect();
my $user = get_user($dbh);

my $last = "";
my $sql = <<EOF;
SELECT 
    channel.title AS channel,
    episode.title,
    state.watched,
    state.resume,
    episode.length,
    channel.id AS channel_id,
    episode.id AS episode_id
FROM episode
JOIN channel 
    ON episode.channel_id = channel.id
JOIN subscribe
    ON subscribe.channel_id = channel.id
    AND subscribe.user_id = ?
LEFT JOIN state 
    ON state.episode_id = episode.id
    AND channel.id = state.channel_id
    AND state.user_id = ?
ORDER BY channel.title, date desc;
EOF
my @episodes = @{$dbh->selectall_arrayref($sql, { Slice => {} }, $user, $user)};
my %eps;
for(@episodes) {
    $eps{$_->{channel}}{unwatched}++ unless $_->{watched};
    $eps{$_->{channel}}{total}++;
}
my $i = 0;
print &pod_header();
for(@episodes) {
    if($_->{channel} ne $last) {
        $i++;
        print "</div>\n" unless $i == 1;
        print "<h2 class=\"header\" onclick=\"toggle_section('$i')\"><i id=\"arrow$i\" class=\"fa fa-fw fa-chevron-right\"></i> $_->{channel} (", $eps{$_->{channel}}{unwatched}, "/", $eps{$_->{channel}}{total}, ")</h2>\n<div id=\"section$i\" class=\"section\">\n";
    }
    $last = $_->{channel};
    my $class = "";
    $class = " class=\"watching\"" if defined $_->{resume} && $_->{resume} > 0;
    $class = " class=\"watched\"" if $_->{watched};
    printf "<a%s href=\"listen.cgi?channel=%s&amp;episode=%s\">%s</a> (%s)<br /><br />\n", 
    $class, $_->{channel_id}, $_->{episode_id}, $_->{title}, format_length($_->{length});
}
print "</div>\n";
print "<br />You do not seem to be subscribed to any channels.<br /><br />Perhaps you should <a href=\"subscribe.cgi\">add some</a>.\n" unless @episodes;
print "</body>\n</html>\n";
