#!/bin/sh

# switch to the data directory
cd /var/www/enyalios.net/data

# get tv and movie data
./get-imdb-data.pl

# get movie data
#wget -qO - ftp://ftp.fu-berlin.de/pub/misc/movies/database/temporaryaccess/ratings.list.gz | gzip -cd | sed -ne '/^MOVIE RATINGS REPORT/,/^----------/p' | perl -ne 'if(/^.{16}(.{8}).{8}(?!")(.*)/) { print "$2\n" if $1 > 1000 }' > movies.list

# get tv data
#wget -qO - ftp://ftp.fu-berlin.de/pub/misc/movies/database/temporaryaccess/ratings.list.gz | gzip -cd | sed -ne '/^MOVIE RATINGS REPORT/,/^----------/p' | perl -ne 'print "$1\n" if /^.{32}"([^"]*)/;' | sort | uniq > tv.list

# get magic data
#wget -qO - 'http://gatherer.wizards.com/Pages/Search/Default.aspx?output=spoiler&method=text&action=advanced&name=+![idspispopd]' | perl -ne 'if(/class="nameLink".*?>(.*?)</) { $_ = $1; s/\xC3\x86/AE/g; s/\xC3\xB6/o/g; s/\xC3\xA0/A/g; s/\xC3\xA2/a/g; s/\xC3\xA9/e/g; s/\xC3\xA0/a/g; s/\xC3\xA1/a/g; s/\xC3\xAD/i/g; s/\xC3\xB6/o/g; s/\xC3\xBA/u/g; s/\xC3\xBB/u/g; print "$_\n" }' > oracle
#wget -qO - 'http://gatherer.wizards.com/Pages/Search/Default.aspx?action=advanced&output=checklist&name=+![idspispopd]' | perl -ne 'if(/<a class="nameLink".*?>(.*?)</) { $_ = $1; s/\xC3\x86/AE/g; s/\xC3\xB6/o/g; s/\xC3\xA0/A/g; s/\xC3\xA2/a/g; s/\xC3\xA9/e/g; s/\xC3\xA0/a/g; s/\xC3\xA1/a/g; s/\xC3\xAD/i/g; s/\xC3\xB6/o/g; s/\xC3\xBA/u/g; s/\xC3\xBB/u/g; print "$_\n" }' > oracle
URL=$(wget -qO- 'http://www.yawgatog.com/resources/oracle/' | perl -ne 'print "http://www.yawgatog.com/resources/oracle/$1\n" if /<a href="([^"]*?)">All Sets<\/a>/')
wget -qO- "$URL" | funzip | perl -pe 'BEGIN { $/ = "\n\n" } s/\n.*/\n/sm' > magic.list

# get perl modules
wget -qO - http://www.cpan.org/modules/02packages.details.txt.gz | gzip -cd | sed -ne '/^$/,$p' | perl -pe 's/ .*//' > perl.list

# get starcraft wiki pages
for PAGE in `GET http://starcraft.wikia.com/wiki/Special:AllPages | perl -ne 'for(/href="(\/wiki\/Special:AllPages.*?)"/g) { s/&amp;/&/g; print "http://starcraft.wikia.com$_\n" unless $seen{$_}++}'`; do
    sleep 1
    GET $PAGE | perl -ne 'next unless /<tr>/; for(/<a href="\/wiki\/[^"]+" title="(.*?)"/g) { print "$_\n" unless $_ eq "Special:AllPages" }'
done > starcraft.list

# get master of magic wiki pages
for PAGE in `GET http://masterofmagic.wikia.com/wiki/Special:AllPages | perl -ne 'for(/href="(\/wiki\/Special:AllPages.*?)"/g) { s/&amp;/&/g; print "http://masterofmagic.wikia.com$_\n" unless $seen{$_}++}'`; do
    sleep 1
    GET $PAGE | perl -ne 'next unless /<tr>/; for(/<a href="\/wiki\/[^"]+" title="(.*?)"/g) { print "$_\n" unless $_ eq "Special:AllPages" }'
done > masterofmagic.list

# get minecraft wiki pages
for PAGE in `GET http://www.minecraftwiki.net/wiki/Special:AllPages | perl -ne 'for(/href="(\/index\.php\?title=Special:AllPages.*?)"/g) { s/&amp;/&/g; print "http://www.minecraftwiki.net$_\n" unless $seen{$_}++}'`; do
    sleep 1
    GET $PAGE | perl -ne 'next unless /<tr>/; for(/<a href="\/wiki\/[^"]+" title="(.*?)"/g) { print "$_\n" unless $_ eq "Special:AllPages" }'
done > minecraft.list

# get hearthstone wiki pages
rm hearthstone.list
URL="http://hearthstone.gamepedia.com/Special:AllPages"
COUNT=0
while [[ "$URL" != "" ]]; do
    COUNT=$(($COUNT + 1))
    [[ "$COUNT" -gt "50" ]] && echo "page count exceeded" >&2 && break
    PAGE=$(wget -qO- "$URL")
    echo "$PAGE" | perl -ne 'next unless /^<li/; for(/<a href=.*? title="(.*?)"/g) { print "$_\n" unless $_ eq "Special:AllPages"; }' >> hearthstone.list
    URL=$(echo "$PAGE" | perl -ne 'if(/<a href="([^"]*?)"[^>]*?>Next page/) { $link = $1; $link =~ s/&amp;/&/g; print "http://hearthstone.gamepedia.com$link\n"; exit }')
    sleep 1
done

# get overwatch wiki pages
rm overwatch.list
URL="http://overwatch.gamepedia.com/Special:AllPages"
COUNT=0
while [[ "$URL" != "" ]]; do
    COUNT=$(($COUNT + 1))
    [[ "$COUNT" -gt "50" ]] && echo "page count exceeded" >&2 && break
    PAGE=$(wget -qO- "$URL")
    echo "$PAGE" | perl -ne 'next unless /^<li/; for(/<a href=.*? title="(.*?)"/g) { print "$_\n" unless $_ eq "Special:AllPages"; }' >> overwatch.list
    URL=$(echo "$PAGE" | perl -ne 'if(/<a href="([^"]*?)"[^>]*?>Next page/) { $link = $1; $link =~ s/&amp;/&/g; print "http://overwatch.gamepedia.com$link\n"; exit }')
    sleep 1
done

# get wikipedia article data (this needs to be last since we cd to a diff directory)
cd wiki
wget -qO - http://download.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz \
| gzip -cd \
| perl -ne 's/_/ /g; $t = $_; s/(..).*\n/$1/; y/A-Z/a-z/; y/a-z0-9/_/c; s/^(.)$/$1_/; print "$_ $t";' \
| sort \
| perl -e '$last = ""; while(<>) { /^(..) (.*)/; ($p, $t) = ($1, $2); if($p ne $last) { close FILE; open FILE, ">$p"; $last = $p; } print FILE "$t\n"; }'
