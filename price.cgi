#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
use LWP::Simple;

$| = 1;
my $progname = $0;
$progname =~ s!^.*/!!;

my $string = param('query');
exit if $string eq "";
my $mode = param('mode');

if($mode eq "cs") { # print cardshark prices
    print "Content-Type: text/html\n\n";
    print &get_card_shark($string);
} elsif($mode eq "ssg") { # print star city games prices
    print "Content-Type: text/html\n\n";
    print &get_star_city_games($string);
} else {
    my $magic_traders = &get_magic_traders($string);
    print <<EOF;
Content-Type: text/html

<html>
    <head>
        <script language="JavaScript" type="text/javascript">
            <!--
            function setfocus() {
                document.prices.query.focus();
            }
            function loadpart(x) {
                var url = "?query=$string&mode=" + x;
                var xmlhttp = new XMLHttpRequest();
                xmlhttp.open("GET", url, true);
                xmlhttp.send(null);
                xmlhttp.onreadystatechange = function() {
                    if(xmlhttp.readyState == 4) {
                        document.getElementById(x).innerHTML=xmlhttp.responseText;
                    }
                }
            }
            window.onload=function() {
                setfocus();
                loadpart("cs");
                loadpart("ssg");
            }
            //-->
        </script>
    </head>
    <body>
        <h2>searching for '$string'</h2>
        <h3><a href="http://classic.magictraders.com/cgi-bin/query.cgi?list=magic&amp;target=$string&amp;field=0&amp;operator=re">magictraders.com</a></h3>
        <pre>$magic_traders</pre>
        <h3><a href="http://cardshark.com/Search.aspx?qu=$string">cardshark.com</a></h3>
        <pre id="cs">Loading...</pre>
        <h3><a href="http://sales.starcitygames.com/spoiler/display.php?name=$string&amp;namematch=AND&amp;foil=nofoil&amp;for=no">starcitygames.com</a></h3>
        <pre id="ssg">Loading...</pre>
        <br />
        Search Again:<br />
        <form method="get" name="prices" action="$progname"><input type="text" name="query" /></form>
    </body>
</html>
EOF
}

sub get_magic_traders {
    # get magictraders prices
    my $string = $_[0];
    open(FILE, "</var/www/enyalios.net/data/prices") or die "couldnt open prices file\n";
    my $retval = join "", grep /\Q$string\E/i, <FILE>;
    close FILE;
    return $retval;
}

sub get_card_shark {
    # get cardshark prices
    my $string = $_[0];
    my $retval;
    my $page = get("http://cardshark.com/Search.aspx?qu=$string");
    if($page =~ /CardShark\.com - Search for cards/) { # multiple results
        while($page =~ m!<a href="/Magic-the-Gathering/.*?">(.*?)</a></font></td><td><font color="Black"><a href="/Buy/Magic-the-Gathering/Find-Cards/.*?">(.*?)</a></font></td><td><font color="Black">.*?</font></td><td><font color="Black">.*?</font></td><td><font color="Black">(.*?)</font>!ig) {
            $retval .= sprintf "%-30s %-30s %6s\n", $1, $2, $3?$3:"??";
        }
    } else { # returned a single card page
        my ($name, $set) = ($page =~ m!<span id="[^"]*_lblCardName" class="heading">(.*?)</span>.*?<span id="[^"]*_lblCardSet">(.*?)</span>!s);
        my ($price) = ($page =~ m!<tr class="tableViewRow" valign="top">\s*<td>(?:<font color="Black">)?\$([\d.]+)(?:</font>)?</td>!);
        $retval = sprintf "%-30s %-30s %6s\n", $name, $set, $price?$price:"??";
    }
    return $retval;
}

sub get_star_city_games {
    # get starcitygames prices
    my $string = $_[0];
    my $retval;
    my $ssg_url = "http://sales.starcitygames.com/spoiler/display.php?name=$string&namematch=AND&foil=nofoil&for=no&display=4&numpage=100";
    my $page = LWP::Simple::get($ssg_url);
    my (%cards, $name, $set);
    my %code_to_digit;
    my %offset_to_digit = qw(
        0px    0
        7px    1
        14px   2
        21px   3
        28px   4
        35px   5
        42px   6
        49px   7
        56px   8
        63px   9
        66px   10
    );

    my $background = $1 if $page =~ /background-image:url\((.*?)\)/;
    $background = "http:" . $background unless $background =~ m!^http://!;
    my $digits = "";
    while(1) {
        $digits = &background_image_to_string($background);
        if($digits ne "") {
            last;
        } else {
            $page = LWP::Simple::get($ssg_url);
            $background = $1 if $page =~ /background-image:url\((.*?)\)/;
            $background = "http:" . $background unless $background =~ m!^http://!;
        }
    }

    # find the offset for each code and convert them to the correct digit
    while($page =~ /\.(......) {background-position:-?([\d.]+(pt|px|em))/g) {
        $code_to_digit{$1} = (exists $offset_to_digit{$2})?$offset_to_digit{$2}:"?";
    }

    for(split /<tr class="deckdbbody2?.*?">/, $page) {
        my ($price_line, $price, $count_line, $count, @cells);
        @cells = /<td class="deckdbbody2?.*?"(?: nowrap="nowrap")?>(.*?)<\/td>/sg;
        next unless @cells;
        if($cells[0] =~ /\n\s*(.*?)<\/a>/) {
            $name = $1;
            $set = $cells[1];
            $set =~ s/<.*?>//g;
            s/&amp;/&/g for $name, $set;
        }
        next if $name =~ /\(Not Tournament Legal\)/;
        next if $set =~ /Rarities & Misprints/;
        for($cells[8] =~ /<div class="(.*?)">/g) {
            for(split " ", $_) {
                s/2$//;
                $price .= substr $digits, $code_to_digit{$_}, 1 if defined $code_to_digit{$_};
            }
        }
        # handle prices how they are listed when there is a sale
        $price = $1 if $cells[8] =~ /^.*<span[^>]*>\$([\d.]+)<\/span>/;
        $count = 0 if $cells[7] eq "Out of Stock";
        for($cells[7] =~ /<div class="(.*?)">/g) {
            for(split " ", $_) {
                s/2$//;
                $count .= substr $digits, $code_to_digit{$_}, 1 if defined $code_to_digit{$_};
            }
        }
        $cards{$name}{$set}{count} += $count;
        $cards{$name}{$set}{min} = $price if(!defined $cards{$name}{$set}{min} || $price < $cards{$name}{$set}{min});
        $cards{$name}{$set}{max} = $price if(!defined $cards{$name}{$set}{max} || $price > $cards{$name}{$set}{max});
        #my $i = 0; print "  ", $i++, ": $_\n" for @cells;
    }

    for my $name(sort keys %cards) {
        for my $set(sort keys %{$cards{$name}}) {
            $retval .= sprintf "%-30s %-30s %6.2f  %3d\n",
            $name,
            $set,
            ($cards{$name}{$set}{min} + $cards{$name}{$set}{max}) / 2,
            $cards{$name}{$set}{count};
        }
    }
    return $retval;
}

sub background_image_to_string {
    my $background = $_[0];
    my @lines = `GET "$background" | pngtopnm | gocr -C 0-9.`;
    for(@lines){ tr/ //d; chomp; }
    my (@digits, %seen_digit);

    # make an array of digits in each row of the image
    my @digits1 = split "", $lines[0];
    my @digits2 = split "", $lines[1];

    # bail if one line is shorter than the other
    return "" unless @digits1 == @digits2;
    # or if they are both the wrong length
    return "" unless @digits1 == 11;

    # iterate thru the digits noting the ones that match
    my $max = (@digits1 > @digits2)?@digits1:@digits2;
    for(0..$max-1) {
        if($digits1[$_] eq $digits2[$_] && $digits1[$_] ne "_") {
            $digits[$_] = $digits1[$_];
            $seen_digit{$digits1[$_]} = 1;
        } else {
            $digits[$_] = "_";
        }
    }

    # when one is unset pick the other if we havent used that digit anywhere else
    for(0..$max-1) {
        if($digits[$_] eq "_") {
            if($digits1[$_] eq "_" && $digits2[$_] ne "_" && !defined $seen_digit{$digits2[$_]}) {
                $digits[$_] = $digits2[$_];
                $seen_digit{$digits2[$_]} = 1;
            } elsif($digits2[$_] eq "_" && $digits1[$_] ne "_" && !defined $seen_digit{$digits1[$_]}) {
                $digits[$_] = $digits1[$_];
                $seen_digit{$digits1[$_]} = 1;
            } elsif($digits1[$_] ne "_" && $digits2[$_] ne "_" && $seen_digit{$digits1[$_]} && !defined $seen_digit{$digits2[$_]}) {
                $digits[$_] = $digits2[$_];
                $seen_digit{$digits2[$_]} = 1;
            } elsif($digits2[$_] ne "_" && $digits1[$_] ne "_" && $seen_digit{$digits2[$_]} && !defined $seen_digit{$digits1[$_]}) {
                $digits[$_] = $digits1[$_];
                $seen_digit{$digits1[$_]} = 1;
            }
        }
    }

    # we have seen every digit but 1, fill it in
    if(keys %seen_digit == 10) {
        my $missing = "";
        for(0..9, ".") {
            $missing = $_ unless defined $seen_digit{$_};
        }
        for(0..$max-1) {
            if($digits[$_] eq "_") {
                $digits[$_] = $missing;
                $seen_digit{$missing} = 1;
            }
        }
    }
    # bail unless we've seen each digit once
    return "" unless keys %seen_digit == 11;
    return join "", @digits;
}
