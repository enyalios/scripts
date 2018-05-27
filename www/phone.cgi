#!/usr/bin/perl
use strict;
use warnings;

sub get_include {
    open INPUT, "</var/www/enyalios.net/includes/".$_[0].".inc" or die "could not open include: $!";
    my $retval = join "", <INPUT>;
    $retval =~ s/\x{E2}\x{80}\x{9D}/"/g;
    $retval =~ s/\x{e2}\x{80}\x{99}/'/g;
    $retval =~ s/\x{E2}\x{80}\x{93}/-/g;
    $retval =~ s/\x{E2}\x{84}\x{A2}/(tm)/g;
    $retval =~ s/\x{E2}\x{80}\x{A6}/.../g;
    close INPUT;
    return $retval;
}

my %inc;
$inc{$_} = get_include($_) for(qw"woot shirt newegg weather steam deals");

my $mobile = ($ENV{HTTP_USER_AGENT} =~ /Galaxy Nexus|Nexus 7|\bMobile\b/i)?"m.":"";
#my $mythtv = ($ENV{REMOTE_ADDR} eq "50.44.158.126")?"http://192.168.0.102/mythweb/":"http://mythtv.enyalios.net/";
#my $minecraft = ($ENV{REMOTE_ADDR} eq "50.44.158.126")?"http://192.168.0.101/":"http://minecraft.enyalios.net/";

my @links = ( 
    [ "Dilbert Comic",          $mobile?"http://dilbert.com/fast":"http://pipes.yahoo.com/pipes/pipe.run?_id=1f33f50b7e2a1162758e9061a16cca83&_render=rss" ],
    [ "Liryon Blog",            "http://liryon.net/" ],
    [ "xkcd",                   "http://${mobile}xkcd.com/" ],
    [ "Basic Instructions",     "http://www.basicinstructions.net/" ],
#    [ "Jamie Wakefield Blog",   "http://www.jamiewakefield.com/" ],
#    [ "The Daily WTF",          "http://thedailywtf.com/" ],
    [ "Sheldon Comic",          "http://www.sheldoncomics.com/" ],
    [ "Drive Comic",            "http://www.drivecomic.com/" ],
    [ "Subnormality Comic",     "http://www.viruscomix.com/subnormality.html" ],
#    [ "Baneling BBQ",           "http://www.banelingbbq.com/" ],
#    [ "Darths and Droids",      "http://darthsanddroids.net/" ],
    [ "The Ferrett Blog",       "http://theferrett.livejournal.com/" ],
    [ "Geekologie",             "http://geekologie.com/" ],
    [ "FMyLife",                "http://www.fmylife.com/" ],
);

my $open_all_text = join "\n" . " "x16, map { sprintf("window.open('%s');", $_->[1]) } @links;

my @smart_searches = (
    {
        prefix => "a",
        label => "Amazon",
        url => "https://smile.amazon.com/s/?field-keywords=%s",
    },
    {
        prefix => "bl",
        label => "Magic Card Price Graphs",
        url => "/cgi-bin/mtgstocks.cgi?q=%s",
    },
    {
        prefix => "c",
        label => "Magic Cards",
        url => "http://magiccards.info/query?q=l%3Aen+%s",
        link => "http://magiccards.info/search.html",
    },
    {
        prefix => "cc",
        label => "Magic Quick Search",
        url => "http://magic.enyalios.net/?q=%s",
    },
    {
        prefix => "cg",
        label => "Gatherer",
        url => "http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[\\\"%s\\\"]",
    },
    {
        prefix => "g",
        label => "Google",
        url => "http://www.google.com/search?q=%s",
        link => "http://www.google.com/",
    },
    {
        prefix => "gi",
        label => "Google Images",
        url => "http://www.google.com/search?tbm=isch&q=%s",
    },
    {
        prefix => "gm",
        label => "Google Maps",
        url => "http://maps.google.com/maps?q=%s",
        link => "http://maps.google.com/",
    },
    {
        prefix => "h",
        label => "Hearthstone",
        url => "http://hearthstone.gamepedia.com/%s",
    },
    {
        prefix => "k",
        label => "Katello",
        url => "https://katello.security.internal.ncsa.edu/cgi-bin/search.cgi?q=%s",
        link => "https://katello.security.internal.ncsa.edu/cgi-bin/search.cgi",
    },
    {
        prefix => "m",
        label => "IMDB",
        url => "http://www.imdb.com/find?q=%s",
    },
    {
        prefix => "mc",
        label => "Minecraft",
        url => "http://www.minecraftwiki.net/wiki/%s",
    },
    {
        prefix => "mom",
        label => "Master of Magic",
        url => "http://masterofmagic.wikia.com/wiki/%s",
    },
    {
        prefix => "mt",
        label => "Movie Times",
        url => "https://www.google.com/search?q=%s",
        link => "https://www.google.com/search?q=movies",
    },
    {
        prefix => "n",
        label => "Netflix",
        url => "http://dvd.netflix.com/Search?v1=%s",
        link => "http://dvd.netflix.com/Queue",
    },
    {
        prefix => "o",
        label => "Overwatch",
        url => "http://overwatch.gamepedia.com/%s",
    },
    {
        prefix => "p",
        label => "Magic Prices",
        url => "http://sales.starcitygames.com/search.php?substring=%s",
    },
    {
        prefix => "pb",
        label => "The Pirate Bay",
        url => "https://thepiratebay.org/search/%s/0/99/0",
    },
    {
        prefix => "pl",
        label => "CPAN",
        url => "http://search.cpan.org/search?query=%s",
    },
    {
        prefix => "s",
        label => "Starcraft",
        url => "http://starcraft.wikia.com/wiki/Special:Search?search=%s",
    },
    {
        prefix => "t",
        label => "The TV DB",
        url => "http://thetvdb.com/index.php?fieldlocation=2&language=7&searching=Search&tab=advancedsearch&order=translation&seriesname=%s",
    },
    {
        prefix => "w",
        label => "Wikipedia",
        url => "http://en.wikipedia.org/w/index.php?search=%s",
    },
);

my $help_text = join "\n" . " "x20, map { sprintf "\"<tr><td>%s</td><td>%s</td></tr>\" +", $_->{prefix}, $_->{label} } @smart_searches;
my $button_text = join "\n" . " "x16, map { sprintf "else if(x.match(/^%s /i)) { document.getElementById(\"search-button\").innerHTML = \"%s\"; }", $_->{prefix}, $_->{label} } @smart_searches;
my @jump_parts = ();
for(@smart_searches) {
    my ($prefix, $url, $link) = ($_->{prefix}, $_->{url}, $_->{link});
    push(@jump_parts, sprintf "else if(q.match(/^%s ?\$/i)) { window.location = \"%s\"; }", $prefix, $link) if defined $link;
    $url =~ s/%s/" + q.replace(\/^$prefix \/i, "") + "/;
    push @jump_parts, sprintf "else if(q.match(/^%s /i)) { window.location = \"%s\"; }", $prefix, $url;
}
my $jump_string = join "\n" . " "x16, @jump_parts;
my $links_string = join "\n", map { sprintf "<a href=\"%s\">%s</a><br/>", $_->[1], $_->[0] } @links;

print <<EOF;
Content-Type: text/html

<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN" "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">
<html>
    <head>
        <title>Phone Links</title>
        <meta charset="UTF-8">
        <style>
            body            { background-color: #000000; 
                              color: #DEDEDE; 
                              font-family: verdana; }
            img             { border: 0; }
            td.icon         { text-align: center; 
                              vertical-align: bottom;
                              width: 100px; }
            a               { text-decoration: none; 
                              color: #3181B4; }
            #help           { display: none;
                              font-size: 8pt; 
                              width: 300px;
                              -moz-border-radius: 8px; 
                              -webkit-border-radius: 8px;
                              border-radius: 8px;
                              border: 1px solid #3181B4;
                              position: absolute;
                              background: rgba(0, 0, 0, 0.7);
                            }
            .help           { padding: 5px; }
            #temp           { background: rgba(0, 0, 0, 0.5); 
                              color: #3181b4;
                              -moz-border-radius: 8px; 
                              -webkit-border-radius: 8px;
                              border-radius: 8px;
                              border: 1px solid #3181B4;
                            }
            .shortcuts      { margin: 5px; }
            .hint           { color: #DEDEDE; 
                              width: 290px; 
                              padding-left: 5px;
                              padding-right: 5px; }
            .hint:hover     { background-color: #3181B4; }
            .selected       { background-color: #3181B4; }
            .included       { overflow: hidden;
                              max-width: 300px;
                              /*white-space: nowrap;*/ }
            .price          { text-align: right; }
            .discount       { font-size: 6pt; 
                              width: 20px; }
            input[type=text] { border: 1px solid #666; 
                              border-radius: 4px 0px 0px 4px;
                              width: 215px; 
                              background-color: #000;
                              color: #bbb;
                              -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
                                      box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075);
                              -webkit-transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
                                      transition: border-color ease-in-out 0.15s, box-shadow ease-in-out 0.15s;
                              padding: 3px; }
            input[type=text]:focus {
                              border-color: #66afe9;
                              outline: 0;
                              -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(102, 175, 233, 0.6);
                                      box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.075), 0 0 8px rgba(102, 175, 233, 0.6);
                              }
            .input-group-addon { border-top: 1px solid #666; 
                              border-right: 1px solid #666; 
                              border-bottom: 1px solid #666; 
                              border-radius: 0px 4px 4px 0px; 
                              background-color: #333;
                              font-size: 10pt;
                              padding: 2px 2px 3px 2px; }
        </style>
        <script language="JavaScript" type="text/javascript">
            <!-- 
            var xmlhttp = null;
            var selected = -2;
            var searchstring;
            function startup() {
                //document.search.query.focus();
            }
            function toggle_help() {
                if(document.getElementById("helptext")) { 
                    document.getElementById("help").innerHTML = "";
                    document.getElementById("help").style.display = "none";
                    return;
                }
                document.getElementById("help").innerHTML = 
                    "<div class=\\"help\\" id=\\"helptext\\">Prefix your search with the " +
                    "following strings to make magic happen.<br/>" +
                    "<table class=\\"shortcuts\\">" +
                    $help_text
                    "</table>Use no prefix to do an \\"I'm feeling " +
                    "lucky\\" search.</div>";
                document.getElementById("help").style.display = "block";
            }
            function go(q) {
                if(q.match(/^\$/)) { /* toggle_help(); */ }
                $jump_string
                else { window.location = "http://www.google.com/search?q=" + q + "&btnI=I'm+Feeling+Lucky"; }
                return false;
            }
            function hint(x) {
                if(x.match(/^\$/i)) { document.getElementById("search-button").innerHTML = "Search"; }
                $button_text

                if(x.match(/^cc/i))
                    window.location = "http://magic.enyalios.net/";

                if (x.length < 3)
                { 
                    document.getElementById("help").innerHTML="";
                    document.getElementById("help").style.display = "none"
                    return;
                }

                var url = "/cgi-bin/hints.cgi?query=" + x;
                if (window.XMLHttpRequest)
                { xmlhttp = new XMLHttpRequest(); }
                else // for older IE 5/6
                { xmlhttp = new ActiveXObject("Microsoft.XMLHTTP"); }

                xmlhttp.onreadystatechange = function() {
                    if(xmlhttp.readyState == 4) {
                        document.getElementById("help").innerHTML=xmlhttp.responseText;
                        if(document.getElementById("help").innerHTML != "") { 
                            document.getElementById("help").style.display = "block";
                        } else {
                            document.getElementById("help").style.display = "none";
                        }
                    }
                }
                xmlhttp.open("GET", url, true);
                xmlhttp.send(null);
            }
            function openall() {
                $open_all_text
            }
            function handlekeys(x) {
                var keynum = (window.event) ? event.keyCode : x.keyCode;
                
                if(keynum == 40) { // down arrow
                    var children = document.getElementById('help').childNodes;
                    if(selected >= 0 && selected < children.length) { children[selected].setAttribute("class", "hint"); }
                    selected += 2;
                    if(selected >= children.length - 1 || children[selected].childNodes[0] == undefined) { selected = -2; }
                    if(selected < 0) { 
                        document.search.query.value = searchstring;
                    } else {
                        children[selected].setAttribute("class", "hint selected");
                        document.search.query.value = children[selected].childNodes[0].innerHTML;
                    }
                    return false;
                } else if(keynum == 38) { // up arrow
                    var children = document.getElementById('help').childNodes;
                    if(selected >= 0 && selected < children.length) { children[selected].setAttribute("class", "hint"); }
                    selected -= 2;
                    if(selected < -2) { 
                        selected = children.length - 2;
                        if(children[children.length-2].childNodes[0] == undefined) { selected -= 2; } 
                    }
                    if(selected < 0) {
                        document.search.query.value = searchstring;
                    } else {
                        children[selected].setAttribute("class", "hint selected");
                        document.search.query.value = children[selected].childNodes[0].innerHTML;
                    }
                    return false;
                } else {
                    selected = -2;
                    searchstring = document.search.query.value;
                    hint(document.search.query.value);
                }
            }
            function tabselect(x) {
                var keynum = (window.event) ? event.keyCode : x.keyCode;
                if(keynum == 9) { // they hit tab
                    document.search.query.value = document.getElementById("help").childNodes[0].childNodes[0].innerHTML;
                    return false;
                }
            }
            window.onload = startup;

            //-->
        </script>

    </head>
    <body link="#3181B4" alink="#CC0000" vlink="#3181B4">
        <form method="get" name="search" action="/cgi-bin/redirect.cgi" onsubmit="return go(this.query.value)">
            <div class="input-group">
                <input type="text" name="query" onkeyup="handlekeys(event)" onkeypress="return tabselect(event)" autocomplete="off" placeholder="Smart Search" autofocus/><span class="input-group-addon" id="search-button">Search</span>
                <a style="font-size:8pt" href="javascript:toggle_help()">(?)</a><br/>
            </div>
        </form>
        <div id="help"></div><br/>
        Random Useful Links<br/>
        <table>
            <tr><td class="icon"><a href="/hearthstone/links.html" accesskey="1"><img src="/img/hearthstone.png"><br/>Hearthstone</a></td>
                <td class="icon"><a href="http://imgur.com/hot/time"><img src="/img/imgur.png"><br/>Imgur</a></td>
                <td class="icon">$inc{weather}</td></tr>
            <tr><td class="icon"><a href="http://www.wizards.com/magic/Magazine/Default.aspx"><img src="/img/magic_the_gathering.jpg"><br/>Daily MTG</a></td>
                <td class="icon"><a href="http://www.starcitygames.com/"><img src="/img/starcitygames.png"><br/>StarCity</a></td>
                <td class="icon"><a href="/life"><img src="/life/plus.png" width="48" height="48"><br/>Life Counter</a></td></tr>
            <tr><td class="icon"><a href="http://enyalios.net/diablo.html"><img src="/img/diablo3.png"><br/>Diablo 3</a></td>
                <td class="icon"><a href="http://minecraft.enyalios.net/"><img src="/img/minecraft.png"><br/>Minecraft</a></td>
                <td class="icon"><a href="http://day9.tv/archives/"><img src="/img/day9.png" width="48" height="48"><br/>Day9</a></td></tr>
        </table>
        <br/>
        <a href="pages.cgi">Currently Open Tabs</a>
        <br/>
        <br/>
<table>
$inc{woot}
$inc{shirt}
$inc{newegg}
$inc{steam}
$inc{deals}
</table>
<br />
Daily Links
<a style="font-size:8pt" href="javascript:openall()">(open all)</a><br/>
$links_string
<br/>
</body>
</html>
EOF

=cut
        <table><tr>
            <tr><td class="icon"><a href="http://www.woot.com/"><img src="/img/woot.png"><br>Woot!</a></td>
                <td class="icon"><a href="http://www.newegg.com/"><img src="/img/newegg.png"><br/>Newegg</a></td></tr>
                <td class="icon"><a href="http://www.google.com/movies?q=movies&loc=61820"><img src="/img/movie_times.png"><br/>Movies</a></td>
                <td class="icon"><a href="http://www.google.com" accesskey="2"><img src="/img/google.png"><br/>Google</a></td>
                <td class="icon"><a href="http://en.m.wikipedia.org/" accesskey="3"><img src="/img/wikipedia.png"><br/>Wikipedia</a></td>
                <td class="icon"><a href="http://xhtml.weather.com/xhtml/cc/61801" accesskey="4"><img src="/img/weather.png"><br/>Weather</a></td>
                <td class="icon"><a href="http://www.imdb.com/" accesskey="5"><img src="/img/imdb.png"><br/>IMDB</a></td>
                <td class="icon"><a href="http://magiccards.info/"><img src="/img/magic_cards_info.gif"><br/>MagicCards</a></td>
                <td class="icon"><a href="http://cardshark.com/"><img src="/img/cardshark.png"><br/>Card Shark</a></td>
                <td class="icon"><a href="http://magictraders.com/"><img src="/img/magictraders.png"><br/>MTGtraders</a></td>
        </tr></table>

        <td><a href="http://mobile.usablenet.com/mt/www.delta.com/home/index.jsp">Delta Airlines</a></td>
1. <a href="http://127.0.0.1/cgi-bin/email.pl" accesskey="1">Email</a/><br/>
6. <a href="http://192.168.0.102/mythweb/" accesskey="6">Mythweb</a><br/>
<a href="https://mail.google.com/mail">Gmail</a><br/>
<a href="http://www.accuweather.com/pda/pda_5dy.asp?act=L">AccuWeather</a><br/>
<a href="http://192.168.1.16/temp/dinner_ideas.html">Dinner Ideas</a><br/>
<a href="http://wap.arune.se/imdb/index.php">IMDB</a><br/>
<a href="http://m.facebook.com/login.php?http&next=http://m.facebook.com/home.php">Facebook</a><br/>
<a href="http://m.gmail.com/">Gmail</a><br/>
<a href="http://mobile.google.com">Google Mobile</a><br/>
<a href="http://mobile.fandango.com/">Fandango</a><br/>
<a href="http://palm.moviefone.com/">Moviefone</a><br/>
<a href="http://dilbert.com/blog/">Dilbert Blog</a><br/>
<a href="http://failblog.org/">Fail Blog</a><br/>
<a href="http://comics.com/pearls_before_swine/?PerPage=50">Pearls Before Swine Comic</a><br/>
<a href="http://www.aikida.net/">Aikida Comic</a><br/>
<a href="http://buttsmithy.com/archives/comic/p-463">Alfie Comic</a><br/>
<a href="http://oglaf.com/">Oglaf Comic</a><br/>
<a href="http://onlythingconstantischange.wordpress.com/">Serena's Blog</a><br/>
<a href="http://uiucnopants.com/">UIUC No Pants</a><br/>
=cut
