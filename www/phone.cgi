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
    close INPUT;
    return $retval;
}

my %inc;
$inc{$_} = get_include($_) for(qw"app woot shirt newegg weather steam deals");

my $mobile = "m." if $ENV{HTTP_USER_AGENT} =~ /Galaxy Nexus|Nexus 7/i;
#my $mythtv = ($ENV{REMOTE_ADDR} eq "50.44.158.126")?"http://192.168.0.102/mythweb/":"http://mythtv.enyalios.net/";
#my $minecraft = ($ENV{REMOTE_ADDR} eq "50.44.158.126")?"http://192.168.0.101/":"http://minecraft.enyalios.net/";

my @links = ( 
    [ "Dilbert Comic",          "http://pipes.yahoo.com/pipes/pipe.run?_id=1f33f50b7e2a1162758e9061a16cca83&_render=rss" ],
    [ "Liryon Blog",            "http://liryon.net/" ],
    [ "xkcd",                   "http://${mobile}xkcd.com/" ],
    [ "Basic Instructions",     "http://www.basicinstructions.net/" ],
#    [ "Jamie Wakefield Blog",   "http://www.jamiewakefield.com/" ],
    [ "The Daily WTF",          "http://thedailywtf.com/" ],
    [ "Sheldon Comic",          "http://www.sheldoncomics.com/" ],
    [ "Drive Comic",            "http://www.drivecomic.com/" ],
    [ "Subnormality Comic",     "http://www.viruscomix.com/subnormality.html" ],
#    [ "Baneling BBQ",           "http://www.banelingbbq.com/" ],
#    [ "Darths and Droids",      "http://darthsanddroids.net/" ],
    [ "The Ferrett Blog",       "http://theferrett.livejournal.com/" ],
    [ "Geekologie",             "http://geekologie.com/" ],
    [ "FMyLife",                "http://www.fmylife.com/" ],
);

print <<EOF;
Content-Type: text/html

<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN" "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">
<html>
    <head>
        <title>Phone Links</title>
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
            input[type=text] { border: 0px solid #3181B4; 
                              border-radius: 8px; 
                              width: 295px; 
                              padding: 3px; }
        </style>
        <script language="JavaScript" type="text/javascript">
            <!-- 
            var xmlhttp = null;
            var selected = -2;
            var searchstring;
            function startup() {
                document.search.query.focus();
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
                    "<tr><td>g</td><td>google</td></tr>" +
                    "<tr><td>gm</td><td>google maps</td></tr>" +
                    "<tr><td>gi</td><td>google image</td></tr>" +
                    "<tr><td>w</td><td>wikipedia</td></tr>" +
                    "<tr><td>m</td><td>movies</td></tr>" +
                    "<tr><td>pl</td><td>perl modules</td></tr>" +
                    "<tr><td>n</td><td>netflix</td></tr>" +
                    "<tr><td>c</td><td>magic cards</td></tr>" +
                    "<tr><td>cg</td><td>magic cards on gatherer</td></tr>" +
                    "<tr><td>t</td><td>tv shows</td></tr>" +
                    "<tr><td>p</td><td>magic card prices</td></tr>" +
                    "<tr><td>bl</td><td>black lotus project</td></tr>" +
                    "<tr><td>s</td><td>starcraft units</td></tr>" +
                    "<tr><td>mc</td><td>minecraft wiki</td></tr>" +
                    "<tr><td>mt</td><td>movie times</td></tr>" +
                    "</table>Use no prefix to do an \\"I'm feeling " +
                    "lucky\\" search.</div>";
                document.getElementById("help").style.display = "block";
            }
            function go(q) {
                if(q.match(/^\$/)) { /* toggle_help(); */ }
                else if(q.match(/^g ?\$/i))  { window.location = "http://www.google.com/"; }
                else if(q.match(/^g /i))  { window.location = "http://www.google.com/search?q=" + q.replace(/^g /i, ""); }
                else if(q.match(/^gm ?\$/i)) { window.location = "http://maps.google.com/"; }
                else if(q.match(/^gm /i)) { window.location = "http://maps.google.com/maps?q=" + q.replace(/^gm /i, ""); }
                else if(q.match(/^gi /i)) { window.location = "http://www.google.com/search?tbm=isch&q=" + q.replace(/^gi /i, ""); }
                else if(q.match(/^w /i))  { window.location = "http://en.wikipedia.org/wiki/" + q.replace(/^w /i, ""); }
                else if(q.match(/^m /i))  { window.location = "http://www.imdb.com/find?q=" + q.replace(/^m /i, "").replace(/ /g, "+"); }
                else if(q.match(/^pl /i)) { window.location = "http://search.cpan.org/search?query=" + q.replace(/^pl /i, ""); }
                else if(q.match(/^n ?\$/i))  { window.location = "http://dvd.netflix.com/Queue"; }
                else if(q.match(/^n /i))  { window.location = "http://dvd.netflix.com/Search?v1=" + q.replace(/^n /i, ""); }
                else if(q.match(/^c ?\$/i))  { window.location = "http://magiccards.info/search.html"; }
                else if(q.match(/^c /i))  { window.location = "http://magiccards.info/query?q=l%3Aen+" + q.replace(/^c /i, ""); }
                else if(q.match(/^bl /i)) { window.location = "http://blacklotusproject.com/cards/?q=" + q.replace(/^bl /i, ""); }
                else if(q.match(/^cg /i)) { window.location = "http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[\\"" + q.replace(/^cg /i, "") + "\\"]"; }
                else if(q.match(/^t /i))  { window.location = "http://thetvdb.com/index.php?language=7&order=translation&searching=Search&tab=advancedsearch&seriesname=" + q.replace(/^t /i, ""); }
                else if(q.match(/^p /i))  { window.location = "/cgi-bin/price.cgi?query=" + q.replace(/^p /i, ""); }
                else if(q.match(/^s /i))  { window.location = "http://starcraft.wikia.com/wiki/index.php?search=" + q.replace(/^s /i, ""); }
                else if(q.match(/^mc /i)) { window.location = "http://www.minecraftwiki.net/wiki/" + q.replace(/^mc /i, ""); }
                else if(q.match(/^mt /i)) { window.location = "http://www.google.com/movies?q=" + q.replace(/^mt /i, ""); }
                else if(q.match(/^mt ?\$/i))  { window.location = "http://www.google.com/movies?q=movies"; }
                else { window.location = "http://www.google.com/search?q=" + q + "&btnI=I'm+Feeling+Lucky"; }
                return false;
            }
            function hint(x) {
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
EOF
print " " x 16, "window.open('", $_->[1], "');\n" for @links;
print <<EOF;
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
        Smart Search <a style="font-size:8pt" href="javascript:toggle_help()">(?)</a><br/>
        <form method="get" name="search" action="/cgi-bin/redirect.cgi" onsubmit="return go(this.query.value)">
            <input type="text" name="query" onkeyup="handlekeys(event)" onkeypress="return tabselect(event)" autocomplete="off" />
        </form>
        <div id="help"></div><br/>
        Random Useful Links<br/>
        <table>
            <tr><td class="icon"><a href="https://mail.google.com/mail" accesskey="1"><img src="/img/gmail.png"><br/>Email</a></td>
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
$inc{app}
$inc{woot}
$inc{shirt}
$inc{newegg}
$inc{steam}
$inc{deals}
</table>
<br />
Daily Links
<a style="font-size:8pt" href="javascript:openall()">(open all)</a><br/>
EOF
print "<a href=\"", $_->[1], "\">", $_->[0], "</a><br/>\n" for @links;
print "<br/>\n</body>\n</html>\n";

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
<a href="http://onlythingconstantischange.wordpress.com/">Serena's Blog</a><br/>
<a href="http://uiucnopants.com/">UIUC No Pants</a><br/>
=cut
