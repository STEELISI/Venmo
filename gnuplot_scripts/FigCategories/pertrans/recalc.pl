# Merge two files

$fh = new IO::File($ARGV[0]);
$sh = new IO::File($ARGV[1]);
%fline=();
%sline=();
while(<$fh>)
{
    @items = split /\s+/, $_;
    $_ =~ s/\n//;
    ($m, $y) = split /\-/, $items[0];
    $fline{$y}{$m} = $_;
}
while(<$sh>)
{
    @items = split /\s+/, $_;
    ($m, $y) = split /\-/, $items[0];
    $y += 2000;
    if (int($m) < 10)
    {
	$m = "0" . $m;
    }
    $items[2] =~ s/\n//;
    $sline{$y}{$m} = $items[2];
}
for $y (sort {$a <=> $b} keys %fline)
{
    for $m (sort {$a <=> $b} keys %{$fline{$y}})
    {
	print "$fline{$y}{$m} $sline{$y}{$m}\n";
    }
}
    
