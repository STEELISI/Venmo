$fh = new IO::File($ARGV[0]);
while(<$fh>)
{
    $_ =~ s/January/01/;
    $_ =~ s/February/02/;
    $_ =~ s/March/03/;
    $_ =~ s/April/04/;
    $_ =~ s/May/05/;
    $_ =~ s/June/06/;
    $_ =~ s/July/07/;
    $_ =~ s/August/08/;
    $_ =~ s/September/09/;
    $_ =~ s/October/10/;
    $_ =~ s/November/11/;
    $_ =~ s/December/12/;
    print $_;
}
