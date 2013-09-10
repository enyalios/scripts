#!/usr/bin/perl

# this is meant to be run as a cgi script via apache and acts a simple webmail
# interface.  it is kept very simple and small in order to be checked from a
# mobile phone.  beware however, as this has no security features whatsoever so
# security must be build into either apache or the wap proxy for your phone.
# right now is only supports reading mail from a maildir, but that could easily
# be extended to other formats.

use strict;
use warnings;
use Date::Parse; # from dev-perl/TimeDate
use POSIX qw(strftime ceil);
use CGI;
use Data::Dumper;
use Email::MIME; # needs Email-MIME
use Net::Domain qw(hostfqdn hostname);

my $q = new CGI;
my $path = $q->param('path') || "";
my $action = $q->param('action') || "";
my $skip = $q->param('skip') || 0;
my $messages_per_page = 50;
my $access_keys = 0;
my $maildir_root = "/var/www/enyalios.net/htdocs/mail/maildir";
my $header_cache = "/var/www/enyalios.net/htdocs/mail/header_cache";
my $real_path = "$maildir_root/$path";
die if $real_path =~ m!(^|/)\.\.(/|$)!;
(my $url = $0) =~ s/.*\///;
my $now = strftime "%s", localtime;

sub print_header {
    my $redir = "";
    $redir = "Location: $_[0]" if $_[0];
    print <<EOF;
Content-Type: text/html
Cache-Control: no-cache
Pragma: no-cache
Expires: 0
$redir

<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN" "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">
<html><head><title>email</title>
<meta name="viewport" content="width=device-width; initial-scale=1.0; user-scalable=0;">
<style>
    body        { color: #000000; 
                  margin: 0;
                  background-color: #fff; }
    .even       { background-color: #ffc; }
    .odd        { background-color: #fff; }
    .nowrap     { white-space: nowrap; }
    .directory  { background-color: #aaf; }
    .header     { background-color: #aaf; }
    .new        { font-weight: bold; }
    .hdrtitle   { font-weight: bold; 
                  padding: 5px; }
    a           { color: #2000a0; 
                  text-decoration: none; }
    .action     { font-size: 70%;
                  background-color: #a7f; 
                  padding: 1px 5px; }
    .pages      { font-size: 70%;
                  background-color: #a7f;
                  padding: 1px 5px; }
    .submit     { background: #ccf;
                  width: 100px; }
    .mailboxes  { width: 100%;
                  border-collapse: collapse; 
                  margin: 2px; }
    .underline  { border-bottom: 1px solid #999; padding: 2px 5px; }
    .doubleline { border-bottom: 1px solid #000;
                  border-top: 1px solid #000; }
    .body       { font-family: monospace;
                  padding: 15px 5px; }
    .topmenu    { padding: 5px; }
    .mailbox    { padding: 2px 10px; }
    .mailboxnum { padding: 2px 10px;
                  width: 0px; }
</style>
</head>
<body>

EOF

    print "<div class=\"topmenu\">", $access_keys?"0. ":"",
          "<a href=\"$url\" accesskey=\"0\">Mailboxes</a>",
          " - <a href=\"$url?action=compose\">Compose</a></div>\n";
}

if($action eq "compose") { # compose an email
    my ($to, $subject, $body, $in_reply_to, $references);
    $to = $subject = $body = $in_reply_to = $references = "";
    if($path) { # if path is set then we are replying to an email
        my $email = read_email($path);
        $to = $email->{reply_to} || $email->{raw_from};
        $to .= ", $email->{cc}" if $email->{cc};
        $subject = $email->{subject};
        $subject =~ s/^(Re: *)*/Re: /;
        $references = "$email->{references} $email->{message_id}";
        $in_reply_to = $email->{message_id};
        
        $body = wrap_text(70, $email->{body});
        $body =~ s/^/> /gm;
        $body = "\n\nOn " . strftime("%a, %b %d, %Y at %T %z", localtime($email->{epoch}))
            . ", $email->{from} wrote:\n\n$body";
        # strip off lots of replies to replies and such
        $body =~ s/^(>\s*)+(From: |On.*wrote:|---- Original message ----|-{4,} Forwarded message -{4,}|--- .* wrote:|Forwarded conversation|.* said the following on)[\w\W]*//m;
        for($to, $subject, $references, $in_reply_to, $path, $body)
            { next unless $_; s/&/&amp;/g; s/</&lt;/g; s/>/&gt;/g; s/"/&quot;/g; }
    }
    print_header();
    print "<form action=\"$url\" method=\"post\">\n";
    print "<table>\n";
    print "<tr><td>From: </td><td><input type=\"text\" name=\"from\"    value=\"enyalios\@gmail.com\" /></td></tr>\n";
    print "<tr><td>To:   </td><td><input type=\"text\" name=\"to\"      value=\"$to\"                 /></td></tr>\n";
    print "<tr><td>Subj: </td><td><input type=\"text\" name=\"subject\" value=\"$subject\"            /></td></tr>\n";
    print "</table>\n<textarea name=\"body\" rows=\"8\" cols=\"80\"> \n\n-paul$body</textarea><br>\n";
    print "<input type=\"hidden\" name=\"action\"      value=\"send\"         />\n";
    print "<input type=\"hidden\" name=\"references\"  value=\"$references\"  />\n";
    print "<input type=\"hidden\" name=\"in_reply_to\" value=\"$in_reply_to\" />\n";
    print "<input type=\"hidden\" name=\"path\"        value=\"$path\"        />\n";
    print "<input class=\"submit\" type=\"submit\" value=\"",$access_keys?"9. ":"","Send\" accesskey=\"9\" /></form>\n";
} elsif($action) { # perform an action on a message
    my $redir_path = $path;
    $redir_path =~ s/^(.*\/).*$/$url?path=$1/;
    $redir_path = $url unless $redir_path;
    print_header($redir_path);
    if($action eq "delete") {
        die if -l $real_path;
        die unless -f _;
        unlink $real_path;
        print "Deleting '$path'.<br>\n<br>\n";
        print "<a href=\"$redir_path\">click here</a> if you are not redirected automatically\n";
    } elsif($action eq "markread") {
        die if -l $real_path;
        die unless -f _;
        my $new_path = add_maildir_flags($real_path, "S");
        $new_path =~ s!/new/!/cur/!;
        print "\nrename $path, $new_path\n";
        rename $real_path, $new_path;
        print "Marking '$path' as read.<br>\n<br>\n";
        print "<a href=\"$redir_path\">click here</a> if you are not redirected automatically\n";
    } elsif($action eq "marknew") {
        die if -l $real_path;
        die unless -f _;
        my $new_path = remove_maildir_flags($real_path, "S");
        $new_path =~ s!/cur/!/new/!;
        rename $real_path, $new_path;
        print "Marking '$path' as new.<br>\n<br>\n";
        print "<a href=\"$redir_path\">click here</a> if you are not redirected automatically\n";
    } elsif($action eq "send") { # send an email
        my $email;
        $email .= "Date: "        . strftime("%a, %d %b %Y %T %z", localtime $now) . "\n";
        $email .= "From: "        . $q->param('from')        . "\n";
        $email .= "To: "          . $q->param('to')          . "\n";
        $email .= "Subject: "     . $q->param('subject')     . "\n";
        $email .= "Message-ID: "  . generate_message_id()    . "\n";
        $email .= "References: "  . $q->param('references')  . "\n" if $q->param('references');
        $email .= "In-Reply-To: " . $q->param('in_reply_to') . "\n" if $q->param('in_reply_to');
        $email .= "User-Agent: Perl script I hacked together so that I could\n";
        $email .= "\t send and receive email on my crappy phone\n";
        $email .= "\n" . $q->param('body') . "\n";

        my $new_file = generate_new_filename();
        open(FILE, ">", $new_file) or die "Could not open '$new_file': $!\n";
        print FILE $email;
        close FILE;

        open(SENDMAIL, "|-", "/usr/sbin/sendmail -i -t") or die "Could not open sendmail\n";
        print SENDMAIL $email;
        close SENDMAIL;

        print "Email sent.<br>\n<br>\n";
        print "<a href=\"$redir_path\">click here</a> if you are not redirected automatically\n";
    } else {
        print "Invalid action '$action'.<br>\n<br>\n";
        print "<a href=\"$redir_path\">click here</a> if you are not redirected automatically\n";
    }
} elsif($path =~ /\/$/) { # generate a list of emails in a mailbox
    my ($cache_file, %files, %emails);
    print_header();

    # make a hash of all the email file names
    @files{read_maildir($path)} = ();
    ($cache_file = $path) =~ y/\//_/;
    %emails = load_cache($cache_file);
    # remove stale entries from the %emails hash
    for(keys %emails) { delete $emails{$_} unless exists $files{$_} }
    # add new entries to the %emails hash
    for(keys %files) { $emails{$_} = read_email_headers($path . $_) unless $emails{$_} }
    write_cache($cache_file, \%emails);

    # write out the header with the directory info
    my $other_path = $path;
    my $new = 1 if $path =~ m!/new/$!;
    $other_path =~ s/\/new\/$/\/cur\// or $other_path =~ s/\/cur\/$/\/new\//;
    my $short_path = $path;
    $short_path =~ s/\/$//;
    $short_path =~ s!^\/!inbox/!;
    print "<div class=\"directory doubleline\"><table width=\"100%\"><tr><td>$short_path(",
          scalar keys %emails,  ")</td><td align=\"right\">",$access_keys?"9. ":"","<a href=\"$url?path=",
          "$other_path\" accesskey=\"9\">View ", $new?"old":"new", "</a></td></tr>",
          "</table>\n";

    print generate_pages_header(scalar keys %emails), "</div>\n";

    my $line_num = 1; # this is used for the accesskey links
    my $count = 0; # this is used to determine with emails go on which page
    for(sort { $b->{epoch} <=> $a->{epoch} } values %emails) {
        # skip the email if its not on the right page
        $count++;
        if(($count <= $skip) || ($count > $skip + $messages_per_page)) {
            next;
        }
        print "<div class=\"underline ", $line_num%2?"odd":"even", 
                  "\" onclick=\"window.location='$url?path=$_->{path}'\">\n",
                  "<table width=\"100%\"><tr>",
                  "<td>$_->{from}</td>\n", 
                  "<td align=\"right\">", format_date_nicely($_->{epoch}), "</td>",
              "</tr></table>\n",
              "<span class=\"nowrap\">",
                  ($access_keys && $line_num < 9)?"$line_num. ":"", "<a href=\"$url?path=$_->{path}\"",
                  ($line_num < 9)?" accesskey=\"$line_num\"":"", ">", 
                  $_->{subject} ? $_->{subject} : "(no subject)", "</a>",
              "</span></div>\n\n";
        $line_num++;
    }
    print "<br><br><center>No ", $new?"new":"old", " emails</center>" unless %emails;
} elsif($path) { # display the contents of an email
    print_header();
    my $email = read_email($path);
    for(values %{$email}) { next unless $_; s/&/&amp;/g; s/</&lt;/g; s/>/&gt;/g; }
    print "<div class=\"header doubleline\">";
    print "<span class=\"hdrtitle\">From:</span> $email->{raw_from}<br>\n";
    print "<span class=\"hdrtitle\">To:</span> $email->{to}<br>\n";
    print "<span class=\"hdrtitle\">Cc:</span> $email->{cc}<br>\n" if $email->{cc};
    print "<span class=\"hdrtitle\">Subject:</span> $email->{subject}<br>\n";
    print "<span class=\"hdrtitle\">Date:</span> ";
    print strftime("%a, %d %B %Y %T", localtime $email->{epoch}), "\n";
    if($path =~ m!/new/!) {
        print "<div class=\"action\">",$access_keys?"1. ":"","<a href=\"$url?path=$path&action=markread\" accesskey=\"1\">Mark as Read</a>\n";
    } else {
        print "<div class=\"action\">",$access_keys?"1. ":"","<a href=\"$url?path=$path&action=marknew\" accesskey=\"1\">Mark as New</a>\n";
    }
    print " - ",$access_keys?"2. ":"","<a href=\"$url?path=$path&action=compose\" accesskey=\"2\">Reply</a>\n";
    print " - ",$access_keys?"9. ":"","<a href=\"$url?path=$path&action=delete\" accesskey=\"9\">Delete</a></div>\n";
    print "</div>\n";
    for($email->{body}) { 
        s/(?<= ) /&nbsp;/g; s/\t/\&nbsp;\&nbsp;\&nbsp;\&nbsp;/g; s/\n/<br\/>\n/g; 
        print "<div class=\"body\">$_</div>\n";
    }
    # print "<pre>$email->{body}</pre>\n";
} else { # generate a list of mailboxes
    print_header();
    my @maildirs;

    sub recurse {
        (my $dir = $_[0]) =~ s!^/!!;
        push @maildirs, $dir;
        opendir DIR, "$maildir_root/$dir" or die "could not open dir '$dir': $!\n";
        my @files = sort grep { !/^\.\.?$/ && -d "$maildir_root/$dir/$_" } readdir DIR;
        closedir DIR;
        for(@files) { recurse("$dir/$_") unless /^(new|tmp|cur)$/ }
    }
    recurse("");

    my $line_num = 1;
    print "<table class=\"mailboxes\">\n";
    for my $dir(@maildirs) {
        my $new_num = read_maildir("$dir/new");
        my $old_num = read_maildir("$dir/cur") + $new_num;
        (my $short_dir = $dir) =~ s!^$!inbox!;
        if($new_num) { $dir .= "/new" } else { $dir .= "/cur" }
        print "<tr class=\"", $line_num%2?"odd":"even", "\">",
              $access_keys?"<td class=\"mailboxnum\">$line_num.</td>":"",
              "<td class=\"mailbox ", ($new_num)?"new":"", "\">",
              "<a href=\"$url?path=$dir/\" accesskey=\"", $line_num++, "\">$short_dir</a>",
              "</td>",
              "<td align=\"right\" class=\"mailbox ", ($new_num)?"new":"", "\">", $new_num?"$new_num/":"", "$old_num",
              "</td></tr>\n";
    }
    print "</table>\n";
}

print "</body></html>\n";

sub read_maildir {
    my $dir = $maildir_root . "/" . $_[0];
    opendir DIR, $dir or die "Cannot open directory '$dir': $!\n";
    my @files = grep { !/^\./ } readdir(DIR);
    closedir DIR;
    @files
}

sub read_email {
    undef $/;
    my $short_path = $_[0];
    my $file_path = $maildir_root . "/" . $short_path;
    my ($from, $raw_from, $epoch, $subject, $date);

    open EMAIL, "<$file_path" or die "Cannot open file '$file_path': $!\n";
    my $email = Email::MIME->new(<EMAIL>);
    close EMAIL;

    $epoch = str2time $email->header('date');

    # oof, we cant find a real date in the date field.
    # fall back to the time we received the email.
    if(!$epoch || $now - $epoch < 0) {
        $epoch = $email->header('received');
        $epoch =~ s/^.*?; (\w{3}, +\d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2}.*)$/$1/;
        $epoch = str2time $epoch;
    }
    $epoch ||= 0;

    $from = $email->header('from') || "???";
    $raw_from = $from;
    $from =~ s/^ *(?:"?(.+?)"? *<.+>|<?(.+?)>?)$/$+/i;
    $from =~ s/\n//g;

    $subject = $email->header('subject') || "";
    $subject =~ s/\n//g;
    $subject =~ s/\t+/ /g;

    my $body = recparse($email);

    { to         => scalar $email->header('to'),       epoch    => $epoch,    from  => $from,
      cc         => scalar $email->header('cc'),       subject  => $subject,  path  => $short_path,
      reply_to   => scalar $email->header('reply-to'), raw_from => $raw_from, body  => $body, 
      references => scalar $email->header('references'), 
      message_id => scalar $email->header('message-id') };
}

sub read_email_headers {
    my $data = read_email($_[0]);
    return { epoch   => $data->{epoch},   from => $data->{from}, 
             subject => $data->{subject}, path => $data->{path} };
}

sub recparse {
    my $email = $_[0];
    my $body = "";

    if(!defined $email->content_type) {
        $body .= $email->body;
    } elsif($email->content_type =~ /^multipart\/(mixed|signed|digest|report|related)\b/) {
        $body .= recparse($_) for $email->parts;
    } elsif($email->content_type =~ /^multipart\/alternative\b/) {
        $body .= recparse(($email->parts)[0]);
    } elsif($email->content_type =~ /^text\/plain\b/) {
        $body .= $email->body;
    } else {
        #} elsif($email->content_type =~ /^(application|image)\//) {
        my $name = $email->filename || $email->invent_filename || "unknown";
        my $type = $email->content_type;
        $type =~ s/;.*$//;
        my $size = format_size(length($email->body));
        $body .= "[-- Attachment: $name --]\n";
        $body .= "[-- Type: $type, Size: $size --]\n\n";
    }

    return $body;
}

sub generate_pages_header {
    my $num_emails = $_[0];
    my $retval = "";
    my $current_page = $skip/$messages_per_page + 1;
    my $max_page = ceil($num_emails / $messages_per_page);
    my $prev_page = ""; my $next_page = "";

    if($current_page > 1)
        { $prev_page = "<a href=\"$url?path=$path&skip=" . 
            ($skip - $messages_per_page) . "\" accesskey=\"*\">&lt;</a>"; }
    if($current_page < $max_page)
        { $next_page = "<a href=\"$url?path=$path&skip=" . 
            ($skip + $messages_per_page) . "\" accesskey=\"\#\">&gt;</a>"; }
    $retval = "<center><div class=\"pages\">\n$prev_page\nPage $current_page/$max_page\n$next_page\n</div></center>\n" if $max_page > 1;

    $retval;
}

sub load_cache {
    my $cache_file = $header_cache . "/" . $_[0];
    -e $cache_file ? %{do $cache_file} : ();
}

sub write_cache {
    my $cache_file = $header_cache . "/" . $_[0];
    my $data = $_[1];
    open CACHE, ">$cache_file"
        or die "could not open '$cache_file' for writing: $!\n";
    print CACHE Dumper $data;
    close CACHE;
}

sub format_date_nicely {
    my $epoch = $_[0];
    my $date;

    if(($now - $epoch) < 60*60) {
        my $amount = ($now - $epoch) / 60;
        $date = sprintf "%d min%s ago", $amount, $amount>=2?"s":"";
    } elsif(($now - $epoch) < 60*60*24) {
        my $amount = ($now - $epoch) / 60 / 60;
        $date = sprintf "%d hr%s ago", $amount, $amount>=2?"s":"";
    } elsif(($now - $epoch) < 60*60*24*7) {
        my $amount = ($now - $epoch) / 60 / 60 / 24;
        $date = sprintf "%d day%s ago", $amount, $amount>=2?"s":"";
    } elsif((localtime($now))[5] == (localtime($epoch))[5]) {
        my $day = (localtime($epoch))[3];
        my $suffix;
        if($day == 11 || $day == 12 || $day == 13) {
            $suffix = "th";
        } elsif($day % 10 == 1) {
            $suffix = "st";
        } elsif($day % 10 == 2) {
            $suffix = "nd";
        } elsif($day % 10 == 3) {
            $suffix = "rd";
        } else {
            $suffix = "th";
        }
        $date = strftime("%B %e", localtime $epoch) . $suffix;
    } else {
        $date = strftime "%b %e, %Y", localtime $epoch;
    }

    $date;
}

sub add_maildir_flags { 
    my $path = $_[0];
    my $new_flags = $_[1];
    my $old_flags = "";
    my %flags;

    $old_flags = $1 if $path =~ s/:2,([a-z]+)$//i;
    @flags{ split "", $new_flags . $old_flags } = ();
    $path . ":2," . join("", sort keys %flags);
}

sub remove_maildir_flags {
    my $path = $_[0];
    my $bad_flags = $_[1];
    my $old_flags = "";
    my %flags;

    $old_flags = $1 if $path =~ s/:2,([a-z]+)$//i;
    @flags{split "", $old_flags} = ();

    delete $flags{$_} for split("", $bad_flags);
    if(%flags) { $path .= ":2," . join("", sort keys %flags) }
    $path;
}

sub format_size {
    my @exponents = split //, "bKMGTPEZY";
    my $number = shift;

    for my $power (reverse 0..@exponents) {
        my $nice_num = $number/(1024**$power);
        if ($nice_num > .97 || $power == 0) {
            return sprintf("%d%s", $nice_num, $exponents[$power]);
        } 
    }
}

sub generate_message_id {
    "<$now." . sprintf("%04d", rand 9999) . ".$$.$url\@" . hostfqdn() . ">";
}

sub wrap_text {
    my ($width, $text) = @_;
    my $width_plus_one = $width + 1;
    no warnings 'uninitialized';

    # this line wraps lines to $width characters, splitting on whitespace when possible
    1 while $text =~ s/^(?=.{$width_plus_one})(?:(.{1,$width}) +(.*)|(.{$width})(.+))/$1$3\n$2$4/m;
    $text;
}

sub generate_new_filename {
    sprintf "%s/sent/cur/%d.%d_%d.%s:2,S", $maildir_root, $now, $$, rand 99, hostname();
}

=for comment

TODO:

- add the 'R' flag when you reply to messages
- wrap the headers to a sane width on outgoing messages
- wrap your email text on outgoing messages
- handle parsing email bodies so that it returns an array of text and attachments
- get rid of all the warnings we dump into apache's error_log
- handle errors when we cant open files and such
- add comments
- combine /new and /cur caches
