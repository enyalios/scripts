#!/usr/bin/perl

# this script is designed to be run as a cgi script via apache and acts as a
# webinterface for mythvideo.  it displays a main listing page of all media, an
# info page for each video when clicked on, and also does the conversion of
# media to flv and streaming.

# in order for the web interface to work youll also need MFPlayer.swf and
# MFPlayer_styles.swf in the current directory.  they both come as part of the
# mythweb package.  im not really happy with them as an flv player, but i
# havent found any others that i like any better.

use warnings;
use strict;
use CGI;
use DBI;

my $q = new CGI;
my %vinfo;

sub bail { print $q->header(), @_; exit; }

my $f = $q->param('filename');
my $m = $q->param('method');

my $dbh = DBI->connect("DBI:mysql:database=mythconverg;host=delta",
    "mythtv", "mythtv", {'RaiseError' => 1}) or die "couldnt connect to db\n";
my $video_dir = $dbh->prepare("select data from settings where value = 'VideoStartupDir'");
$video_dir->execute();
$video_dir = $video_dir->fetchall_arrayref()->[0]->[0];

if(!defined $f) {
    my $sth = $dbh->prepare("SELECT filename FROM videometadata ORDER BY filename");
    $sth->execute();

    print $q->header();
    print $q->start_html(-title => "video listing", -style=>{-code=>generate_stylesheet()});
    while (my $ref = $sth->fetchrow_hashref()) {
        my $name = $ref->{filename};
        $name =~ s!^\Q$video_dir\E/?!!;
        print "<a href=\"videos.pl?method=info&filename=$name\">$name</a><br>\n";
    }
} else {

    bail("no filename")    unless $f;
    #bail("bad directory")  unless $f =~ m!^/mnt/videos/!;
    bail("bad extension")  unless $f =~ m/\.(avi|mkv|mpe?g|rm|asf|wmv|mov|mp4)$/i;
    bail("cant use '..'")  if $f =~ m!/\.\./!;
    bail("cant find file") unless -e "$video_dir/$f";

    if($m eq "stream") {
        print $q->header( -type => 'video/x-flv' );

        my $enc = $q->param("encoder") || "";
        if($enc eq "ffmpeg") {
            # ugly hack to get the aspect ratio close to right
            open(INFO, '-|', "/usr/bin/midentify", "$video_dir/$f");
            /^(\w+)=(.*)$/, $vinfo{$1} = $2 for(<INFO>);
            close INFO;

            my $height = int(480 * $vinfo{ID_VIDEO_HEIGHT} / $vinfo{ID_VIDEO_WIDTH} + 20);
            $height = int($height / 2) * 2; # must be a mult of 2

            # close stderr as this dumps a lot into the apache logs
            close STDERR;
            open(DATA, '-|', qw"/usr/bin/ffmpeg -y -i", "$video_dir/$f", "-s", "480x$height",
                qw"-r 20 -f flv -ac 2 -ar 11025 -ab 64k -b 300k /dev/stdout");
        } else {
            # right now this command loses audio sync on some files
            no warnings qw(qw); # turn off a false positive warning message
            close STDERR;
            open(DATA, '-|', "/usr/bin/mencoder", "$video_dir/$f", qw/-o - -ovc lavc -lavcopts/,
                qw/vcodec=flv:vbitrate=300 -vf pp=fd,scale=480:-2 -ofps 20 -oac/,
                qw/mp3lame -lameopts abr:br=64 -srate 11025 -of lavf -lavfopts/,
                qw/format=flv -really-quiet/);
        }

        while (read DATA, my $buffer, 262144) { print $buffer; }

    } elsif ($m eq "info") {
        print $q->header();

        my $sth = $dbh->prepare("
            SELECT rating, director, userrating, inetref, length, plot,
            title, coverfile, year FROM videometadata where filename = ?");
        $sth->execute("$video_dir/$f");
        my $ref = $sth->fetchrow_hashref();

        print $q->start_html(-title => $ref->{title}, -style=>{-code=>generate_stylesheet()}); 
        print "<div class=header1><div class=headertext>";
        print "<img src='mepo.png' style='float:right'>Video Information</div></div>\n";
        print "<div class=header2>&nbsp;</div>\n<div class=header3>&nbsp;</div>\n";
        print "<div class=body>\n";

        my $cover = $ref->{coverfile};
        # in order for this to work you'll need to make a symlink to your covers dir
        $cover =~ s!^/home/enyalios/.mythtv/MythVideo!covers!;
        print "<img src='$cover' width='300' class=cover>\n" unless $cover eq 'No Cover';
        print "<span class=title>", $ref->{title}, "</span><br><br>\n";
        print "<span class=director><span class=yellowish>Directed by:</span> ", $ref->{director}, "</span><br>\n";
        print $ref->{plot}, "<br><br><br>\n<span class=yellowish>", $ref->{rating}, "</span><br><br>\n";
        print "<table><tr><td><span class=yellowish>Runtime:</span></td><td>", $ref->{length}, " minutes</td></tr>";
        print "<tr><td><span class=yellowish>Year:</span></td><td>", $ref->{year}, "</td></tr>";
        print "<tr><td><span class=yellowish>User Rating:</span></td><td>", $ref->{userrating}, "</td></tr></table>";

        print "<br><a href='http://www.imdb.com/title/tt", $ref->{inetref}, 
            "/'>imdb</a><br>\n" if($ref->{inetref} >= 1000);

        open(INFO, '-|', "/usr/bin/midentify", "$video_dir/$f");
        /^(\w+)=(.*)$/, $vinfo{$1} = $2 for(<INFO>);
        close INFO;
        #for(sort keys %vinfo) { print "$_: $vinfo{$_}<br>\n"; }
        my $height = int(480 * $vinfo{ID_VIDEO_HEIGHT} / $vinfo{ID_VIDEO_WIDTH} + 20);
        my $time = int($vinfo{ID_LENGTH});

        print "<br>\n<a href=\"javascript:void(0)\" onclick=\"", 
        "javascript:window.open('MFPlayer.swf?totalTime=$time&width=480",
        "&height=$height&styles=MFPlayer_styles.swf&file=/videos/videos.pl/$f",
        "','videoplayer','width=480,height=$height')\">play using mencoder</a>";

        print "<br>\n<a href=\"javascript:void(0)\" onclick=\"", 
        "javascript:window.open('MFPlayer.swf?totalTime=$time&width=480",
        "&height=$height&styles=MFPlayer_styles.swf&file=/videos/videos.pl/ff/$f",
        "','videoplayer','width=480,height=$height')\">play using ffmpeg</a>";

        print "<div class=clearer></div></div><br>\n<div class=footer1>&nbsp</div>";
        print "<div class=footer2>&nbsp;</div>";
    } else {
        bail("method not recognized");
    }
}

sub generate_stylesheet {
    my $stylesheet = <<EOF;
*           { padding:0px; margin:0px; }
html,body   { margin: 20; font-size: 12pt;
              font-family: Arial, Helvetica, sans-serif;
              background-color: #203545; color: #ffffff; }
a, a:link   { color: #a0a0ff; text-decoration: none; }
a:active    { color: #990033; text-decoration: none; }
a:visited   { color: #a0a0ff; text-decoration: none; }
a:hover     { color: #f5e289; text-decoration: underline; }
img.cover   { padding-top: 10px; padding-right: 20px;
              padding-bottom: 10px; float: left; }
.title      { font-size: 22pt; color: #FFA70B; }
.body       { padding-left: 20px; padding-right: 20px; }
.director   { font-size: 14pt; }
.yellowish  { color: #f5e289; }
.header1    { background-color: #4090b0; height: 72px;
              vertical-align: bottom; }
.headertext { font-size: 48px; text-align: right;
              text-color: #ffffff; text-align: top;
              position: relative; padding-right: 0px;
              padding-top: 20px; }
.header2    { background-color: #ffffff; height: 2px; }
.header3    { }
.footer1    { background-color: #000000; }
.footer2    { background-color: #808080; height: 3px; }
div.clearer { clear: left; line-height: 0; height: 0; }
EOF
}
