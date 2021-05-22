#!/bin/bash
minval=0    # the result of some (omitted) calculation
maxval=100  # ditto
gnuplot -persist <<-EOFMarker
set rmargin 10
set key font ",12"
set xtics font ",12"
set ytics font ",13"
set xlabel font ",13"
set ylabel font ",13"
#set key abov left
#set key Left abov
set key Left abov reverse

set term png
set output 'percentage_uc.png'
set grid
#set xdata time
#set timefmt "%m/%d/%y"
set xtics rotate by -45
#set logscale y
set xlabel "User category based on the range of total notes posted"
set ylabel "Percentage"
set boxwidth 2 relative
set style fill solid 0.8 border -1
#set xrange ["7/10/18":"2/25/19"]
set yrange [0:101]
#set xtics ("6/1/12","6/12/12")
set ytics 10
#set xtics ("July-2018" 1, "August-2018" 8, "October-2018" 33)
plot 'percentage_uc.txt' using 7: xtic(1) t "Percentage of sensitive/personal notes posted" with histogram lc 10, 'percentage_uc.txt' using 4: xtic(1) t "Percentage of users who posted at least 1 sensitive/personal note" with histogram lc 3




EOFMarker
