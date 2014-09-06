#!/usr/bin/perl

use strict;
use warnings;
use CGI ":standard";
use DBI;
use lib "/var/www/pod.enyalios.net/lib";
use Pod;

my $dbh = db_connect();
my $user = get_user($dbh);
my $channel = param("channel") || "";
my $episode = param("episode") || "";

unless($channel && $episode) {
    print "Content-Type: text/html\n\nmissing channel or episode\n";
    exit;
}

my $sql = <<EOF;
SELECT
    channel.title AS channel,
    channel.id AS channel_id,
    episode.id AS episode_id,
    episode.title,
    episode.link,
    episode.summary,
    episode.date,
    episode.file,
    episode.length,
    state.resume,
    state.watched
FROM
    episode
JOIN channel
    ON channel.id = episode.channel_id
    AND channel.id = ?
    AND episode.id = ?
LEFT JOIN state
    ON state.channel_id = channel.id
    AND state.episode_id = episode.id
    AND state.user_id = ?
EOF
my %episode = %{$dbh->selectrow_hashref($sql, {}, $channel, $episode, $user)};
my $length = format_length($episode{length});
my $date = scalar localtime($episode{date});
my $watched = $episode{watched}?"<i class=\"fa fa-lg fa-eye\"></i> Mark Unwatched":"<i class=\"fa fa-lg fa-eye-slash\"></i> Mark as Watched";
$episode{resume} = 0 unless $episode{resume};
my $resumeplay = $episode{resume}?"resume":"play";
my $resume = $episode{resume}?" You have watched " . format_length($episode{resume}) . ".":"";
print pod_header();
print <<EOF;
    <br />
    <script>setInterval("save_time($episode{channel_id}, $episode{episode_id}, $episode{length})", 5000);</script>
    <div class="channel">$episode{channel}</div>
    <div class="title">$episode{title}</div>
    <div class="date">$date</div>
    <div class="main">
        <div class="summary">$episode{summary}</div>
        <!-- <a href="$episode{link}">Read More...</a> --><br />
        <audio id="pod" class="pod" controls>
            <source src="$episode{file}" type="audio/mpeg">
            Your browser does not support the audio tag.
        </audio> 
        <br /><br />
        <div class="length">Episode is $length long.$resume</div>
        <p class="seekbar">
            <a class="seek left-seek" href="javascript:seek(-60)"><i class="fa fa-fast-backward"></i> 1m</a><a class="seek" href="javascript:seek(-10)"><i class="fa fa-backward"></i> 10s</a><a class="seek" href="javascript:resume($episode{resume})"><i class="fa fa-play"> $resumeplay</i></a><a class="seek" href="javascript:seek(10)">10s <i class="fa fa-forward"></i></a><a class="seek right-seek" href="javascript:seek(60)">1m <i class="fa fa-fast-forward"></i></a>
        </p>
        <a href="javascript:toggle_watched($episode{channel_id}, $episode{episode_id})"><div class="toggle" id="toggle">$watched</div></a><br />
    </div>
    <div id="status"></div>
</body>
</html>
EOF
