#!/usr/bin/perl

use strict;
use warnings;
use CGI ':standard';
use DBI;
use UUID::Tiny ":std";

my $dbfile = "/var/www/pod.enyalios.net/db/pod.db";
my $key = param('key') || cookie('key');
my $email = param('email');
my $logout = param('logout');

if($logout) {
    # delete the cookie, do a redirect
    my $cookie = cookie(-name => "key", -value => "", -expires => "-1d");
    print header(-cookie => $cookie, -refresh => "0; url=/"),
    start_html(-title => "Podcast", -style => {-src => "style.css"}),
    "You have been logged out.  Click <a href=\"/\">here</a> to continue.",
    end_html;
} elsif(request_method eq "POST" && $email) {
    # set stuff in the db and send an email
    print header, start_html(-title => "Podcast", -style => {-src => "style.css"});
    my $dbh = DBI->connect("dbi:SQLite:dbname=$dbfile", "", "", { RaiseError => 1, AutoCommit => 1 }) or die;
    my @keys = @{$dbh->selectcol_arrayref("SELECT key FROM user WHERE email = ?", {}, $email)};
    if(@keys == 0) {
        # new email, create uuid
        $key = create_uuid_as_string(UUID_RANDOM);
        $dbh->do("INSERT INTO user VALUES (NULL, ?, ?)", {}, $email, $key);
        print "Your account has been created.  ";
    } else {
        # existing email, just mail their key
        $key = $keys[0];
    }
    &send_mail($email, $key);
    $email =~ s/.*@//;
    print "Please check your email to log in to your account.  These emails often get misclassified as spam, so be sure to check your spam folder.<br /><br />\n",
    "<a href=\"http://$email\">Click here to go to $email</a>\n",
    end_html;
} elsif(defined $key) {
    # set the cookie, do a redirect
    my $cookie = cookie(-name => "key", -value => $key, -expires => "+1y");
    print header(-cookie => $cookie, -refresh => "0; url=/"),
    start_html(-title => "Podcast", -style => {-src => "style.css"}),
    "You're logged in.  Click <a href=\"/\">here</a> to continue.",
    end_html;
} else {
    # make a form so they can log in
    print header,
    start_html(-title => "Podcast", -style => {-src => "style.css"}, -meta => {viewport => "width=device-width,initial-scale=1"}),
    "Please enter your email address to create an account.",
    start_form(-method => "POST", -action => ""),
    "Email Address: ", textfield("email"), br, submit,
    end_form, end_html;
}

sub send_mail {
    my ($email, $key) = @_;
    my $message =
    "From: podcast\@enyalios.net\n" .
    "To: $email\n" .
    "Subject: Podcast Account\n" .
    "\n" .
    "Your account has been created.  Please click the following link to log in:\n" .
    "\n" .
    "    http://pod.enyalios.net/login.cgi?key=$key\n";

    #print "<pre>$message</pre>\n";
    open(SENDMAIL, "|-", "/usr/sbin/sendmail -i -t") or die "Could not open sendmail\n";
    print SENDMAIL $message;
    close SENDMAIL;
}
