#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set ylabel "angels" offset 0

set rmargin 20
set key font ",12"
set xtics font ",12"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
set key abov

set term png
set output 'percentage.png'
set grid
set xtics rotate by -45
set xlabel "Each month in the dataset"
set ylabel "Percentage of monthly public Venmo notes"
#set boxwidth 1.0 relative
boxwidth=2.0
set boxwidth 3.0 relative
#set boxwidth 3.0 absolute
set style fill solid 1.0 border -1
#set xrange ["7/10/18":"2/25/19"]
set yrange [0:35]
#set xtics ("6/1/12","6/12/12")
set ytics 10
#set autoscale

#plot 'sensitive_mon.txt' using 3:xtic(1) t "Percentage of sensitive/personal notes (Notes in English)" with boxes lc 2, 'sensitive_mon.txt' using 2:xtic(1) t "Percentage of sensitive/personal notes (Total Notes)" with boxes lc 7

#plot 'sensitive_mon.txt' using 3:xtic(1) t "Percentage of sensitive/personal notes (Notes in English)" with histogram lc 2, 'sensitive_mon.txt' using 2:xtic(1) t "Percentage of sensitive/personal notes (Total Notes)" with histogram lc 7


plot 'monthly.txt' using 3:xtic(1) t "Percentage of sensitive/personal notes (Notes in English)" with histogram lc 2, 'monthly.txt' using 2:xtic(1) t "Percentage of sensitive/personal notes (Total Notes)" with histogram lc 7
EOFMarker
