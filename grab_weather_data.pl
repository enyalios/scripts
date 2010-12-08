#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;
use XML::Simple;
use LWP::Simple;

my $zip = 61801;
my %trans = ( 4  => "tstorm3.png",
              7  => "sleet.png",
              10 => "sleet.png",
              11 => "light_rain.png",
              12 => "shower3.png",
              14 => "snow4.png",
              16 => "snow5.png",
              20 => "fog.png",
              21 => "mist.png",
              26 => "cloudy5.png",
              27 => "cloudy3_night.png",
              28 => "cloudy3.png",
              29 => "cloudy1_night.png",
              30 => "cloudy1.png",
              31 => "sunny_night.png",
              32 => "sunny.png",
              44 => "dunno.png" );

my $content = XMLin(&get("http://rss.weather.com/weather/rss/local/$zip"));
my $current = $content->{channel}->{item}->[0]->{description};
my $forecast = $content->{channel}->{item}->[-1]->{description};

$forecast =~ s/F\.----.*$//;
if($current =~ m|^.*?src=".*?wxicons/31/(\d+).gif\?\d*".*?>(.*?), and (-?\d+) &deg; F\. For more details.*$|)
{ $current = "<span style=\"width:60px\">
    <span style=\"position:relative;top:0px;left:20px\">
        <img src=\"/weather/$1.png\" title=\"$forecast\" width=\"48px\" height=\"48px\" />
    </span>
    <span id=\"temp\" style=\"position:relative;top:0px;left:-10px\">$3&deg;</span></span>
</span>
<br />$2" }

open OUTPUT, ">/var/www/enyalios.net/htdocs/weather/current.txt";
print OUTPUT "$current\n";
close OUTPUT;
