#!/usr/bin/perl

use strict;
use warnings;
use CGI ":standard";
use DBI;
use lib "/var/www/pod.enyalios.net/lib";
use Pod;

my $dbh = db_connect();
my $user = get_user($dbh);
my $action = param("action") || "";
my $channel = param("channel") || "";

if($action eq "add") {
    $dbh->do("INSERT OR IGNORE INTO subscribe VALUES (?, ?)", {}, $user, $channel);
} elsif($action eq "rem") {
    $dbh->do("DELETE FROM subscribe WHERE user_id = ? AND channel_id = ?", {}, $user, $channel);
}

my $sql = "
SELECT
    channel.id,
    channel.title,
    channel.rss,
    channel.link,
    channel.summary,
    subscribe.user_id as subscribed
FROM
    channel
LEFT JOIN
    subscribe
ON
    channel.id = subscribe.channel_id
    AND subscribe.user_id = ?
ORDER BY channel.title";
my @channels = @{$dbh->selectall_arrayref($sql, {Slice => {}}, $user)};
print pod_header(), br,
"<div id=\"addchannel2\">", "<a class=\"close\" href=\"javascript:toggle_add_channel()\"><i class=\"fa fa-times-circle fa-lg\"></i></a>",
start_form(-method => "POST", -action => "update.cgi"),
"RSS URL: ", textfield("rss"), " ", submit("Add"),
end_form, "</div>",
"<table><tr><td>Subscribed</td><td>",
"<div id=\"addchannel1\"><a href=\"javascript:toggle_add_channel()\"><i class=\"fa fa-plus-circle fa-lg\"></i> Add a New Channel</a></div>",
"</td></tr>\n";
for(@channels) {
    my $sub = defined $_->{subscribed};
    print "  <tr>\n";
    print "    <td><div id=\"sub$_->{id}\"><a href=\"javascript:subscribe($_->{id},", $sub?0:1, ")\"><i class=\"subbox fa fa-3x fa-", $sub?"check-":"", "square-o\"></i></a></div></td>\n";
    print "    <td><h3><a href=\"$_->{link}\">$_->{title}</a> <a href=\"$_->{rss}\"><i class=\"fa fa-rss-square\"></i></a></h3>\n$_->{summary}\n";
    print "  </tr>\n";
}
print "</table>", end_html;
