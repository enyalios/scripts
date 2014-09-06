package Pod;
use strict;
use warnings;
use DBI;
use CGI ":standard";

use Exporter qw(import);

our @EXPORT = qw(db_connect get_user pod_header format_length);
our @EXPORT_OK = qw();

our $dbfile = "/var/www/pod.enyalios.net/db/pod.db";
our $dbh = DBI->connect("dbi:SQLite:dbname=$dbfile", "", "", { RaiseError => 1, AutoCommit => 1 }) or die;
our $user = 0;

sub db_connect {
    return $dbh;
}

sub get_user {
    my $dbh = $_[0];
    my $key = cookie('key') || "";
    my $user_id = $dbh->selectcol_arrayref("SELECT id FROM user WHERE key = ?", {}, $key);
    if(@{$user_id} == 1) {
        $user_id = $user_id->[0];
        $user = $user_id;
    } else {
        my $cookie = cookie(-name => "key", -value => "", -expires => "-1d");
        print header(-cookie => $cookie, -refresh => "0; url=login.cgi");
        exit;
    }
    return $user;
}

sub pod_header {
    my $row = $dbh->selectrow_arrayref("SELECT s.channel_id, s.episode_id, e.date FROM state as s, episode as e WHERE e.id = s.episode_id AND e.channel_id = s.channel_id AND s.user_id = ? AND s.watched = 0 ORDER BY e.date LIMIT 1", {}, $user);
    my $current = "";
    $current = "        <a href=\"listen.cgi?channel=$row->[0]&amp;episode=$row->[1]\"><i class=\"fa fa-play\"></i> Current</a> |\n" if $row;
    return header(-cache_control => "no-cache, no-store, must-revalidate"),
        start_html(-title => "Podcast",
                   -style => {-src => ["style.css", "//netdna.bootstrapcdn.com/font-awesome/4.0.3/css/font-awesome.css"]},
                   -meta => {viewport => "width=device-width,initial-scale=1"},
                   -script => {-src => "pod.js"}),
               "    <div class=\"navbar\">\n",
               "        <a href=\"/\"><i class=\"fa fa-bars\"></i> Home</a> |\n",
               $current,
               "        <a href=\"subscribe.cgi\"><i class=\"fa fa-wrench\"></i> Podcasts</a> |\n",
               "        <a href=\"login.cgi?logout=1\"><i class=\"fa fa-sign-out\"></i> Logout</a>\n",
               "    </div>\n",
               "    <br />\n";
}

sub format_length {
    my $length = $_[0];
    my $minutes = int($length / 60);
    my $seconds = $length % 60;
    $seconds = "0" . $seconds if $seconds < 10;
    return "$minutes:$seconds" if $minutes < 60;

    my $hours = int($minutes / 60);
    $minutes = $minutes % 60;
    $minutes = "0" . $minutes if $minutes < 10;
    return "$hours:$minutes:$seconds";
}

1;
