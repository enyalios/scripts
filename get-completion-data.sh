#!/bin/sh

# switch to the data directory
cd /var/www/enyalios.net/data

# get movie data
wget -qO - ftp://ftp.fu-berlin.de/pub/misc/movies/database/ratings.list.gz | gzip -cd | sed -ne '/^MOVIE RATINGS REPORT/,/^----------/p' | perl -ne '/^.{16}(.{8}).{8}(?!")(.*)/; print "$2\n" if $1 > 1000;' > movies.list

# get tv data
wget -qO - ftp://ftp.fu-berlin.de/pub/misc/movies/database/ratings.list.gz | gzip -cd | sed -ne '/^MOVIE RATINGS REPORT/,/^----------/p' | perl -ne 'print "$1\n" if /^.{32}"([^"]*)/;' | sort | uniq > tv.list

# get magic data
wget -qO - 'http://gatherer.wizards.com/Pages/Search/Default.aspx?output=spoiler&method=text&action=advanced&name=+![idspispopd]' | perl -ne 'if(/class="nameLink".*?>(.*?)</) { $_ = $1; s/\xC3\x86/AE/g; s/\xC3\xB6/o/g; s/\xC3\xA0/A/g; s/\xC3\xA2/a/g; s/\xC3\xA9/e/g; s/\xC3\xA0/a/g; s/\xC3\xA1/a/g; s/\xC3\xAD/i/g; s/\xC3\xB6/o/g; s/\xC3\xBA/u/g; s/\xC3\xBB/u/g; print "$_\n" }' > oracle

# get perl modules
wget -qO - http://www.cpan.org/modules/02packages.details.txt.gz | gzip -cd | sed -ne '/^$/,$p' | perl -pe 's/ .*//' > perl.list

# get wikipedia article data (this needs to be last since we cd to a diff directory)
cd wiki
wget -qO - http://download.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz \
| gzip -cd \
| perl -ne 's/_/ /g; $t = $_; s/(..).*\n/$1/; y/A-Z/a-z/; y/a-z0-9/_/c; s/^(.)$/$1_/; print "$_ $t";' \
| sort \
| perl -e '$last = ""; while(<>) { /^(..) (.*)/; ($p, $t) = ($1, $2); if($p ne $last) { close FILE; open FILE, ">$p"; $last = $p; } print FILE "$t\n"; }'
