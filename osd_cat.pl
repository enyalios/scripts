#!/usr/bin/perl

use strict;
use warnings;
use Getopt::Long;
use Gtk3 '-init';
use Encode;

my $font = "Sans";
my $font_size = 20;
my $color = "#3095a7";
my $position = "top";
my $offset = 20;
my $align = "left";
my $indent = 20;
my $outline = 1;
my $ocolor = "#000000";
my $delay = 5;
my $max_lines = 5;
my $screen_width = 0;
my $screen_height = 0;
(my $progname = $0) =~ s/.*\///;
my @lines;
my $timer;

sub parse_args {
    Getopt::Long::Configure qw(bundling pass_through);
    GetOptions(
        'pos|p=s'          => \$position,
        'offset|o=i'       => \$offset,
        'align|A=s'        => \$align,
        'indent|i=i'       => \$indent,
        'font|f=s'         => \$font,
        'size|z=i'         => \$font_size,
        'color|c=s'        => \$color,
        'delay|d=i'        => \$delay,
        'lines|l=i'        => \$max_lines,
        'outline|O=i'      => \$outline,
        'outlinecolor|u=s' => \$ocolor,
        'help|h'           => sub { print_help() }, 
    );
    $color = Gtk3::Gdk::RGBA::parse($color);
    $ocolor = Gtk3::Gdk::RGBA::parse($ocolor);
}

sub print_help {
    print <<EOF;
$progname [OPTION] [FILE]...
Display FILE, or standard input, on top of display.

  -p --pos (top|middle|bottom)    vertical position
  -o --offset <offset>            vertical offset
  -A --align (left|center|right)  horizontal position 
  -i --indent <offset>            horizontal offset
  -f --font <font>                font to use
  -z --size <size>                font size
  -c --color <color>              font color
  -d --delay <delay>              duration to display for
  -l --lines <lines>              max lines to display
  -O --outline <outline>          outline thickness
  -u --outlinecolor <color>       outline color
  -h --help                       this help message

EOF
exit;
}

sub trans_setup {
    my $window = shift;
    $window->set_app_paintable(1);
    my $screen = $window->get_screen();
    my $visual = $screen->get_rgba_visual();
    $window->set_visual($visual);
}

sub window_setup {
    my $window = shift;
    $window->realize; # crucial to set override redirect
    # this is how to call gdk functions
    # tell the window manager to not manage this window
    $window->get_window->set_override_redirect(Glib::TRUE);
    # pass thru clicks to windows below
    $window->get_window->input_shape_combine_region(Cairo::Region->create(), 0, 0);
    my $screen = $window->get_screen();
    $screen_width = $screen->get_width();
    $screen_height = $screen->get_height();
    $window->set_default_size($screen_width, $screen_height);
    $window->move(0, 0);
}

sub do_drawing {
    my ($widget, $context, $ref_status) = @_;
    $context->set_source_rgba(0, 0, 0, 0);
    $context->paint;
    $context->select_font_face($font, "normal", "normal");
    $context->set_font_size($font_size);
    my $line_height = sprintf("%.0f", $context->text_extents("Gg")->{height}*1.25);
    my $line_num = 1;
    for(@lines) {
        $_ = Encode::decode('UTF-8', $_);
        my $x = $indent;
        my $width = $context->text_extents($_)->{x_advance};
        if($align eq "right" || $align eq "r") {
            $x = $screen_width - $width - $indent;
        } elsif($align eq "center" || $align eq "c") {
            $x = ($screen_width - $width)/2;
        }

        my $y = $offset;
        my $height = @lines*$line_height;
        if($position eq "bottom" || $position eq "b") {
            $y = $screen_height - $height - $offset;
        } elsif($position eq "middle" || $position eq "m") {
            $y = ($screen_height - $height)/2;
        }

        $context->move_to($x, $y+$line_height*$line_num);
        $context->text_path($_);
        $context->set_source_rgba($ocolor->red, $ocolor->green, $ocolor->blue, $ocolor->alpha);
        $context->set_line_width($outline*2);
        $context->stroke_preserve;
        $context->set_source_rgba($color->red, $color->green, $color->blue, $color->alpha);
        $context->fill();
        $line_num++;
    }
}

parse_args();

my $window = Gtk3::Window->new('toplevel');
trans_setup($window);
my $darea = Gtk3::DrawingArea->new;
$darea->signal_connect(draw => \&do_drawing);
$window->signal_connect(delete_event => sub { Gtk3->main_quit });
$timer = Glib::Timeout->add($delay * 1000, sub { Gtk3->main_quit });
$window->add($darea);

window_setup($window);

if(@ARGV) {
    require File::Slurper;
    push @lines, split '\n', File::Slurper::read_text($_) for @ARGV;
} else {
    require IO::Select;
    my $s = IO::Select->new();
    $s->add(\*STDIN);

    Glib::IO->add_watch(fileno(STDIN), 'in', sub {
            # reset the timeout
            Glib::Source->remove($timer);
            $timer = Glib::Timeout->add($delay * 1000, sub { Gtk3->main_quit });

            # read from STDIN until it would block
            my $buffer;
            while($s->can_read(0) && sysread(STDIN, $_, 1024)) {
                $buffer .= $_;
            }

            # add new lines to @lines, then truncate to $max_lines
            push @lines, split '\n', $buffer;
            @lines = @lines[-$max_lines .. -1] if @lines > $max_lines;

            # trigger the screen to redraw
            $darea->queue_draw();

            # return true to keep the watch active
            return 1;
        });
}

$window->show_all;
Gtk3->main;
