#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
use LWP::UserAgent;

$| = 1;
my $progname = $0;
$progname =~ s!^.*/!!;
my $ua = LWP::UserAgent->new; 
#sub post { $ua->post($_[0], $_[1])->{_content}; }
sub get { $ua->get($_[0])->{_content}; }

my $string = param('query');
exit if $string eq "";

print "Content-Type: text/html\n\n<html><head>\n<script language=\"JavaScript\" type=\"text/javascript\">\n";
print "<!--\nfunction setfocus() {\ndocument.prices.query.focus();\n}\n//-->\n</script>\n<body onload=\"setfocus()\">\n";
print "<h2>searching for '$string'</h2>\n";
print "<h3><a href=\"http://magictraders.com/cgi-bin/query.cgi?list=magic&target=$string&field=0&operator=re\">magictraders.com</a></h3>\n<pre>";

# print magictraders prices
open(FILE, "</var/www/enyalios.net/data/prices") or die "couldnt open prices file\n";
print grep /\Q$string\E/i, <FILE>;
close FILE;

print "</pre><h3><a href=\"http://cardshark.com/Search.aspx?qu=$string\">cardshark.com</a></h3>\n<pre>";

# print cardshark prices
my $page = &get("http://cardshark.com/Search.aspx?qu=$string");
if($page =~ /CardShark\.com - Search for cards/) { # multiple results
    while($page =~ m!<a href="CardDetail\.aspx\?id=\d+&amp;game=Magic">(.*?)</a></font></td><td><font color="Black"><a href="/Buy/Buy\.aspx\?Game=Magic&amp;CardSet=.*?">(.*?)</a></font></td><td><font color="Black">.*?</font></td><td><font color="Black">.*?</font></td><td><font color="Black">(.*?)</font></td>!ig) {
        printf "%-30s %-30s %6s\n", $1, $2, $3?$3:"??";
    }
} else { # returned a single card page
    my ($name, $set) = ($page =~ m!<span id="[^"]*_lblCardName" class="heading">(.*?)</span>.*?<span id="[^"]*_lblCardSet">(.*?)</span>!s);
    my ($price) = ($page =~ m!<tr class="tableViewRow" valign="top">\s*<td>(?:<font color="Black">)?\$([\d.]+)(?:</font>)?</td>!);
    printf "%-30s %-30s %6s\n", $name, $set, $price?$price:"??";
}
print "</pre><br />\nSearch Again:<br />\n<form method=\"get\" name=\"prices\" action=\"$progname\"><input type=\"text\" name=\"query\" />\n";
print "</body></html>";
