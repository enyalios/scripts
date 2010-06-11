#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
use LWP::UserAgent;

$| = 1;
my $progname = $0;
$progname =~ s!^.*/!!;
my $ua = LWP::UserAgent->new; 
sub post { $ua->post($_[0], $_[1])->{_content}; }
sub get { $ua->get($_[0])->{_content}; }

my $string = param('query');

print "Content-Type: text/html\n\n<html><head>\n<script language=\"JavaScript\" type=\"text/javascript\">\n";
print "<!--\nfunction setfocus() {\ndocument.prices.query.focus();\n}\n//-->\n</script>\n<body onload=\"setfocus()\">\n";
print "<form method=\"post\" name=\"myform\" action=\"http://cardshark.com/quick_search.asp\"><input type=\"hidden\" name=\"query\" value=\"$string\"></form>\n"; 
print "<h2>searching for '$string'</h2>\n";
print "<h3><a href=\"http://magictraders.com/cgi-bin/query.cgi?list=magic&target=$string&field=0&operator=re\">magictraders.com</a></h3>\n<pre>";

# print magictraders prices
open(FILE, "</var/www/enyalios.net/data/prices") or die "couldnt open prices file\n";
print grep /\Q$string\E/i, <FILE>;
close FILE;

print "</pre><h3><a href=\"javascript:void(0)\" onClick=\"document.myform.submit();return false\">cardshark.com</a></h3>\n<pre>";

# print cardshark prices
my $page = &post("http://cardshark.com/quick_search.asp", { 'query' => $string });
for($page =~ m!<A HREF="(/magic/card_detail\.asp\?card_id=\d+)"!ig) {
    $page = &get("http://cardshark.com$_");
    $page =~ m!</B>.*?<B>(.*?)</B>.*?</I>.*?<I>(.*?)</I>.*?Estimated Value: <B><font size="4" COLOR=".FF0000">(?:Unknown|\$(.*?))</FONT>!s;
    printf "%-30s %-30s %6s\n", $1, $2, $3?$3:"??";
}
print "</pre><br />\nSearch Again:<br />\n<form method=\"get\" name=\"prices\" action=\"$progname\"><input type=\"text\" name=\"query\" />\n";
print "</body></html>";
